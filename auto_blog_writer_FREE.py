import os
import sys
import json
import time
import random
import logging
import datetime
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple

from groq import Groq
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

BASE_DIR = Path(__file__).resolve().parent

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BLOGGER_BLOG_ID = os.getenv("BLOGGER_BLOG_ID")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
GOOGLE_TOKEN_URI = os.getenv("GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token")

TOPICS_FILE = BASE_DIR / "auto_topics.json"
STATE_FILE = BASE_DIR / "used_topics.json"
TOKEN_FILE = BASE_DIR / "token.json"  # local fallback only

MODEL_NAME = "llama-3.3-70b-versatile"
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 3

TOPIC_REPLENISH_THRESHOLD = 30
TOPIC_BATCH_SIZE = 30
MAX_TOPICS_PER_GENERATION = 50
TOPIC_GENERATION_ATTEMPTS = 5

BLOGGER_SCOPE = "https://www.googleapis.com/auth/blogger"

DEFAULT_TOPICS = {
    "Mindset": [
        "Neuroplasticity for Adults",
        "The Stoic Approach to Modern Stress",
        "Growth Mindset vs Fixed Mindset"
    ],
    "Finance": [
        "Dividend Growth Investing",
        "The 50/30/20 Budgeting Rule",
        "How to Negotiate Your Salary"
    ],
    "Health": [
        "Intermittent Fasting Protocols",
        "The Importance of Zone 2 Cardio",
        "High-Protein Meal Prep"
    ],
    "Tech": [
        "Building Private Cloud Storage",
        "The Ethics of Artificial Intelligence",
        "Mastering the Linux Command Line"
    ]
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def is_retryable_error(error: Exception) -> bool:
    if isinstance(error, RefreshError):
        return False

    if isinstance(error, HttpError):
        status = getattr(error.resp, "status", None)
        return status in {429, 500, 502, 503, 504}

    msg = str(error).lower()
    transient_markers = [
        "timeout",
        "timed out",
        "temporarily unavailable",
        "connection reset",
        "connection aborted",
        "remote end closed connection",
        "502",
        "503",
        "504",
        "rate limit",
        "too many requests",
    ]
    return any(marker in msg for marker in transient_markers)


def retry(func, *args, **kwargs):
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e

            if not is_retryable_error(e):
                raise

            logging.warning("Attempt %s/%s failed: %s", attempt, MAX_RETRIES, e)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)

    raise last_error


def normalize_text(value: str) -> str:
    return " ".join(str(value).strip().split())


def topic_key(category: str, topic: str) -> str:
    return f"{normalize_text(category)}|||{normalize_text(topic)}".casefold()


