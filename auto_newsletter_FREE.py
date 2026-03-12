"""
📧 AUTO NEWSLETTER WRITER - 100% FREE
=======================================
Automatically writes & sends beautiful newsletters twice a day
using FREE Groq AI + Mailchimp API

SETUP INSTRUCTIONS:
====================
STEP 1 - Create FREE Mailchimp account:
   1. Go to: https://mailchimp.com/
   2. Sign up free (no credit card)
   3. Complete account setup

STEP 2 - Get Mailchimp API Key:
   1. Login to Mailchimp
   2. Click your profile (top right) → Account & Billing
   3. Go to Extras → API Keys
   4. Click "Create A Key"
   5. Copy the key → paste below

STEP 3 - Get your Audience/List ID:
   1. In Mailchimp → Audience → All Contacts
   2. Click Settings → Audience name and defaults
   3. Copy the "Audience ID" shown there

STEP 4 - Get your Server Prefix:
   1. Look at your Mailchimp URL when logged in
   2. It shows something like: us21.admin.mailchimp.com
   3. The prefix is: us21 (just the usXX part)

STEP 5 - Install libraries:
   pip install groq mailchimp-marketing schedule

STEP 6 - Run:
   python auto_newsletter_FREE.py
"""

from groq import Groq
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
import schedule
import time
import random
import json
import os
import datetime
import sys

# ============================================================
# 🔧 YOUR SETTINGS - FILL THESE IN!
# ============================================================

GROQ_API_KEY        = "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"     # From https://console.groq.com
MAILCHIMP_API_KEY   = "a809ddd7023f1d2df0ba4fdeeebfe27b-us13" # From Mailchimp → Account → API Keys
MAILCHIMP_SERVER    = "us13"                                # e.g. us1, us21 — from your Mailchimp URL
MAILCHIMP_LIST_ID   = "64baf15ba1"       # From Mailchimp → Audience → Settings
FROM_NAME           = "Daily Tips World"                   # Your newsletter name
FROM_EMAIL          = "tibco.tibco.8@gmail.com"               # Must match your Mailchimp verified email

# ============================================================
# 📚 NEWSLETTER TOPICS - All categories, twice daily
# ============================================================

MORNING_TOPICS = {
    "Technology & AI": [
        "How AI is transforming jobs in 2026 — what you must know",
        "10 free AI tools that will supercharge your productivity today",
        "The future of work: humans + AI working together",
        "How to use AI to make money from home in 2026",
        "Cybersecurity threats in 2026 and how to protect yourself",
    ],
    "Money & Finance": [
        "5 money habits that will make you rich in 5 years",
        "How to invest your first ₹1000 — a beginner's guide",
        "Passive income ideas that actually work in 2026",
        "How to save ₹10,000 per month even on a small salary",
        "The truth about cryptocurrency — should you invest?",
    ],
    "Motivational & Life Tips": [
        "The morning routine that successful people swear by",
        "How to build unstoppable confidence in 30 days",
        "Why most people fail and how you can succeed",
        "The power of saying NO — how boundaries change your life",
        "How to turn your biggest failure into your greatest success",
    ],
    "Education & Self Improvement": [
        "The fastest way to learn any new skill in 2026",
        "Top 10 skills that will make you highly employable",
        "How to read 52 books a year — a simple system",
        "The science of memory — how to remember everything",
        "How to master English speaking in just 90 days",
    ],
}

EVENING_TOPICS = {
    "Health & Fitness": [
        "Why you can't sleep — and 7 science-backed fixes tonight",
        "The 10-minute evening workout that melts stress away",
        "Foods to eat at night for better sleep and recovery",
        "How to reduce anxiety naturally — no medication needed",
        "The evening habits of the healthiest people in the world",
    ],
    "Food & Cooking": [
        "5 quick dinner recipes ready in under 20 minutes",
        "The healthiest Indian dinner you can make tonight",
        "Why you should stop eating after 8pm — the science",
        "Best meal prep ideas for the entire week ahead",
        "The perfect bedtime snack that won't ruin your diet",
    ],
    "Travel & Adventure": [
        "Best weekend getaways from Hyderabad under ₹5000",
        "How to plan a dream vacation on a budget — step by step",
        "Hidden gems in India most tourists never discover",
        "The ultimate packing guide — never forget anything again",
        "Best places in the world to visit in 2026",
    ],
    "Motivational & Life Tips": [
        "How to end your day perfectly — an evening reflection routine",
        "The journaling habit that will change your life",
        "How to plan tomorrow tonight — the secret of productive people",
        "Why gratitude is the most powerful habit you can build",
        "How to let go of stress before bed — 5 proven techniques",
    ],
}

USED_TOPICS_FILE = "newsletter_used_topics.json"

# ============================================================
# 🧠 GROQ AI - Newsletter Writer
# ============================================================

