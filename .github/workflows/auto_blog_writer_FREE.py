"""
🤖 AUTO BLOG WRITER - 100% FREE using Google Gemini AI
=======================================================
Automatically writes and publishes blog posts to Blogger.com every hour.
NO CREDIT CARD NEEDED - Uses Google's FREE Gemini API

SETUP INSTRUCTIONS (5 minutes only!):
=======================================
STEP 1 - Get FREE Gemini API Key:
   1. Go to: https://aistudio.google.com/app/apikey
   2. Sign in with your Google account
   3. Click "Create API Key"
   4. Copy the key and paste below where it says: GEMINI_API_KEY = "paste here"

STEP 2 - Get Blogger Blog ID:
   1. Go to: https://www.blogger.com
   2. Open your blog dashboard
   3. Look at the URL - it shows: blogger.com/blog/posts/XXXXXXXXXX
   4. That number is your Blog ID - paste it below

STEP 3 - Set up Blogger API (one time only):
   1. Go to: https://console.cloud.google.com
   2. Create a new project (name it anything)
   3. Search "Blogger API v3" → Enable it
   4. Go to Credentials → Create → OAuth 2.0 Client ID
   5. Application type: Desktop App
   6. Download JSON → rename to: credentials.json
   7. Put credentials.json in same folder as this script

STEP 4 - Install libraries:
   pip install google-generativeai google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client schedule

STEP 5 - Run it!:
   python auto_blog_writer_FREE.py
"""

from groq import Groq
import schedule
import time
import random
import json
import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ============================================================
# 🔧 YOUR SETTINGS - FILL THESE IN!
# ============================================================

GROQ_API_KEY    = "paste_your_groq_api_key_here"      # From https://console.groq.com
BLOGGER_BLOG_ID = "paste_your_blog_id_here"           # From your Blogger dashboard URL

# How often to post (in minutes) - default is 60 (every hour)
POST_EVERY_MINUTES = 60

# ============================================================
# 📚 BLOG TOPICS - All categories, rotates automatically
# ============================================================

ALL_TOPICS = {
    "Technology & AI": [
        "How AI is changing everyday life in 2026",
        "Top 10 free AI tools you should use today",
        "What is machine learning explained simply",
        "How to use AI tools for daily productivity",
        "Future of smartphones in the next 5 years",
        "Best free apps to learn coding in 2026",
        "How robots are being used in hospitals",
        "What is blockchain and why it matters",
        "Top cybersecurity tips for beginners",
        "How to protect your privacy online",
    ],
    "Health & Fitness": [
        "10 minute morning workout for beginners",
        "Best foods to eat for more energy all day",
        "How to sleep better every single night",
        "Simple tips to reduce stress naturally",
        "Benefits of drinking more water daily",
        "How to start running for the first time",
        "Best home exercises with no equipment needed",
        "Foods that boost your immune system fast",
        "How to build healthy habits that actually stick",
        "Mental health tips for very busy people",
    ],
    "Money & Finance": [
        "How to save money even on a small income",
        "Best ways to earn passive income online in 2026",
        "What is investing and how to start today",
        "How to get out of debt faster than you think",
        "Best free budgeting apps in 2026",
        "How to make money from home this year",
        "What is cryptocurrency explained for beginners",
        "How to negotiate a higher salary confidently",
        "10 tips to stop wasting money every month",
        "How to build an emergency fund fast",
    ],
    "Motivational & Life Tips": [
        "How to stay motivated every single day",
        "Morning routines of the most successful people",
        "How to overcome fear and finally take action",
        "Simple daily habits that will change your life",
        "How to set goals and actually achieve them",
        "Why reading books every day changes everything",
        "How to stop procrastinating once and for all",
        "Powerful lessons learned from failure",
        "How to build real self confidence step by step",
        "Why waking up early is a total game changer",
    ],
    "Food & Cooking": [
        "5 easy meals you can cook in just 15 minutes",
        "Best healthy breakfast ideas for busy mornings",
        "How to meal prep for the entire week easily",
        "Cheap and healthy dinner recipes for families",
        "Best Indian recipes anyone can make at home",
        "How to make the perfect cup of tea or coffee",
        "Easy desserts with only 3 simple ingredients",
        "Best foods to eat when you are feeling sick",
        "Amazing street foods from around the world",
        "Simple ways to reduce food waste at home",
    ],
    "Travel & Adventure": [
        "Best budget travel tips every traveler must know",
        "Top 10 most beautiful places in India to visit",
        "How to travel solo safely and confidently",
        "Best hidden gems to visit in South India",
        "How to plan an amazing trip on a tight budget",
        "Best time to visit Hyderabad as a tourist",
        "Complete travel packing checklist for any trip",
        "Best weekend getaways from Hyderabad city",
        "How to find cheap flights every single time",
        "Top things to do in Goa for first time visitors",
    ],
    "Education & Self Improvement": [
        "Best free online courses to learn new skills in 2026",
        "How to learn absolutely anything faster using science",
        "Top skills that will definitely get you hired in 2026",
        "How to improve your English speaking skills fast",
        "Best YouTube channels to learn anything for free",
        "How to study smarter and not just harder",
        "What to do if you failed your exams this year",
        "Best books every young person should read",
        "How to write a perfect resume in 2026",
        "Pro tips for acing any job interview",
    ],
}

USED_TOPICS_FILE = "used_topics.json"

# ============================================================
# 🧠 GEMINI AI - Blog Writer (FREE!)
# ============================================================

def generate_blog_post(topic: str, category: str) -> dict:
    """Uses FREE Groq AI to write a full blog post"""

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""Write a complete, engaging blog post about: "{topic}"
Category: {category}

