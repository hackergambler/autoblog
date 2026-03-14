import os, sys, random, json, datetime, time
from groq import Groq
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
BLOGGER_BLOG_ID = os.environ.get("BLOGGER_BLOG_ID")
HISTORY_FILE = "used_topics.json"

TOPICS = {
    "Mindset": ["Neuroplasticity for Adults", "The Stoic Approach to Modern Stress", "Growth Mindset vs Fixed Mindset"],
    "Finance": ["Dividend Growth Investing", "The 50/30/20 Budgeting Rule", "How to Negotiate Your Salary"],
    "Health": ["Intermittent Fasting Protocols", "The Importance of Zone 2 Cardio", "High-Protein Meal Prep"],
    "Tech": ["Building Private Cloud Storage", "The Ethics of Artificial Intelligence", "Mastering the Linux Command Line"]
}

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f: return json.load(f)
        except: return []
    return []

def save_history(topic):
    history = load_history()
    history.append(topic)
    with open(HISTORY_FILE, "w") as f: json.dump(history, f)

def get_service():
    with open('token.json', 'r') as f:
        info = json.load(f)
    return build('blogger', 'v3', credentials=Credentials.from_authorized_user_info(info))

def get_styled_html(content, category, topic):
    curr_date = datetime.datetime.now().strftime('%B %d, %Y')
    return f"""
    <div style="font-family: 'Helvetica', sans-serif; max-width: 800px; margin: auto; color: #334; line-height: 1.8;">
        <div style="background: #1e293b; color: white; padding: 50px 30px; border-radius: 15px; text-align: center; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 2.5rem;">{topic}</h1>
            <p style="text-transform: uppercase; letter-spacing: 2px; opacity: 0.8;">{category} • {curr_date}</p>
        </div>
        <div style="font-size: 1.1rem;">{content}</div>
        <div style="border-top: 2px solid #f1f5f9; margin-top: 60px; padding: 30px; text-align: center; color: #1e293b;">
            <p style="margin: 0; font-size: 1.2rem;"><b>Published by MYRQ</b></p>
            <p style="margin: 5px 0; color: #64748b;">{curr_date} • Expert Insights & Daily Tips</p>
        </div>
    </div>"""

def run():
    history = load_history()
    pool = [(c, t) for c, ts in TOPICS.items() for t in ts if t not in history]
    
    if not pool:
        print("All topics used. Resetting history.")
        with open(HISTORY_FILE, "w") as f: json.dump([], f)
        return

    cat, topic = random.choice(pool)
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"Write a 1200-word expert guide on '{topic}'. Use HTML tags (h2, h3, p). No AI intros."
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    
    html_content = get_styled_html(res.choices[0].message.content, cat, topic)
    
    service = get_service()
    body = {'title': topic, 'content': html_content, 'labels': [cat, 'Expert Tips']}
    service.posts().insert(blogId=BLOGGER_BLOG_ID, body=body, isDraft=False).execute()
    
    save_history(topic)
    print(f"✅ Daily Tip Published: {topic}")

if __name__ == "__main__":
    run()