def generate_newsletter(topic: str, edition: str) -> dict:
    """Uses FREE Groq AI to write a beautiful long-form newsletter"""

    client = Groq(api_key=GROQ_API_KEY)

    time_greeting = "Good Morning ☀️" if edition == "morning" else "Good Evening 🌙"
    time_context  = "start your day with energy and focus" if edition == "morning" else "wind down and reflect on your day"

    prompt = f"""Write a long, engaging newsletter edition about: "{topic}"

This is the {edition.upper()} edition. Help readers {time_context}.

Requirements:
- Start with: "{time_greeting} — [catchy opening line]"
- Length: 1000-1200 words
- Very conversational, warm, friendly tone — like writing to a friend
- Include a real story or example at the start to hook the reader
- 3-4 main sections with bold headers
- Each section has practical, actionable tips
- Include interesting facts or statistics
- End with a motivating "Today's Challenge" — one small action they can take today
- Add a fun "Quote of the Day" at the very end

Return ONLY a JSON object (no markdown, no extra text):
{{
  "subject": "catchy email subject line (under 60 chars, creates curiosity)",
  "preview_text": "preview text shown in inbox (under 100 chars)",
  "content_html": "full newsletter in beautiful HTML with inline styles",
  "topic_category": "category name"
}}

For content_html, use this structure with beautiful inline styling:
- Greeting section with colored background
- Story/hook section
- Main content sections with styled headers
- Today's Challenge box (colored background, stands out)
- Quote of the Day (italic, centered)
- Footer with unsubscribe note"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=3000
    )

    response_text = response.choices[0].message.content.strip()

    # Clean up JSON code fences
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    # Fix common JSON issues — remove control characters except \n \t
    import re
    # Replace literal newlines inside JSON string values with \n escape
    # Remove invalid control characters (ASCII 0-31 except \t \n \r)
    response_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', response_text)

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # If still failing — ask Groq to return simpler content
        print("   ⚠️  JSON parse failed, retrying with simpler prompt...")
        simple_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""Write a newsletter about "{topic}".
Return ONLY valid JSON with NO newlines inside string values. Use <br> for line breaks in HTML.
Format: {{"subject":"title","preview_text":"preview","content_html":"<p>content here</p>","topic_category":"category"}}"""
            }],
            temperature=0.5,
            max_tokens=3000
        )
        simple_text = simple_response.choices[0].message.content.strip()
        if "```json" in simple_text:
            simple_text = simple_text.split("```json")[1].split("```")[0].strip()
        elif "```" in simple_text:
            simple_text = simple_text.split("```")[1].split("```")[0].strip()
        simple_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', simple_text)
        return json.loads(simple_text)


# ============================================================
# 🎨 BEAUTIFUL HTML EMAIL WRAPPER
# ============================================================

def wrap_in_email_template(newsletter_data: dict, edition: str) -> str:
    """Wraps newsletter content in a beautiful HTML email template"""

    now       = datetime.datetime.now()
    date_str  = now.strftime("%A, %B %d, %Y")
    edition_label = "🌅 Morning Edition" if edition == "morning" else "🌙 Evening Edition"

    # Color theme based on edition
    if edition == "morning":
        header_bg  = "linear-gradient(135deg, #f97316, #fb923c)"
        accent     = "#f97316"
    else:
        header_bg  = "linear-gradient(135deg, #4f46e5, #7c3aed)"
        accent     = "#4f46e5"

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0; padding:0; background:#f3f4f6; font-family:'Segoe UI',Arial,sans-serif;">

  <div style="max-width:640px; margin:0 auto; background:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.1);">

    <!-- HEADER -->
    <div style="background:{header_bg}; padding:40px 32px; text-align:center;">
      <p style="color:rgba(255,255,255,0.85); font-size:13px; margin:0 0 8px; letter-spacing:2px; text-transform:uppercase;">{edition_label}</p>
      <h1 style="color:#ffffff; font-size:28px; font-weight:800; margin:0 0 8px;">{FROM_NAME}</h1>
      <p style="color:rgba(255,255,255,0.9); font-size:14px; margin:0;">{date_str}</p>
    </div>

    <!-- CONTENT -->
    <div style="padding:36px 32px; color:#374151; font-size:16px; line-height:1.8;">
      {newsletter_data.get('content_html', '')}
    </div>

    <!-- DIVIDER -->
    <div style="height:2px; background:linear-gradient(to right, transparent, {accent}, transparent); margin:0 32px;"></div>

    <!-- FOOTER -->
    <div style="padding:24px 32px; text-align:center; background:#f9fafb;">
      <p style="color:#9ca3af; font-size:13px; margin:0 0 8px;">
        You're receiving this because you subscribed to <strong>{FROM_NAME}</strong>
      </p>
      <p style="color:#9ca3af; font-size:12px; margin:0;">
        Sent with ❤️ from Hyderabad, India
      </p>
    </div>

  </div>

  <!-- SPACER -->
  <div style="height:32px;"></div>

