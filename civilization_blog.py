import os, sys, random, json, datetime
from groq import Groq
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
CIV_BLOGGER_BLOG_ID = os.environ.get("CIV_BLOGGER_BLOG_ID")

CIV_TOPICS = ["The Fall of the Aztec Empire", "The Library of Ashurbanipal", "Samurai Warfare Tactics", "The Industrial Revolution's Dark Side"]

def get_service():
    with open('token.json', 'r') as f:
        info = json.load(f)
    return build('blogger', 'v3', credentials=Credentials.from_authorized_user_info(info))

def get_styled_html(content, topic):
    hero_img = f"https://picsum.photos/seed/{topic.replace(' ', '')}/800/450?grayscale"
    style = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,700;1,400&display=swap');
        .civ-wrapper { font-family: 'Crimson Pro', serif; line-height: 1.9; color: #2d2d2d; max-width: 800px; margin: auto; }
        .civ-header { border-top: 4px double #8d6e63; border-bottom: 4px double #8d6e63; padding: 40px 0; text-align: center; margin-bottom: 40px; background: #fffcf5; }
        .civ-header h1 { font-size: 3rem; color: #3e2723; margin: 10px 0; }
        .civ-image { width: 100%; border: 1px solid #d7ccc8; padding: 10px; margin: 30px 0; }
        .historical-note { background: #fdf5e6; padding: 30px; font-style: italic; border-left: 4px solid #8d6e63; margin: 30px 0; }
        h2 { font-size: 2rem; color: #5d4037; border-bottom: 1px solid #d7ccc8; padding-bottom: 5px; }
    </style>
    """
    return f"""
    {style}
    <div class="civ-wrapper">
        <div class="civ-header">
            <span style="letter-spacing: 3px; color: #8d6e63; font-weight: bold;">CHRONICLES OF TIME</span>
            <h1>{topic}</h1>
            <p>Historical Analysis • {datetime.datetime.now().strftime('%Y')}</p>
        </div>
        <img class="civ-image" src="{hero_img}" alt="{topic}">
        <div class="historical-note">
            "To understand the present, one must first unravel the tapestry of the past."
        </div>
        <div class="content">{content}</div>
    </div>
    """

def generate_civ(topic):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"Act as a World Historian. Write a 1500-word atmospheric analysis of '{topic}'. Use HTML. Focus on cultural legacy and 'What If' scenarios. Tone: Academic yet captivating."
    response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", temperature=0.8)
    return get_styled_html(response.choices[0].message.content, topic)

if __name__ == "__main__":
    topic = random.choice(CIV_TOPICS)
    service = get_service()
    body = {'title': topic, 'content': generate_civ(topic), 'labels': ['History', 'Civilization']}
    service.posts().insert(blogId=CIV_BLOGGER_BLOG_ID, body=body, isDraft=False).execute()
    print(f"🏛️ Civilization Published: {topic}")
