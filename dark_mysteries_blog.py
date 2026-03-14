import os, sys, random, json, datetime
from groq import Groq
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DARK_BLOGGER_BLOG_ID = os.environ.get("DARK_BLOGGER_BLOG_ID")

DARK_TOPICS = ["The Dyatlov Pass Incident", "The Hinterkaifeck Murders", "The Lead Masks Case", "The Disappearance of the Mary Celeste"]

def get_service():
    with open('token.json', 'r') as f:
        info = json.load(f)
    return build('blogger', 'v3', credentials=Credentials.from_authorized_user_info(info))

def get_styled_html(content, topic):
    hero_img = f"https://picsum.photos/seed/{topic.replace(' ', '')}/800/450?blur=2"
    style = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=Courier+Prime&display=swap');
        .dark-wrapper { background: #121212; color: #cfd8dc; padding: 40px; font-family: 'Courier Prime', monospace; max-width: 800px; margin: auto; }
        .case-file-header { border: 2px solid #b71c1c; padding: 20px; margin-bottom: 40px; text-align: center; }
        .case-file-header h1 { color: #f44336; font-family: 'Special Elite', cursive; font-size: 2.5rem; margin: 10px 0; }
        .evidence-img { width: 100%; border: 5px solid #263238; filter: sepia(0.5) contrast(1.2); margin: 30px 0; }
        h2 { color: #f44336; border-left: 4px solid #b71c1c; padding-left: 15px; font-family: 'Special Elite', cursive; }
        .warning { color: #ffeb3b; border: 1px dashed #ffeb3b; padding: 15px; font-size: 0.9rem; margin-bottom: 20px; }
    </style>
    """
    return f"""
    {style}
    <div class="dark-wrapper">
        <div class="warning">⚠️ CONFIDENTIAL FILE: FOR RESEARCH PURPOSES ONLY</div>
        <div class="case-file-header">
            <span style="color: #b71c1c; font-weight: bold;">UNSOLVED MYSTERIES DIVISION</span>
            <h1>CASE: {topic}</h1>
            <p>Status: Open Investigation • Log Date: {datetime.datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
        <img class="evidence-img" src="{hero_img}" alt="Evidence">
        <div class="content">{content}</div>
        <div style="text-align: center; margin-top: 50px; color: #546e7a;">*** End of File ***</div>
    </div>
    """

def generate_dark(topic):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"Act as an Investigative Journalist. Write a 1500-word deep-dive on '{topic}'. Tone: Eerie, suspenseful, and objective. Structure: The Event, The Evidence, The Theories. Use HTML."
    response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return get_styled_html(response.choices[0].message.content, topic)

if __name__ == "__main__":
    topic = random.choice(DARK_TOPICS)
    service = get_service()
    body = {'title': f"Unsolved: {topic}", 'content': generate_dark(topic), 'labels': ['Mystery', 'Case Files']}
    service.posts().insert(blogId=DARK_BLOGGER_BLOG_ID, body=body, isDraft=False).execute()
    print(f"👻 Dark Mystery Published: {topic}")