</body>
</html>
"""


# ============================================================
# 📤 MAILCHIMP - Send Newsletter
# ============================================================

def send_newsletter_via_mailchimp(newsletter_data: dict, edition: str) -> str:
    """Creates and sends newsletter campaign via Mailchimp"""

    client = MailchimpMarketing.Client()
    client.set_config({
        "api_key": MAILCHIMP_API_KEY,
        "server":  MAILCHIMP_SERVER
    })

    html_content = wrap_in_email_template(newsletter_data, edition)

    # Step 1: Create campaign
    campaign = client.campaigns.create({
        "type": "regular",
        "recipients": {
            "list_id": MAILCHIMP_LIST_ID
        },
        "settings": {
            "subject_line": newsletter_data["subject"],
            "preview_text": newsletter_data.get("preview_text", ""),
            "title":        f"{edition.capitalize()} Newsletter - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "from_name":    FROM_NAME,
            "reply_to":     FROM_EMAIL,
        }
    })

    campaign_id = campaign["id"]
    print(f"   ✅ Campaign created: {campaign_id}")

    # Step 2: Set content
    client.campaigns.set_content(campaign_id, {
        "html": html_content
    })
    print(f"   ✅ Content set")

    # Step 3: Send immediately
    client.campaigns.send(campaign_id)
    print(f"   ✅ Newsletter sent!")

    return campaign_id


# ============================================================
# 🔄 TOPIC MANAGER
# ============================================================

def get_next_topic(edition: str) -> tuple:
    """Gets a fresh topic for this edition"""

    used_topics = []
    if os.path.exists(USED_TOPICS_FILE):
        with open(USED_TOPICS_FILE, "r") as f:
            used_topics = json.load(f)

    topics_pool = MORNING_TOPICS if edition == "morning" else EVENING_TOPICS

    category = random.choice(list(topics_pool.keys()))
    available = [t for t in topics_pool[category] if t not in used_topics]

    if not available:
        available = topics_pool[category]
        used_topics = [t for t in used_topics if t not in topics_pool[category]]

    topic = random.choice(available)

    used_topics.append(topic)
    if len(used_topics) > 100:
        used_topics = used_topics[-100:]

    with open(USED_TOPICS_FILE, "w") as f:
        json.dump(used_topics, f)

    return topic, category


# ============================================================
# 🚀 MAIN JOB
# ============================================================

def write_and_send_newsletter(edition: str = "morning"):
    """Main: picks topic → writes with Groq → sends via Mailchimp"""

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*55}")
    print(f"⏰  Running {edition.upper()} edition at: {now}")
    print(f"{'='*55}")

    try:
        # Step 1: Pick topic
        topic, category = get_next_topic(edition)
        print(f"📌 Topic    : {topic}")
        print(f"📂 Category : {category}")

        # Step 2: Write with Groq AI
        print("✍️  Writing newsletter with Groq AI...")
        newsletter_data = generate_newsletter(topic, edition)
        print(f"✅ Written  : {newsletter_data['subject']}")

        # Step 3: Send via Mailchimp
        print("📤 Sending via Mailchimp...")
        campaign_id = send_newsletter_via_mailchimp(newsletter_data, edition)

        # Save log
        log_entry = {
            "time":        now,
            "edition":     edition,
            "subject":     newsletter_data["subject"],
            "topic":       topic,
            "category":    category,
            "campaign_id": campaign_id
        }

        logs = []
        if os.path.exists("newsletter_log.json"):
            with open("newsletter_log.json", "r") as f:
                logs = json.load(f)
        logs.append(log_entry)
        with open("newsletter_log.json", "w") as f:
            json.dump(logs, f, indent=2)

        print(f"📊 Total newsletters sent: {len(logs)}")

    except ApiClientError as e:
        print(f"❌ Mailchimp Error: {e.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("⏳ Will retry next scheduled time...")


# ============================================================
# ▶️  START
# ============================================================

if __name__ == "__main__":
    print("=" * 55)
    print("📧  AUTO NEWSLETTER WRITER - FREE VERSION")
    print("    Powered by Groq AI + Mailchimp")
    print("=" * 55)

    # GitHub Actions mode — pass --morning or --evening
    if "--morning" in sys.argv:
        write_and_send_newsletter("morning")

    elif "--evening" in sys.argv:
        write_and_send_newsletter("evening")

    else:
        # Local mode — runs on schedule
        print("🌅  Morning newsletter: 8:00 AM daily")
        print("🌙  Evening newsletter: 7:00 PM daily")
        print("🛑  Press Ctrl+C to stop\n")

        # Run immediately for testing
        hour = datetime.datetime.now().hour
        edition = "morning" if hour < 12 else "evening"
        write_and_send_newsletter(edition)

        # Schedule twice daily
        schedule.every().day.at("08:00").do(write_and_send_newsletter, edition="morning")
        schedule.every().day.at("19:00").do(write_and_send_newsletter, edition="evening")

        while True:
            schedule.run_pending()
            time.sleep(60)
