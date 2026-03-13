import os, sys, random, json
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

def generate_dark(topic):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"Act as an Investigative Journalist. Write a 1500-word report on '{topic}'. Tone: Eerie and objective. Structure: The Event, The Evidence, The Theories. HTML only."
    response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return response.choices[0].message.content

if __name__ == "__main__":
    topic = random.choice(DARK_TOPICS)
    service = get_service()
    body = {'title': f"Unsolved: {topic}", 'content': generate_dark(topic), 'labels': ['Mystery', 'Investigation']}
    service.posts().insert(blogId=DARK_BLOGGER_BLOG_ID, body=body, isDraft=False).execute()
    print(f"👻 Dark Mystery Published: {topic}")
