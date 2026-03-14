import os, sys, random, json, datetime
from groq import Groq
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DARK_BLOGGER_BLOG_ID = os.environ.get("DARK_BLOGGER_BLOG_ID")
HISTORY_FILE = "dark_history.json"

DARK_TOPICS = ["The Dyatlov Pass Incident", "The Hinterkaifeck Murders", "The Lead Masks Case", "The Disappearance of the Mary Celeste"]

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

def get_styled_html(content, topic):
    curr_date = datetime.datetime.now().strftime('%B %d, %Y')
    return f"""
    <div style="background: #0d0d0d; color: #d1d5db; font-family: 'Courier New', monospace; padding: 50px; max-width: 800px; margin: auto; border: 1px solid #333;">
        <div style="border: 2px solid #ff3333; padding: 25px; text-align: center; margin-bottom: 40px;">
            <p style="color: #ff3333; margin: 0; letter-spacing: 3px;">TOP SECRET // CLASSIFIED RECORD</p>
            <h1 style="color: white; font-size: 2.4rem; margin: 15px 0;">CASE: {topic}</h1>
        </div>
        <div style="line-height: 1.7; font-size: 1.1rem; padding: 0 10px;">{content}</div>
        <div style="border-top: 1px dashed #ff3333; margin-top: 70px; padding: 30px; text-align: center;">
            <p style="color: #ff3333; font-size: 1.3rem; margin: 0; letter-spacing: 2px;"><b>Published by MYRQ</b></p>
            <p style="margin: 5px 0; color: #9ca3af;">{curr_date} • Unsolved Mysteries & Conspiracies</p>
        </div>
    </div>"""

if __name__ == "__main__":
    history = load_history()
    pool = [t for t in DARK_TOPICS if t not in history]
    
    if not pool:
        print("Mystery topics exhausted.")
        sys.exit()

    topic = random.choice(pool)
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"Act as an Investigative Journalist. Write a 1500-word deep-dive on '{topic}'. Use HTML. Tone: Suspenseful."
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    
    html = get_styled_html(res.choices[0].message.content, topic)
    service = get_service()
    body = {'title': f"Unsolved: {topic}", 'content': html, 'labels': ['Dark Mysteries', 'Investigation']}
    service.posts().insert(blogId=DARK_BLOGGER_BLOG_ID, body=body, isDraft=False).execute()
    
    save_history(topic)
    print(f"👻 Case File Published: {topic}")
