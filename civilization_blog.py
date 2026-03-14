import os, sys, random, json, datetime
from groq import Groq
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
CIV_BLOGGER_BLOG_ID = os.environ.get("CIV_BLOGGER_BLOG_ID")
HISTORY_FILE = "civ_history.json"

CIV_TOPICS = ["The Fall of the Aztec Empire", "The Library of Ashurbanipal", "Samurai Warfare Tactics", "The Industrial Revolution's Dark Side"]

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
    <div style="font-family: 'Georgia', serif; max-width: 800px; margin: auto; background: #fffcf9; padding: 45px; border: 1px solid #dcd1bd; color: #2d241e;">
        <div style="text-align: center; border-bottom: 2px solid #8d6e63; padding-bottom: 20px; margin-bottom: 40px;">
            <p style="letter-spacing: 5px; color: #8d6e63; font-weight: bold;">THE ANCIENT ARCHIVES</p>
            <h1 style="font-size: 3rem; margin: 10px 0; color: #3e2723;">{topic}</h1>
        </div>
        <div style="line-height: 2; font-size: 1.2rem;">{content}</div>
        <div style="border-top: 3px double #8d6e63; margin-top: 60px; padding: 30px; text-align: center;">
            <p style="font-size: 1.3rem; margin: 0; color: #3e2723;"><b>Published by MYRQ</b></p>
            <p style="margin: 5px 0; font-style: italic;">{curr_date} • Human History & Lost Civilizations</p>
        </div>
    </div>"""

if __name__ == "__main__":
    history = load_history()
    pool = [t for t in CIV_TOPICS if t not in history]
    
    if not pool:
        print("History topics exhausted.")
        sys.exit()

    topic = random.choice(pool)
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"Act as a World Historian. Write a 1500-word analysis of '{topic}'. Use HTML. Tone: Academic yet captivating."
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    
    html = get_styled_html(res.choices[0].message.content, topic)
    service = get_service()
    body = {'title': topic, 'content': html, 'labels': ['History', 'Civilization']}
    service.posts().insert(blogId=CIV_BLOGGER_BLOG_ID, body=body, isDraft=False).execute()
    
    save_history(topic)
    print(f"🏛️ History Published: {topic}")
