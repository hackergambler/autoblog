import os
import sys
import json
import time
import random
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Any, Set

from groq import Groq
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

BASE_DIR = Path(__file__).resolve().parent

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CIV_BLOGGER_BLOG_ID = os.getenv("CIV_BLOGGER_BLOG_ID")

TOPICS_FILE = BASE_DIR / "civ_topics.json"
STATE_FILE = BASE_DIR / "civ_history.json"
TOKEN_FILE = BASE_DIR / "token.json"

MODEL_NAME = "llama-3.3-70b-versatile"
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 3

TOPIC_REPLENISH_THRESHOLD = 30
TOPIC_BATCH_SIZE = 30
MAX_TOPICS_PER_GENERATION = 50
TOPIC_GENERATION_ATTEMPTS = 5

DEFAULT_TOPICS = [
    "The Fall of the Aztec Empire",
    "The Library of Ashurbanipal",
    "Samurai Warfare Tactics",
    "The Industrial Revolution's Dark Side",
    "The Rise and Fall of Carthage",
    "The Engineering Genius of Ancient Rome",
    "The Bronze Age Collapse",
    "Daily Life in the Indus Valley Civilization",
    "The Mongol Empire's Military System",
    "The Political World of the Italian Renaissance",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def retry(func, *args, **kwargs):
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            logging.warning("Attempt %s/%s failed: %s", attempt, MAX_RETRIES, e)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
    raise last_error


def normalize_topic(topic: str) -> str:
    return " ".join(str(topic).strip().split())


def dedupe_preserve_order(topics: List[str]) -> List[str]:
    seen: Set[str] = set()
    cleaned: List[str] = []

    for t in topics:
        n = normalize_topic(t)
        if not n:
            continue
        key = n.casefold()
        if key not in seen:
            seen.add(key)
            cleaned.append(n)

    return cleaned


def default_state() -> Dict[str, Any]:
    return {
        "used_topics": [],
        "last_topic": None,
        "published_count": 0,
        "last_run_at": None,
        "topic_refills": 0,
    }


def load_state() -> Dict[str, Any]:
    if not STATE_FILE.exists():
        return default_state()

    try:
        with STATE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            logging.warning("Invalid state file. Resetting.")
            return default_state()

        state = default_state()
        state.update(data)

        if not isinstance(state.get("used_topics"), list):
            state["used_topics"] = []

        return state

    except Exception as e:
        logging.warning("Could not read state file: %s. Resetting.", e)
        return default_state()


def save_state(state: Dict[str, Any]) -> None:
    temp_file = STATE_FILE.with_suffix(".tmp")
    with temp_file.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    temp_file.replace(STATE_FILE)


def create_default_topics_file() -> None:
    if TOPICS_FILE.exists():
        return
    save_topics(DEFAULT_TOPICS)


def load_topics() -> List[str]:
    create_default_topics_file()

    with TOPICS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "topics" in data:
        topics = data["topics"]
    elif isinstance(data, list):
        topics = data
    else:
        raise ValueError("Topics JSON must be a list or an object with a 'topics' key")

    topics = dedupe_preserve_order([str(t) for t in topics])

    if not topics:
        raise ValueError("Topics file is empty")

    return topics


def save_topics(topics: List[str]) -> None:
    topics = dedupe_preserve_order(topics)

    payload = {
        "topics": topics,
        "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "count": len(topics),
    }

    temp_file = TOPICS_FILE.with_suffix(".tmp")
    with temp_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    temp_file.replace(TOPICS_FILE)


def validate_config() -> None:
    missing = []

    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not CIV_BLOGGER_BLOG_ID:
        missing.append("CIV_BLOGGER_BLOG_ID")
    if not TOKEN_FILE.exists():
        missing.append("token.json")

    if missing:
        raise RuntimeError(f"Missing required configuration: {', '.join(missing)}")


def groq_client() -> Groq:
    return Groq(api_key=GROQ_API_KEY)


def extract_json_object(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]

    return text


def parse_topics_from_response(raw: str) -> List[str]:
    raw = raw.strip()
    candidate = extract_json_object(raw)

    try:
        data = json.loads(candidate)
        if isinstance(data, dict) and isinstance(data.get("topics"), list):
            return dedupe_preserve_order([str(t) for t in data["topics"]])
        if isinstance(data, list):
            return dedupe_preserve_order([str(t) for t in data])
    except json.JSONDecodeError:
        pass

    topics = []
    for line in raw.splitlines():
        line = line.strip().strip(",")
        if not line:
            continue

        if line[:2] in ("- ", "* "):
            line = line[2:].strip()

        if "." in line[:4]:
            parts = line.split(".", 1)
            if parts[0].isdigit():
                line = parts[1].strip()

        line = line.strip().strip('"').strip("'").strip()

        if line in {"{", "}", "[", "]"}:
            continue
        if line.startswith('"topics"') or line.startswith("'topics'"):
            continue
        if len(line) < 8:
            continue

        topics.append(line)

    return dedupe_preserve_order(topics)


def generate_new_topics(existing_topics: List[str], batch_size: int = TOPIC_BATCH_SIZE) -> List[str]:
    batch_size = max(5, min(batch_size, MAX_TOPICS_PER_GENERATION))
    existing_sample = existing_topics[-100:] if len(existing_topics) > 100 else existing_topics

    client = groq_client()
    last_error = None

    for attempt in range(1, TOPIC_GENERATION_ATTEMPTS + 1):
        prompt = f"""
Generate {batch_size} unique history / civilization / empire / archaeology / warfare / world-history blog topic titles.

Return ONLY valid JSON in exactly this format:
{{
  "topics": [
    "topic 1",
    "topic 2"
  ]
}}

Rules:
- exactly {batch_size} topics
- no markdown
- no code fences
- no explanation
- no numbering
- no duplicates
- each topic should be specific, historically interesting, and article-worthy
- avoid these existing topics:
{json.dumps(existing_sample, ensure_ascii=False)}

Mix across:
ancient civilizations, military history, empires, lost cities, archaeology,
historical trade, political systems, royal courts, revolutions,
religion in history, ancient science, medieval society, maritime history,
collapse of civilizations, famous historical turning points.
"""

        try:
            response = retry(
                client.chat.completions.create,
                messages=[{"role": "user", "content": prompt}],
                model=MODEL_NAME,
                temperature=1.0,
            )

            raw = response.choices[0].message.content.strip()
            if not raw:
                raise RuntimeError("Empty topic generation response.")

            topics = parse_topics_from_response(raw)

            existing_keys = {normalize_topic(t).casefold() for t in existing_topics}
            fresh_topics = [
                t for t in topics
                if normalize_topic(t).casefold() not in existing_keys
            ]

            if len(fresh_topics) >= max(5, batch_size // 2):
                return fresh_topics

            raise RuntimeError(
                f"Too few usable topics returned on attempt {attempt}: got {len(fresh_topics)}"
            )

        except Exception as e:
            last_error = e
            logging.warning(
                "Topic generation attempt %s/%s failed: %s",
                attempt,
                TOPIC_GENERATION_ATTEMPTS,
                e,
            )
            time.sleep(2)

    raise RuntimeError(f"Topic generation failed after retries: {last_error}")


def ensure_topic_inventory(state: Dict[str, Any], topics: List[str]) -> List[str]:
    used = {normalize_topic(t).casefold() for t in state.get("used_topics", [])}
    unused = [t for t in topics if normalize_topic(t).casefold() not in used]

    logging.info("Topic inventory: total=%s unused=%s", len(topics), len(unused))

    if len(unused) >= TOPIC_REPLENISH_THRESHOLD:
        return topics

    logging.info(
        "Unused topics below threshold (%s). Generating more topics in small batches.",
        TOPIC_REPLENISH_THRESHOLD,
    )

    merged = topics[:]
    target_unused = TOPIC_REPLENISH_THRESHOLD + TOPIC_BATCH_SIZE

    for _ in range(5):
        used_now = {normalize_topic(t).casefold() for t in state.get("used_topics", [])}
        unused_now = [t for t in merged if normalize_topic(t).casefold() not in used_now]

        if len(unused_now) >= target_unused:
            break

        new_topics = generate_new_topics(merged, TOPIC_BATCH_SIZE)
        before = len(merged)
        merged = dedupe_preserve_order(merged + new_topics)
        added_count = len(merged) - before

        logging.info("Generated batch added %s new topics", added_count)

        if added_count == 0:
            logging.warning("No new topics added in this batch.")
            break

    if len(merged) == len(topics):
        raise RuntimeError("Could not replenish topics; no new unique topics were added.")

    save_topics(merged)
    state["topic_refills"] = int(state.get("topic_refills", 0)) + 1
    save_state(state)

    logging.info("Topic inventory updated: total=%s", len(merged))
    return merged


def choose_topic(state: Dict[str, Any], topics: List[str]) -> str:
    used_topics = {normalize_topic(t).casefold() for t in state.get("used_topics", [])}
    last_topic = normalize_topic(state.get("last_topic")) if state.get("last_topic") else None

    available = [t for t in topics if normalize_topic(t).casefold() not in used_topics]

    if not available:
        logging.info("No available topics left. Resetting used topics as fallback.")
        state["used_topics"] = []
        save_state(state)
        available = topics[:]

    if last_topic and len(available) > 1:
        non_repeating = [t for t in available if normalize_topic(t) != last_topic]
        if non_repeating:
            available = non_repeating

    return random.choice(available)


def mark_topic_used(state: Dict[str, Any], topic: str) -> None:
    topic = normalize_topic(topic)

    existing = {normalize_topic(t).casefold() for t in state["used_topics"]}
    if topic.casefold() not in existing:
        state["used_topics"].append(topic)

    state["last_topic"] = topic
    state["published_count"] = int(state.get("published_count", 0)) + 1
    state["last_run_at"] = datetime.datetime.utcnow().isoformat() + "Z"


def get_service():
    try:
        raw = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if not raw:
            raise RuntimeError("token.json exists but is empty.")

        info = json.loads(raw)

        if not isinstance(info, dict):
            raise RuntimeError("token.json must contain a JSON object.")

        creds = Credentials.from_authorized_user_info(info)
        return build("blogger", "v3", credentials=creds)

    except json.JSONDecodeError as e:
        raise RuntimeError(f"token.json is invalid JSON: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load Blogger credentials from token.json: {e}")


def generate_article(topic: str) -> str:
    client = groq_client()

    prompt = f"""
Act as a world historian and historical analyst.

Write a 1200-1500 word article about "{topic}".

Requirements:
- return valid HTML only
- use <h2>, <h3>, <p>, <ul>, <li> where useful
- tone: academic yet captivating
- no markdown
- no "as an AI"
- avoid vague filler
- include historical context, causes, significance, and long-term impact
- end with a concise reflective conclusion
"""

    response = retry(
        client.chat.completions.create,
        messages=[{"role": "user", "content": prompt}],
        model=MODEL_NAME,
        temperature=0.8,
    )

    content = response.choices[0].message.content.strip()
    if not content:
        raise RuntimeError("Groq returned empty article content.")

    return content


def get_styled_html(content: str, topic: str) -> str:
    curr_date = datetime.datetime.now().strftime("%B %d, %Y")
    return f"""
<div style="font-family: Georgia, serif; max-width: 800px; margin: auto; background: #fffcf9; padding: 45px; border: 1px solid #dcd1bd; color: #2d241e;">
    <div style="text-align: center; border-bottom: 2px solid #8d6e63; padding-bottom: 20px; margin-bottom: 40px;">
        <p style="letter-spacing: 5px; color: #8d6e63; font-weight: bold;">THE ANCIENT ARCHIVES</p>
        <h1 style="font-size: 3rem; margin: 10px 0; color: #3e2723;">{topic}</h1>
    </div>

    <div style="line-height: 2; font-size: 1.2rem;">
        {content}
    </div>

    <div style="border-top: 3px double #8d6e63; margin-top: 60px; padding: 30px; text-align: center;">
        <p style="font-size: 1.3rem; margin: 0; color: #3e2723;"><b>Published by MYRQ</b></p>
        <p style="margin: 5px 0; font-style: italic;">{curr_date} • Human History &amp; Lost Civilizations</p>
    </div>
</div>"""


def publish_post(service, topic: str, html: str):
    body = {
        "title": topic,
        "content": html,
        "labels": ["History", "Civilization"],
    }

    return retry(
        service.posts().insert(
            blogId=CIV_BLOGGER_BLOG_ID,
            body=body,
            isDraft=False,
        ).execute
    )


def main():
    try:
        validate_config()

        state = load_state()
        topics = load_topics()

        try:
            topics = ensure_topic_inventory(state, topics)
        except Exception as e:
            logging.warning("Topic refill failed, continuing with existing topics: %s", e)

        topic = choose_topic(state, topics)
        logging.info("Selected topic: %s", topic)

        article_html = generate_article(topic)
        final_html = get_styled_html(article_html, topic)

        service = get_service()
        result = publish_post(service, topic, final_html)

        mark_topic_used(state, topic)
        save_state(state)

        logging.info("Published successfully: %s", topic)
        logging.info("Post URL: %s", result.get("url", "N/A"))
        print(f"🏛️ History Published: {topic}")

    except HttpError as e:
        logging.exception("Blogger API error: %s", e)
        sys.exit(1)
    except Exception as e:
        logging.exception("Script failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
