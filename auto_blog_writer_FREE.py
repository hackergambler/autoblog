import os, sys, random, time, json, datetime
from groq import Groq
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
BLOGGER_BLOG_ID = os.environ.get("BLOGGER_BLOG_ID")

TOPICS = {
    "Mindset": ["Neuroplasticity for Adults", "The Stoic Approach to Modern Stress", "Growth Mindset vs Fixed Mindset"],
    "Finance": ["Dividend Growth Investing", "The 50/30/20 Budgeting Rule", "How to Negotiate Your Salary"],
    "Health": ["Intermittent Fasting Protocols", "The Importance of Zone 2 Cardio", "High-Protein Meal Prep"],
    "Tech": ["Building Private Cloud Storage", "The Ethics of Artificial Intelligence", "Mastering the Linux Command Line"]
}

def get_service():
    with open('token.json', 'r') as f:
        info = json.load(f)
    return build('blogger', 'v3', credentials=Credentials.from_authorized_user_info(info))

def get_styled_html(content, category, topic):
    themes = {
        "Tech": {"bg": "#0f172a", "accent": "#6366f1", "icon": "💻"},
        "Health": {"bg": "#052e16", "accent": "#22c55e", "icon": "🌿"},
        "Finance": {"bg": "#1c1917", "accent": "#f59e0b", "icon": "💰"},
        "Mindset": {"bg": "#4a044e", "accent": "#e879f9", "icon": "🧠"}
    }
    theme = themes.get(category, {"bg": "#1e293b", "accent": "#3b82f6", "icon": "📝"})
    hero_img = f"https://picsum.photos/seed/{topic.replace(' ', '')}/800/450"
    
    style = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
        .blog-wrapper {{ font-family: 'Inter', sans-serif; line-height: 1.8; color: #334155; max-width: 800px; margin: auto; }}
        .hero-banner {{ background: linear-gradient(135deg, {theme['bg']} 0%, {theme['accent']} 100%); color: white; padding: 60px 20px; border-radius: 12px; text-align: center; margin-bottom: 30px; }}
        .category-badge {{ background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; text-transform: uppercase; }}
        .key-takeaways {{ background: #f8fafc; border-left: 5px solid {theme['accent']}; padding: 25px; border-radius: 0 8px 8px 0; margin: 30px 0; }}
        h2 {{ color: {theme['bg']}; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-top: 40px; }}
        img {{ width: 100%; border-radius: 12px; margin: 20px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .action-box {{ background: {theme['bg']}; color: white; padding: 30px; border-radius: 12px; margin-top: 40px; }}
    </style>
    """
    
    return f"""
    {style}
    <div class="blog-wrapper">
        <div class="hero-banner">
            <span class="category-badge">{theme['icon']} {category}</span>
            <h1 style="font-size: 2.8rem; margin-top: 15px; line-height: 1.2;">{topic}</h1>
            <p>⏱️ 6 min read • {datetime.datetime.now().strftime('%B %d, %Y')}</p>
        </div>
        <img src="{hero_img}" alt="{topic}">
        <div class="key-takeaways">
            <h3 style="margin-top:0;">📌 Executive Summary</h3>
            <p>This deep-dive explores the core principles of {topic}, providing actionable strategies to master {category.lower()} in the modern era.</p>
        </div>
        <div class="main-content">{content}</div>
        <div class="action-box">
            <h3>🚀 Take Action Today</h3>
            <p>Don't just read—apply. Which of these strategies will you implement first? Let us know in the comments!</p>
        </div>
    </div>
    """

def generate_content(topic, cat):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"Act as an industry expert in {cat}. Write a 1200-word authoritative guide on '{topic}'. Use HTML (h2, h3, b, li). Focus on data, specific examples, and a professional tone. Avoid AI clichés."
    response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", temperature=0.7)
    return get_styled_html(response.choices[0].message.content, cat, topic)

def run():
    cat = random.choice(list(TOPICS.keys()))
    topic = random.choice(TOPICS[cat])
    content = generate_content(topic, cat)
    service = get_service()
    body = {'title': topic, 'content': content, 'labels': [cat, 'Expert Tips']}
    service.posts().insert(blogId=BLOGGER_BLOG_ID, body=body, isDraft=False).execute()
    print(f"✅ Daily Tips Published: {topic}")

if __name__ == "__main__":
    run()