def dedupe_topic_items(items: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen: Set[str] = set()
    cleaned: List[Dict[str, str]] = []

    for item in items:
        category = normalize_text(item.get("category", "General"))
        topic = normalize_text(item.get("topic", ""))

        if not topic:
            continue

        key = topic_key(category, topic)
        if key not in seen:
            seen.add(key)
            cleaned.append({"category": category, "topic": topic})

    return cleaned


def default_state() -> Dict[str, Any]:
    return {
        "used_topics": [],
        "last_topic": None,
        "last_category": None,
        "published_count": 0,
        "last_run_at": None,
        "topic_refills": 0
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

    items = []
    for category, topics in DEFAULT_TOPICS.items():
        for topic in topics:
            items.append({"category": category, "topic": topic})

    save_topics(items)


def load_topics() -> List[Dict[str, str]]:
    create_default_topics_file()

    with TOPICS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "topics" in data:
        items = data["topics"]
    elif isinstance(data, list):
        items = data
    else:
        raise ValueError("Topics JSON must be a list or an object with a 'topics' key")

    if not isinstance(items, list):
        raise ValueError("Topics list is invalid")

    cleaned = dedupe_topic_items(items)
    if not cleaned:
        raise ValueError("Topics file is empty")

    return cleaned


def save_topics(items: List[Dict[str, str]]) -> None:
    items = dedupe_topic_items(items)

    payload = {
        "topics": items,
        "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "count": len(items)
    }

    temp_file = TOPICS_FILE.with_suffix(".tmp")
    with temp_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    temp_file.replace(TOPICS_FILE)


def has_env_google_auth() -> bool:
    return all([
        GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET,
        GOOGLE_REFRESH_TOKEN,
    ])


def validate_config() -> None:
    missing = []

    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not BLOGGER_BLOG_ID:
        missing.append("BLOGGER_BLOG_ID")

    if not has_env_google_auth() and not TOKEN_FILE.exists():
        missing.append(
            "Google auth: set GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET + GOOGLE_REFRESH_TOKEN "
            "or provide token.json"
        )

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


def parse_generated_topic_items(raw: str) -> List[Dict[str, str]]:
    raw = raw.strip()
    candidate = extract_json_object(raw)

    try:
        data = json.loads(candidate)

        if isinstance(data, dict) and isinstance(data.get("topics"), list):
            parsed = []
            for item in data["topics"]:
                if isinstance(item, dict):
                    parsed.append({
                        "category": str(item.get("category", "General")),
                        "topic": str(item.get("topic", "")).strip()
                    })
            return dedupe_topic_items(parsed)

    except json.JSONDecodeError:
        pass

    parsed = []
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
        if not line or len(line) < 8:
            continue

        if "|" in line:
            category, topic = line.split("|", 1)
            parsed.append({"category": category.strip(), "topic": topic.strip()})
        else:
            parsed.append({"category": "General", "topic": line})

    return dedupe_topic_items(parsed)


def generate_new_topics(existing_items: List[Dict[str, str]], batch_size: int = TOPIC_BATCH_SIZE) -> List[Dict[str, str]]:
    batch_size = max(5, min(batch_size, MAX_TOPICS_PER_GENERATION))
    sample = existing_items[-80:] if len(existing_items) > 80 else existing_items

    sample_text = [
        f'{item["category"]} | {item["topic"]}'
        for item in sample
    ]

    client = groq_client()
    last_error = None

    for attempt in range(1, TOPIC_GENERATION_ATTEMPTS + 1):
        prompt = f"""
Generate {batch_size} unique blog topic ideas for an expert advice / daily tips blog.

Return ONLY valid JSON in exactly this format:
{{
  "topics": [
    {{
      "category": "Mindset",
      "topic": "How to Build Emotional Resilience"
    }},
    {{
      "category": "Finance",
      "topic": "How to Automate Monthly Savings"
    }}
  ]
}}

Rules:
- exactly {batch_size} items
- categories should be practical and blog-friendly
- use categories like Mindset, Finance, Health, Tech, Productivity, Career, Habits, Learning
- no markdown
- no code fences
- no explanation
- no numbering
- no duplicates
- each topic should be specific and useful
- avoid these existing topics:
{json.dumps(sample_text, ensure_ascii=False)}
"""

        try:
            response = retry(
                client.chat.completions.create,
                messages=[{"role": "user", "content": prompt}],
                model=MODEL_NAME,
                temperature=1.0
            )

            raw = response.choices[0].message.content.strip()
            if not raw:
                raise RuntimeError("Empty topic generation response.")

            parsed = parse_generated_topic_items(raw)

            existing_keys = {
                topic_key(item["category"], item["topic"])
                for item in existing_items
            }

            fresh = [
                item for item in parsed
                if topic_key(item["category"], item["topic"]) not in existing_keys
            ]

            if len(fresh) >= max(5, batch_size // 2):
                return fresh

            raise RuntimeError(
                f"Too few usable topics returned on attempt {attempt}: got {len(fresh)}"
            )

        except Exception as e:
            last_error = e
            logging.warning(
                "Topic generation attempt %s/%s failed: %s",
                attempt,
                TOPIC_GENERATION_ATTEMPTS,
                e
            )
            time.sleep(2)

    raise RuntimeError(f"Topic generation failed after retries: {last_error}")


def ensure_topic_inventory(state: Dict[str, Any], items: List[Dict[str, str]]) -> List[Dict[str, str]]:
    used_keys = {str(x).casefold() for x in state.get("used_topics", [])}
    unused = [
        item for item in items
        if topic_key(item["category"], item["topic"]) not in used_keys
    ]

    logging.info("Topic inventory: total=%s unused=%s", len(items), len(unused))

    if len(unused) >= TOPIC_REPLENISH_THRESHOLD:
        return items

    logging.info(
        "Unused topics below threshold (%s). Generating more topics in small batches.",
        TOPIC_REPLENISH_THRESHOLD
    )

    merged = items[:]
    target_unused = TOPIC_REPLENISH_THRESHOLD + TOPIC_BATCH_SIZE

    for _ in range(5):
        used_now = {str(x).casefold() for x in state.get("used_topics", [])}
        unused_now = [
            item for item in merged
            if topic_key(item["category"], item["topic"]) not in used_now
        ]

        if len(unused_now) >= target_unused:
            break

        new_items = generate_new_topics(merged, TOPIC_BATCH_SIZE)
        before = len(merged)
        merged = dedupe_topic_items(merged + new_items)
        added_count = len(merged) - before

        logging.info("Generated batch added %s new topics", added_count)

        if added_count == 0:
            logging.warning("No new topics added in this batch.")
            break

    if len(merged) == len(items):
        raise RuntimeError("Could not replenish topics; no new unique topics were added.")

    save_topics(merged)
    state["topic_refills"] = int(state.get("topic_refills", 0)) + 1
    save_state(state)

    logging.info("Topic inventory updated: total=%s", len(merged))
    return merged


def choose_topic(state: Dict[str, Any], items: List[Dict[str, str]]) -> Tuple[str, str]:
    used_keys = {str(x).casefold() for x in state.get("used_topics", [])}
    last_key = None
    if state.get("last_category") and state.get("last_topic"):
        last_key = topic_key(state["last_category"], state["last_topic"])

    available = [
        item for item in items
        if topic_key(item["category"], item["topic"]) not in used_keys
    ]

    if not available:
        logging.info("No available topics left. Resetting used topics as fallback.")
        state["used_topics"] = []
        save_state(state)
        available = items[:]

    if last_key and len(available) > 1:
        non_repeating = [
            item for item in available
            if topic_key(item["category"], item["topic"]) != last_key
        ]
        if non_repeating:
            available = non_repeating

    selected = random.choice(available)
    return selected["category"], selected["topic"]


def mark_topic_used(state: Dict[str, Any], category: str, topic: str) -> None:
    key = topic_key(category, topic)

    if key not in {str(x).casefold() for x in state["used_topics"]}:
        state["used_topics"].append(key)

    state["last_category"] = normalize_text(category)
    state["last_topic"] = normalize_text(topic)
    state["published_count"] = int(state.get("published_count", 0)) + 1
    state["last_run_at"] = datetime.datetime.utcnow().isoformat() + "Z"


def load_google_credentials_from_env() -> Credentials:
    if not has_env_google_auth():
        raise RuntimeError(
            "Missing GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / GOOGLE_REFRESH_TOKEN"
        )

    return Credentials(
        token=None,
        refresh_token=GOOGLE_REFRESH_TOKEN,
        token_uri=GOOGLE_TOKEN_URI,
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=[BLOGGER_SCOPE],
    )


def load_google_credentials_from_file() -> Credentials:
    try:
        raw = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if not raw:
            raise RuntimeError("token.json exists but is empty.")

        info = json.loads(raw)

        if not isinstance(info, dict):
            raise RuntimeError("token.json must contain a JSON object.")

        creds = Credentials.from_authorized_user_info(info, scopes=[BLOGGER_SCOPE])

        if not creds.refresh_token:
            raise RuntimeError(
                "token.json does not contain a refresh_token. "
                "Regenerate OAuth token with offline access."
            )

        return creds

    except json.JSONDecodeError as e:
        raise RuntimeError(f"token.json is invalid JSON: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load Blogger credentials from token.json: {e}")


def get_google_credentials() -> Credentials:
    if has_env_google_auth():
        logging.info("Using Google credentials from environment variables.")
        return load_google_credentials_from_env()

    logging.info("Using Google credentials from token.json fallback.")
    return load_google_credentials_from_file()


def refresh_credentials(creds: Credentials) -> Credentials:
    try:
        creds.refresh(Request())
        return creds
    except RefreshError as e:
        raise RuntimeError(
            "Google OAuth refresh failed. Your refresh token is expired, revoked, "
            "or mismatched with the OAuth client. Regenerate GOOGLE_REFRESH_TOKEN."
        ) from e
    except Exception as e:
        raise RuntimeError(f"Failed to refresh Google credentials: {e}") from e


def get_service():
    creds = get_google_credentials()
    creds = refresh_credentials(creds)
    return build("blogger", "v3", credentials=creds, cache_discovery=False)


def clean_generated_html(content: str, topic: str) -> str:
    if not content:
        return content

    cleaned = content.strip()

    cleaned = re.sub(r"^```html\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    topic_pattern = re.escape(topic.strip())

    cleaned = re.sub(
        rf"^\s*<h1[^>]*>\s*{topic_pattern}\s*</h1>\s*",
        "",
        cleaned,
        flags=re.IGNORECASE | re.DOTALL
    )

    cleaned = re.sub(
        rf"^\s*<h2[^>]*>\s*{topic_pattern}\s*</h2>\s*",
        "",
        cleaned,
        flags=re.IGNORECASE | re.DOTALL
    )

    return cleaned.strip()


def generate_article(category: str, topic: str) -> str:
    client = groq_client()

    prompt = f"""
Write a 1200-1500 word expert guide on "{topic}" in the category "{category}".

Requirements:
- return valid HTML only
- do NOT include the article title as <h1> or <h2>
- start directly with useful content
- use <h2>, <h3>, <p>, <ul>, <li> where useful
- practical, clear, helpful, engaging tone
- no markdown
- no "as an AI"
- no generic intro about why the topic matters
- avoid vague filler
- end with a concise practical conclusion
"""

    response = retry(
        client.chat.completions.create,
        messages=[{"role": "user", "content": prompt}],
        model=MODEL_NAME,
        temperature=0.8
    )

    content = response.choices[0].message.content.strip()
    if not content:
        raise RuntimeError("Groq returned empty article content.")

    return clean_generated_html(content, topic)


def get_styled_html(content: str, category: str, topic: str) -> str:
    curr_date = datetime.datetime.now().strftime("%B %d, %Y")

    return f"""
<div style="font-family: Helvetica, Arial, sans-serif; max-width: 800px; margin: auto; color: #334; line-height: 1.8;">
    <div style="background: #1e293b; color: white; padding: 50px 30px; border-radius: 15px; text-align: center; margin-bottom: 30px;">
        <h1 style="margin: 0; font-size: 2.5rem;">{topic}</h1>
        <p style="text-transform: uppercase; letter-spacing: 2px; opacity: 0.8;">{category} • {curr_date}</p>
    </div>

    <div style="font-size: 1.1rem;">
        {content}
    </div>

    <div style="border-top: 2px solid #f1f5f9; margin-top: 60px; padding: 30px; text-align: center; color: #1e293b;">
        <p style="margin: 0; font-size: 1.2rem;"><b>Published by MYRQ</b></p>
        <p style="margin: 5px 0; color: #64748b;">{curr_date} • Expert Insights &amp; Daily Tips</p>
    </div>
</div>
""".strip()


def publish_post(service, category: str, topic: str, html_content: str):
    body = {
        "title": topic,
        "content": html_content,
        "labels": [category, "Expert Tips"]
    }

    return retry(
        service.posts().insert(
            blogId=BLOGGER_BLOG_ID,
            body=body,
            isDraft=False
        ).execute
    )


def run():
    try:
        validate_config()

        state = load_state()
        items = load_topics()

        try:
            items = ensure_topic_inventory(state, items)
        except Exception as e:
            logging.warning("Topic refill failed, continuing with existing topics: %s", e)

        category, topic = choose_topic(state, items)
        logging.info("Selected topic: [%s] %s", category, topic)

        article_html = generate_article(category, topic)
        html_content = get_styled_html(article_html, category, topic)

        service = get_service()
        result = publish_post(service, category, topic, html_content)

        mark_topic_used(state, category, topic)
        save_state(state)

        logging.info("Published successfully: %s", topic)
        logging.info("Post URL: %s", result.get("url", "N/A"))
        print(f"✅ Daily Tip Published: {topic}")

    except HttpError as e:
        logging.exception("Blogger API error: %s", e)
        sys.exit(1)
    except Exception as e:
        logging.exception("Script failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    run()
