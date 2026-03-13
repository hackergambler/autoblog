import os, sys, random, time, json, datetime
from groq import Groq
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
BLOGGER_BLOG_ID = os.environ.get("BLOGGER_BLOG_ID")

# 200+ Topics logic - Categorized for variety
TOPICS = {
    "Mindset": ["Neuroplasticity for Adults", "The Stoic Approach to Modern Stress", "Growth Mindset vs Fixed Mindset"],
    "Finance": ["Dividend Growth Investing", "The 50/30/20 Budgeting Rule", "How to Negotiate Your Salary"],
    "Health": ["Intermittent Fasting Protocols", "The Importance of Zone 2 Cardio", "High-Protein Meal Prep for Busy Professionals"],
    "Tech": ["Building Private Cloud Storage", "The Ethics of Artificial Intelligence", "Mastering the Linux Command Line"]
}

def get_service():
    with open('token.json', 'r') as f:
        info = json.load(f)
    return build('blogger', 'v3', credentials=Credentials.from_authorized_user_info(info))

def generate_content(topic, cat):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"Act as an expert in {cat}. Write a 1200-word deep-dive on '{topic}'. Use HTML tags <h2>, <h3>, <b>. No AI clichés. Focus on actionable value."
    response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", temperature=0.7)
    return response.choices[0].message.content

def run():
    cat = random.choice(list(TOPICS.keys()))
    topic = random.choice(TOPICS[cat])
    content = generate_content(topic, cat)
    service = get_service()
    body = {'title': topic, 'content': content, 'labels': [cat, 'Expert Tips']}
    # Set isDraft=True if appeal is still pending
    service.posts().insert(blogId=BLOGGER_BLOG_ID, body=body, isDraft=False).execute()
    print(f"✅ Daily Tips Published: {topic}")

if __name__ == "__main__":
    run()
