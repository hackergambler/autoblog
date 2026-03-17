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
DARK_BLOGGER_BLOG_ID = os.getenv("DARK_BLOGGER_BLOG_ID")

STATE_FILE = BASE_DIR / "dark_state.json"
TOPICS_FILE = BASE_DIR / "dark_topics_2000.json"
TOKEN_FILE = BASE_DIR / "token.json"

MODEL_NAME = "llama-3.3-70b-versatile"
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 3

TOPIC_REPLENISH_THRESHOLD = 50
TOPIC_BATCH_SIZE = 200
MAX_TOPICS_PER_GENERATION = 500

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


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


def load_topics() -> List[str]:
    if not TOPICS_FILE.exists():
        raise FileNotFoundError(f"Topics file not found: {TOPICS_FILE}")

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
    if not DARK_BLOGGER_BLOG_ID:
        missing.append("DARK_BLOGGER_BLOG_ID")
    if not TOKEN_FILE.exists():
        missing.append("token.json")
    if not TOPICS_FILE.exists():
        missing.append(str(TOPICS_FILE))

    if missing:
        raise RuntimeError(f"Missing required configuration: {', '.join(missing)}")


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


def groq_client() -> Groq:
    return Groq(api_key=GROQ_API_KEY)


def generate_new_topics(existing_topics: List[str], batch_size: int = TOPIC_BATCH_SIZE) -> List[str]:
    batch_size = max(1, min(batch_size, MAX_TOPICS_PER_GENERATION))
    existing_sample = existing_topics[-150:] if len(existing_topics) > 150 else existing_topics

    prompt = f"""
Generate {batch_size} unique dark mystery / unexplained / conspiracy / true crime blog topic titles.

Requirements:
- Return ONLY valid JSON
- Format must be:
  {{
    "topics": [
      "topic 1",
      "topic 2"
    ]
  }}
- Each topic must be specific, compelling, and blog-worthy
- Avoid duplicates or near-duplicates
- Avoid repeating these existing topics:
{json.dumps(existing_sample, ensure_ascii=False, indent=2)}

Mix across:
- unsolved crimes
- disappearances
- paranormal cases
- historical mysteries
- UFO incidents
- secret experiments
- maritime mysteries
- abandoned places
- cryptids
- strange deaths
- occult incidents
- conspiracy theories
- lost expeditions
- unexplained transmissions
- cursed objects
- cursed places

Keep each topic as a short title or title with angle.
Do not include numbering.
Do not include commentary.
JSON only.
"""

    client = groq_client()

    response = retry(
        client.chat.completions.create,
        messages=[{"role": "user", "content": prompt}],
        model=MODEL_NAME,
        temperature=1.0,
    )

    raw = response.choices[0].message.content.strip()
    if not raw:
        raise RuntimeError("Topic generation returned empty output.")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Topic generation returned invalid JSON: {e}\nRaw output:\n{raw[:1000]}")

    if not isinstance(data, dict) or "topics" not in data or not isinstance(data["topics"], list):
        raise RuntimeError("Topic generation JSON missing 'topics' list.")

    new_topics = dedupe_preserve_order([str(t) for t in data["topics"]])

    if not new_topics:
        raise RuntimeError("Topic generation produced no usable topics.")

    return new_topics


def ensure_topic_inventory(state: Dict[str, Any], topics: List[str]) -> List[str]:
    used = {normalize_topic(t).casefold() for t in state.get("used_topics", [])}
    unused = [t for t in topics if normalize_topic(t).casefold() not in used]

    logging.info("Topic inventory: total=%s unused=%s", len(topics), len(unused))

    if len(unused) >= TOPIC_REPLENISH_THRESHOLD:
        return topics

    logging.info(
        "Unused topics below threshold (%s). Generating %s new topics.",
        TOPIC_REPLENISH_THRESHOLD,
        TOPIC_BATCH_SIZE,
    )

    new_topics = generate_new_topics(topics, TOPIC_BATCH_SIZE)
    merged = dedupe_preserve_order(topics + new_topics)
    added_count = len(merged) - len(topics)

    if added_count == 0:
        raise RuntimeError("Generated topics were all duplicates; no new topics were added.")

    save_topics(merged)
    state["topic_refills"] = int(state.get("topic_refills", 0)) + 1
    save_state(state)

    logging.info("Added %s new topics. New total=%s", added_count, len(merged))
    return merged


