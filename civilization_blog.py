import os, sys, random, json
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

def generate_civ(topic):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"Act as a World Historian. Write a 1500-word atmospheric analysis of '{topic}'. Use HTML. Focus on cultural legacy and 'What If' scenarios. No AI summaries."
    response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", temperature=0.8)
    return response.choices[0].message.content

if __name__ == "__main__":
    topic = random.choice(CIV_TOPICS)
    service = get_service()
    body = {'title': topic, 'content': generate_civ(topic), 'labels': ['History', 'Culture']}
    service.posts().insert(blogId=CIV_BLOGGER_BLOG_ID, body=body, isDraft=False).execute()
    print(f"🏛️ Civilization Published: {topic}")