Requirements:
- Write in simple, friendly English anyone can understand
- Length: 600-800 words
- Catchy introduction that grabs attention
- Use subheadings to organize content
- Include practical tips and real examples
- End with a motivating conclusion
- Make it SEO friendly with natural keywords

Return ONLY a JSON object with these exact fields (no extra text, no markdown):
{{
  "title": "your catchy blog title here",
  "content": "full blog content in HTML using <h2>, <p>, <ul>, <li> tags",
  "meta_description": "SEO description under 155 characters",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )

    response_text = response.choices[0].message.content.strip()

    # Clean up if model adds markdown code fences
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    blog_data = json.loads(response_text)
    blog_data["category"] = category
    blog_data["topic"] = topic
    return blog_data

# ============================================================
# 📝 BLOGGER API - Publisher
# ============================================================

SCOPES = ["https://www.googleapis.com/auth/blogger"]

def get_blogger_service():
    """Authenticate and return Blogger API service"""
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("blogger", "v3", credentials=creds)


def publish_to_blogger(blog_data: dict) -> str:
    """Publishes the blog post to Blogger.com"""

    service = get_blogger_service()

    full_content = f"""
<div style="font-family: Georgia, serif; max-width: 800px; margin: 0 auto; line-height: 1.8; color: #333;">
    <p style="background:#f0f7ff; padding:15px; border-left:4px solid #4a90e2; border-radius:4px;">
        <em>Category: {blog_data['category']} | Published by Auto Blog Writer</em>
    </p>
    {blog_data['content']}
    <hr style="margin:30px 0; border:none; border-top:1px solid #eee;"/>
    <p style="color:#888; font-size:0.9em; text-align:center;">
        Published on {datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")}
    </p>
</div>
"""

    post = {
        "title": blog_data["title"],
        "content": full_content,
        "labels": blog_data.get("tags", []) + [blog_data["category"]]
    }

    result = service.posts().insert(blogId=BLOGGER_BLOG_ID, body=post).execute()
    return result.get("url", "Published successfully!")

# ============================================================
# 🔄 TOPIC MANAGER - No repeats
# ============================================================

def get_next_topic() -> tuple:
    """Gets a fresh topic that hasn't been used recently"""

    used_topics = []
    if os.path.exists(USED_TOPICS_FILE):
        with open(USED_TOPICS_FILE, "r") as f:
            used_topics = json.load(f)

    # Pick a random category
    category = random.choice(list(ALL_TOPICS.keys()))
    available = [t for t in ALL_TOPICS[category] if t not in used_topics]

    # If all topics in category used, reset that category
    if not available:
        available = ALL_TOPICS[category]
        used_topics = [t for t in used_topics if t not in ALL_TOPICS[category]]

    topic = random.choice(available)

    # Save so we don't repeat
    used_topics.append(topic)
    if len(used_topics) > 50:
        used_topics = used_topics[-50:]

    with open(USED_TOPICS_FILE, "w") as f:
        json.dump(used_topics, f)

    return topic, category

# ============================================================
# 🚀 MAIN JOB - Runs every hour automatically
# ============================================================

def write_and_publish_blog():
    """Main: picks topic → writes with Gemini AI → publishes to Blogger"""

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*55}")
    print(f"⏰  Running at: {now}")
    print(f"{'='*55}")

    try:
        # Step 1: Pick a topic
        topic, category = get_next_topic()
        print(f"📌 Topic    : {topic}")
        print(f"📂 Category : {category}")

        # Step 2: Write blog with FREE Gemini AI
        print("✍️  Writing blog post with Gemini AI (FREE)...")
        blog_data = generate_blog_post(topic, category)
        print(f"✅ Written  : {blog_data['title']}")

        # Step 3: Publish to Blogger
        print("📤 Publishing to Blogger.com...")
        url = publish_to_blogger(blog_data)
        print(f"🎉 Published: {url}")

        # Save log
        log_entry = {
            "time": now,
            "title": blog_data["title"],
            "category": category,
            "url": url
        }

        logs = []
        if os.path.exists("blog_log.json"):
            with open("blog_log.json", "r") as f:
                logs = json.load(f)
        logs.append(log_entry)
        with open("blog_log.json", "w") as f:
            json.dump(logs, f, indent=2)

        print(f"📊 Total posts published so far: {len(logs)}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("⏳ Will retry at next scheduled time...")

# ============================================================
# ▶️  START
# ============================================================

if __name__ == "__main__":
    import sys

    print("=" * 55)
    print("🚀  AUTO BLOG WRITER - FREE VERSION")
    print("    Powered by Groq AI (No cost!)")
    print("=" * 55)

    # GitHub Actions passes --once to run just one post then exit
    if "--once" in sys.argv:
        print("☁️  Running in GitHub Actions mode (single post)\n")

        # Read keys from environment variables if set
        import os
        if os.environ.get("GROQ_API_KEY"):
            GROQ_API_KEY = os.environ["GROQ_API_KEY"]
        if os.environ.get("BLOGGER_BLOG_ID"):
            BLOGGER_BLOG_ID = os.environ["BLOGGER_BLOG_ID"]

        write_and_publish_blog()

    else:
        # Normal mode - runs on your PC every hour
        print(f"📅  Will post every {POST_EVERY_MINUTES} minutes")
        print("🛑  Press Ctrl+C to stop\n")

        write_and_publish_blog()

        schedule.every(POST_EVERY_MINUTES).minutes.do(write_and_publish_blog)

        while True:
            schedule.run_pending()
            time.sleep(30)