def choose_topic(state: Dict[str, Any], topics: List[str]) -> str:
    used_topics = {normalize_topic(t).casefold() for t in state.get("used_topics", [])}
    last_topic = normalize_topic(state.get("last_topic")) if state.get("last_topic") else None

    available = [t for t in topics if normalize_topic(t).casefold() not in used_topics]

    if not available:
        logging.info("No available topics left. Forcing refill.")
        topics = ensure_topic_inventory(state, topics)
        used_topics = {normalize_topic(t).casefold() for t in state.get("used_topics", [])}
        available = [t for t in topics if normalize_topic(t).casefold() not in used_topics]

    if not available:
        logging.warning("Still no topics after refill. Resetting used_topics as fallback.")
        state["used_topics"] = []
        save_state(state)
        available = topics.copy()

    if last_topic and len(available) > 1:
        non_repeating = [t for t in available if normalize_topic(t) != last_topic]
        if non_repeating:
            available = non_repeating

    return random.choice(available)


def mark_topic_used(state: Dict[str, Any], topic: str) -> None:
    if topic not in state["used_topics"]:
        state["used_topics"].append(topic)

    state["last_topic"] = topic
    state["published_count"] = int(state.get("published_count", 0)) + 1
    state["last_run_at"] = datetime.datetime.utcnow().isoformat() + "Z"


def get_service():
    with TOKEN_FILE.open("r", encoding="utf-8") as f:
        info = json.load(f)

    creds = Credentials.from_authorized_user_info(info)
    return build("blogger", "v3", credentials=creds)


def generate_article(topic: str) -> str:
    client = groq_client()

    prompt = f"""
Act as an investigative journalist and mystery writer.

Write a 1200-1500 word deep-dive article about "{topic}".

Requirements:
- Return valid HTML only
- Use:
  <h2> for section headings
  <p> for paragraphs
  <blockquote> where appropriate
  <ul><li> for key theories or evidence
- Tone: suspenseful, intelligent, eerie, immersive
- Do not wrap output in <html> or <body>
- Do not include markdown
- End with a strong unresolved conclusion
"""

    response = retry(
        client.chat.completions.create,
        messages=[{"role": "user", "content": prompt}],
        model=MODEL_NAME,
        temperature=0.9,
    )

    content = response.choices[0].message.content.strip()

    if not content:
        raise RuntimeError("Groq returned empty article content.")

    return content


def get_styled_html(content: str, topic: str) -> str:
    curr_date = datetime.datetime.now().strftime("%B %d, %Y")

    return f"""
<div style="background:#0d0d0d;color:#d1d5db;font-family:'Courier New',monospace;padding:50px;max-width:800px;margin:auto;border:1px solid #333;">
    <div style="border:2px solid #ff3333;padding:25px;text-align:center;margin-bottom:40px;">
        <p style="color:#ff3333;margin:0;letter-spacing:3px;">TOP SECRET // CLASSIFIED RECORD</p>
        <h1 style="color:white;font-size:2.4rem;margin:15px 0;">CASE: {topic}</h1>
    </div>

    <div style="line-height:1.7;font-size:1.1rem;padding:0 10px;">
        {content}
    </div>

    <div style="border-top:1px dashed #ff3333;margin-top:70px;padding:30px;text-align:center;">
        <p style="color:#ff3333;font-size:1.3rem;margin:0;letter-spacing:2px;"><b>Published by MYRQ</b></p>
        <p style="margin:5px 0;color:#9ca3af;">{curr_date} • Unsolved Mysteries &amp; Conspiracies</p>
    </div>
</div>
"""


def publish_post(service, topic: str, html: str):
    body = {
        "title": f"Unsolved: {topic}",
        "content": html,
        "labels": ["Dark Mysteries", "Investigation"],
    }

    return retry(
        service.posts().insert(
            blogId=DARK_BLOGGER_BLOG_ID,
            body=body,
            isDraft=False
        ).execute
    )


def main():
    try:
        validate_config()

        state = load_state()
        topics = load_topics()
        topics = ensure_topic_inventory(state, topics)

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
        print(f"👻 Case File Published: {topic}")

    except HttpError as e:
        logging.exception("Blogger API error: %s", e)
        sys.exit(1)
    except Exception as e:
        logging.exception("Script failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
