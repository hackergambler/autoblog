"""
🏛️ AUTO CIVILIZATION BLOG WRITER - 100% FREE
=============================================
Automatically writes and publishes civilization blog posts
every 30 minutes using FREE Groq AI to Blogger.com

48 posts per day — Ancient, Lost, Modern, Wars, Empires!

SETUP:
1. Create new Blogger blog at https://www.blogger.com
2. Get new Blog ID from the dashboard URL
3. Reuse same credentials.json and token.json from main blog
4. Fill in GROQ_API_KEY and BLOGGER_BLOG_ID below
5. Run: python civilization_blog.py
"""

from groq import Groq
import schedule
import time
import random
import json
import os
import datetime
import sys
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ============================================================
# 🔧 YOUR SETTINGS
# ============================================================

GROQ_API_KEY    = os.environ.get("GROQ_API_KEY",    "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")
BLOGGER_BLOG_ID = os.environ.get("BLOGGER_BLOG_ID", "998461773101344795")

POST_EVERY_MINUTES = 30   # Every 30 minutes = 48 posts/day

# ============================================================
# 🏛️ CIVILIZATION TOPICS - 200+ unique topics!
# ============================================================

ALL_TOPICS = {

    "Ancient Civilizations": [
        "The rise and fall of Ancient Egypt — a complete story",
        "How the Roman Empire became the greatest power in history",
        "Ancient Greece — birthplace of democracy and philosophy",
        "Mesopotamia — the world's very first civilization",
        "The Indus Valley Civilization — India's forgotten ancient empire",
        "Ancient China — the dynasty that built the Great Wall",
        "The Persian Empire — how Cyrus the Great changed the world",
        "Ancient Carthage — Rome's greatest enemy",
        "The Phoenicians — the civilization that invented the alphabet",
        "Ancient Nubia — the African empire that rivaled Egypt",
        "The Babylonian Empire and the Code of Hammurabi",
        "Ancient Sparta — the most feared warrior society ever",
        "The Assyrian Empire — the world's first military superpower",
        "The Han Dynasty — when China ruled the ancient world",
        "Ancient Athens vs Sparta — the greatest rivalry in history",
        "The Maurya Empire — when India ruled most of Asia",
        "Ancient Sumeria — the civilization that invented writing",
        "The Zhou Dynasty — longest ruling dynasty in Chinese history",
        "Cleopatra and the last days of Ancient Egypt",
        "Julius Caesar — the man who changed Rome forever",
        "Alexander the Great — how one man conquered the known world",
        "The Olympic Games in Ancient Greece — origins and history",
        "How Ancient Egyptians really built the pyramids",
        "The Roman Colosseum — blood, glory and entertainment",
        "Ancient Roman roads — the infrastructure that built an empire",
    ],

    "Lost & Mystery Civilizations": [
        "Atlantis — myth or real lost civilization?",
        "The Maya civilization — why did they suddenly disappear?",
        "The mystery of the Indus Valley script nobody can decode",
        "Easter Island — who built the Moai statues and why?",
        "The lost city of El Dorado — fact or legend?",
        "Göbekli Tepe — the 12,000 year old temple that rewrites history",
        "The Nazca Lines — ancient messages from the sky",
        "Angkor Wat — the lost jungle city of the Khmer Empire",
        "The mystery of the Anasazi — a civilization that vanished",
        "Pompeii — the city frozen in time by Mount Vesuvius",
        "The lost kingdom of Punt — Egypt's mysterious trading partner",
        "Troy — was Homer's legendary city real?",
        "The Olmec civilization — mother of all Mesoamerican cultures",
        "Machu Picchu — the Inca city hidden in the clouds",
        "The mystery of the Sea Peoples who destroyed Bronze Age civilizations",
        "Stonehenge — who built it and what was its purpose?",
        "The lost library of Alexandria — what knowledge was destroyed?",
        "Cahokia — the forgotten Native American megacity",
        "The Minoan civilization — Europe's first advanced society",
        "Nan Madol — the mysterious floating city of the Pacific",
        "The Bronze Age Collapse — when civilizations fell overnight",
        "Zimbabwe's Great Enclosure — Africa's ancient stone city",
        "The Aksumite Empire — Ethiopia's forgotten ancient superpower",
        "Teotihuacan — the city of the gods nobody understands",
        "The mystery of the Voynich Manuscript — civilization's unsolved puzzle",
    ],

    "Medieval Civilizations": [
        "The Byzantine Empire — Rome's 1000 year successor",
        "The Islamic Golden Age — when Muslims led the world in science",
        "The Mongol Empire — the largest land empire in history",
        "The Viking Age — raiders, traders and explorers",
        "The Crusades — holy wars that changed the world",
        "Feudal Japan — samurai, shoguns and honor culture",
        "The Ottoman Empire — how it ruled for 600 years",
        "Genghis Khan — the most feared conqueror in human history",
        "The Black Death — the plague that killed half of Europe",
        "Medieval castles — how they were built and why",
        "The Knights Templar — history's most powerful secret order",
        "The Silk Road — the trade route that connected civilizations",
        "The Mali Empire — when Africa was the richest place on Earth",
        "The Aztec Empire — blood, gold and the sun god",
        "The Inca Empire — masters of mountains and engineering",
        "The Song Dynasty — China's most advanced medieval civilization",
        "Saladin — the Muslim hero who recaptured Jerusalem",
        "Joan of Arc — the peasant girl who saved France",
        "The Holy Roman Empire — neither holy nor Roman nor an empire",
        "Medieval Europe's plague doctors — terrifying history explained",
        "The Khmer Empire — builders of Angkor Wat",
        "Suleiman the Magnificent — the Ottoman sultan who terrified Europe",
        "The Samurai code of Bushido — history and philosophy",
        "Medieval torture devices — the dark side of civilization",
        "The Hanseatic League — history's first trade superpower",
    ],

    "Wars & Conquests": [
        "The Punic Wars — Rome vs Carthage — history's greatest rivalry",
        "The Peloponnesian War — how Athens destroyed itself",
        "The Mongol invasion of Europe — why they suddenly stopped",
        "The Hundred Years War — England vs France explained",
        "The Wars of the Roses — England's bloody civil war",
        "The fall of Constantinople — end of the Eastern Roman Empire",
        "The Spanish conquest of the Aztecs — how 500 men defeated millions",
        "The Battle of Marathon — 10,000 Greeks vs the Persian Empire",
        "The Battle of Thermopylae — 300 Spartans vs 100,000 Persians",
        "Napoleon's invasion of Russia — history's greatest military disaster",
        "The conquests of Alexander the Great — battle by battle",
        "The Arab conquest of Persia — how Islam spread by the sword",
        "The Norman Conquest of England — 1066 and all that",
        "Hannibal crossing the Alps — the most daring military move ever",
        "The Battle of Hastings — the day England changed forever",
        "Saladin vs the Crusaders — the battle for Jerusalem",
        "The Siege of Troy — history or myth?",
        "The Roman conquest of Britain — Caesar's invasion explained",
        "Attila the Hun — the scourge of God who terrified Rome",
        "The Battle of Waterloo — Napoleon's final defeat",
        "Timur the Lame — the conqueror who made pyramids of skulls",
        "The fall of Rome — why the greatest empire in history collapsed",
        "The Wars of Alexander's Successors — fighting over his empire",
        "The Reconquista — 700 years of war in Spain",
        "The Thirty Years War — Europe's most devastating conflict",
    ],

    "Empires & Dynasties": [
        "The British Empire — how Britain ruled a quarter of the world",
        "The Spanish Empire — gold, conquest and colonization",
        "The Mughal Empire — India's greatest Islamic dynasty",
        "The Qing Dynasty — China's last imperial dynasty",
        "The Russian Empire — from small duchy to world superpower",
        "The French Empire under Napoleon — rise and fall",
        "The Portuguese Empire — first global empire in history",
        "The Dutch Golden Age — how a small nation dominated world trade",
        "The Habsburg Dynasty — Europe's most powerful royal family",
        "The Gupta Empire — India's golden age of science and culture",
        "The Tang Dynasty — China's most cosmopolitan empire",
        "The Songhai Empire — the largest empire in African history",
        "The Safavid Empire — Persia's greatest Islamic dynasty",
        "The Maratha Empire — India's last Hindu empire",
        "The Vijayanagara Empire — South India's greatest kingdom",
        "The Chola Dynasty — the naval empire of South India",
        "The Abbasid Caliphate — the golden age of Islamic civilization",
        "The Umayyad Caliphate — Islam's first great empire",
        "The Carolingian Empire — Charlemagne's vision of Europe",
        "The Plantagenet Dynasty — England's most dramatic royal family",
        "The Medici family — bankers who ruled Florence and funded art",
        "The Tokugawa Shogunate — 250 years of peace in Japan",
        "The Achaemenid Persian Empire — Darius and Xerxes explained",
        "The Seleucid Empire — Alexander's forgotten successors",
        "The Mauryan Empire under Ashoka — from warrior to Buddhist saint",
    ],

    "Ancient Wonders & Achievements": [
        "The Seven Wonders of the Ancient World — complete guide",
        "How ancient Romans built roads that lasted 2000 years",
        "The Great Wall of China — facts that will surprise you",
        "Ancient Egyptian medicine — surprisingly advanced for its time",
        "How the Antikythera Mechanism works — world's first computer",
        "Roman aqueducts — the greatest engineering feat of the ancient world",
        "The construction of the Colosseum — engineering marvel explained",
        "Ancient Greek mathematics — how it shapes our world today",
        "The Library of Alexandria — what was lost when it burned",
        "Ancient Inca engineering — how they built without wheels or iron",
        "The Hanging Gardens of Babylon — did they really exist?",
        "How ancient Egyptians mummified their dead — step by step",
        "Greek fire — the secret weapon that saved the Byzantine Empire",
        "Ancient Roman concrete — why it's still stronger than modern cement",
        "The Lighthouse of Alexandria — wonder of the ancient world",
        "How ancient civilizations tracked time and created calendars",
        "Ancient Indian surgery — Sushruta performed plastic surgery 2600 years ago",
        "The Baghdad Battery — did ancients discover electricity?",
        "How Archimedes almost sank the Roman fleet",
        "The terracotta army of Emperor Qin — 8000 soldiers buried in silence",
        "Ancient Mesopotamian astronomy — mapping the stars 5000 years ago",
        "The Rosetta Stone — how it unlocked Egyptian hieroglyphics",
        "Ancient Roman gladiators — the full brutal truth",
        "How the Maya predicted eclipses without modern technology",
        "Ancient Greek Olympic sports — stranger than you think",
    ],

    "Civilizations & Religion": [
        "Ancient Egyptian religion — gods, afterlife and rituals explained",
        "How Christianity spread across the Roman Empire",
        "The birth of Islam and the first Muslim civilization",
        "Hindu civilization — the world's oldest living religion",
        "Ancient Greek gods and how they shaped civilization",
        "The spread of Buddhism from India to Asia",
        "Zoroastrianism — the ancient Persian religion that influenced all others",
        "The Aztec religion — why they sacrificed thousands of people",
        "Ancient Norse religion — Vikings, Odin and Valhalla",
        "The Dead Sea Scrolls — what they reveal about ancient civilization",
        "The Druids — Celtic priests of the ancient world",
        "Ancient Roman religion — how it changed under Constantine",
        "The Inquisition — religion, power and persecution in medieval Europe",
        "Shinto — Japan's ancient indigenous religion explained",
        "The role of priests in ancient Mesopotamian civilization",
        "Ancient Egyptian Book of the Dead — guide to the afterlife",
        "How the Catholic Church shaped medieval European civilization",
        "The Reformation — Martin Luther and the split of Christianity",
        "Ancient Mayan religion — gods, sacrifice and the cosmic calendar",
        "The Crusades and the clash of Islamic and Christian civilizations",
        "Confucianism — how one philosopher's ideas shaped China for 2500 years",
        "The Inca religion — Inti the sun god and human sacrifice",
        "Ancient Sumerian gods — the original mythology",
        "The Jewish civilization — history of the world's oldest monotheistic religion",
        "How Alexander the Great tried to merge Greek and Persian religion",
    ],
}

USED_TOPICS_FILE = "civ_used_topics.json"

# ============================================================
# 🧠 GROQ AI — Blog Writer
# ============================================================

def generate_blog_post(topic: str, category: str) -> dict:
    """Uses FREE Groq AI to write a civilization blog post"""

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""Write a fascinating, detailed blog post about: "{topic}"
Category: {category}

Requirements:
- Write in engaging, storytelling style — like a documentary narrator
- Length: 700-900 words
- Start with a dramatic hook that grabs attention immediately
- Include surprising facts most people don't know
- Use subheadings to organize content
- Include historical dates and real names
- Make history feel alive and exciting
- End with why this civilization/event matters today

Return ONLY a JSON object (no markdown, no extra text):
{{
  "title": "dramatic, curiosity-driving blog title",
  "content": "full blog in HTML using <h2>, <p>, <ul>, <li> tags",
  "meta_description": "SEO description under 155 characters",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=2000
    )

    response_text = response.choices[0].message.content.strip()

    import re
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    response_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', response_text)

    try:
        blog_data = json.loads(response_text)
    except json.JSONDecodeError:
        # Retry with simpler prompt
        simple = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f'Write about "{topic}". Return ONLY JSON: {{"title":"title","content":"<p>content</p>","meta_description":"desc","tags":["t1","t2","t3"]}}'}],
            temperature=0.5,
            max_tokens=2000
        )
        simple_text = simple.choices[0].message.content.strip()
        if "```json" in simple_text:
            simple_text = simple_text.split("```json")[1].split("```")[0].strip()
        elif "```" in simple_text:
            simple_text = simple_text.split("```")[1].split("```")[0].strip()
        simple_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', simple_text)
        blog_data = json.loads(simple_text)

    blog_data["category"] = category
    blog_data["topic"]    = topic
    return blog_data


# ============================================================
# 🎨 BEAUTIFUL CIVILIZATION STYLING
# ============================================================

def get_category_style(category: str) -> dict:
    """Returns ancient/historical color theme per category"""
    styles = {
        "Ancient Civilizations":        {"bg": "#1a0a00", "accent": "#c9a84c", "badge": "#f0c040", "text": "#fff8e7"},
        "Lost & Mystery Civilizations": {"bg": "#0d0d2b", "accent": "#7c3aed", "badge": "#a78bfa", "text": "#ede9fe"},
        "Medieval Civilizations":       {"bg": "#0f1a0a", "accent": "#4d7c0f", "badge": "#84cc16", "text": "#f0fdf4"},
        "Wars & Conquests":             {"bg": "#1a0000", "accent": "#dc2626", "badge": "#f87171", "text": "#fff1f1"},
        "Empires & Dynasties":          {"bg": "#0a0a1a", "accent": "#2563eb", "badge": "#60a5fa", "text": "#eff6ff"},
        "Ancient Wonders & Achievements": {"bg": "#1a0f00", "accent": "#d97706", "badge": "#fbbf24", "text": "#fffbeb"},
        "Civilizations & Religion":     {"bg": "#1a0a1a", "accent": "#9333ea", "badge": "#c084fc", "text": "#fdf4ff"},
    }
    return styles.get(category, {"bg": "#1a1000", "accent": "#c9a84c", "badge": "#f0c040", "text": "#fff8e7"})


# ============================================================
# 📝 BLOGGER PUBLISHER
# ============================================================

SCOPES = ["https://www.googleapis.com/auth/blogger"]

def get_blogger_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open("token.json", "w") as token:
                    token.write(creds.to_json())
                print("🔄  Token refreshed successfully")
            except Exception as e:
                print(f"⚠️  Token refresh failed: {e} — re-authenticating...")
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
            print("✅  New token saved")
    return build("blogger", "v3", credentials=creds)


def get_topic_image(topic: str, category: str) -> str:
    """Pick a curated, always-working image matched to the category."""
    IMAGE_POOL = {
        "Ancient Civilizations": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Kheops-Pyramid.jpg/800px-Kheops-Pyramid.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseum_in_Rome%2C_Italy_-_April_2007.jpg/800px-Colosseum_in_Rome%2C_Italy_-_April_2007.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Parthenon_from_west.jpg/800px-Parthenon_from_west.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/800px-Camponotus_flavomarginatus_ant.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Great_Wall_of_China_July_2006.jpg/800px-Great_Wall_of_China_July_2006.jpg",
        ],
        "Lost & Mystery Civilizations": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Nazca_monkey.jpg/800px-Nazca_monkey.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Machu_Picchu%2C_Peru.jpg/800px-Machu_Picchu%2C_Peru.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Stonehenge_at_dusk.jpg/800px-Stonehenge_at_dusk.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Stonehenge2007_07_30.jpg/800px-Stonehenge2007_07_30.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Voynich_Manuscript_%28166%29.jpg/800px-Voynich_Manuscript_%28166%29.jpg",
        ],
        "Medieval Civilizations": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Notre-Dame_de_Paris_2013-07-24.jpg/800px-Notre-Dame_de_Paris_2013-07-24.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Carcassonne_Castle_and_Town.jpg/800px-Carcassonne_Castle_and_Town.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Bodiam-castle-10My8-1197.jpg/800px-Bodiam-castle-10My8-1197.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Neuschwanstein_Castle_Schwangau_Germany_Luc_Viatour.jpg/800px-Neuschwanstein_Castle_Schwangau_Germany_Luc_Viatour.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Hagia_Sophia_Mars_2013.jpg/800px-Hagia_Sophia_Mars_2013.jpg",
        ],
        "Wars & Conquests": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Sto%C5%99ov%C3%A9_v%C3%A1lky.jpg/800px-Sto%C5%99ov%C3%A9_v%C3%A1lky.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseum_in_Rome%2C_Italy_-_April_2007.jpg/800px-Colosseum_in_Rome%2C_Italy_-_April_2007.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Bodiam-castle-10My8-1197.jpg/800px-Bodiam-castle-10My8-1197.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Great_Wall_of_China_July_2006.jpg/800px-Great_Wall_of_China_July_2006.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Stonehenge_at_dusk.jpg/800px-Stonehenge_at_dusk.jpg",
        ],
        "Empires & Dynasties": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseum_in_Rome%2C_Italy_-_April_2007.jpg/800px-Colosseum_in_Rome%2C_Italy_-_April_2007.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Kheops-Pyramid.jpg/800px-Kheops-Pyramid.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Hagia_Sophia_Mars_2013.jpg/800px-Hagia_Sophia_Mars_2013.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Great_Wall_of_China_July_2006.jpg/800px-Great_Wall_of_China_July_2006.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Neuschwanstein_Castle_Schwangau_Germany_Luc_Viatour.jpg/800px-Neuschwanstein_Castle_Schwangau_Germany_Luc_Viatour.jpg",
        ],
        "Inventions & Discoveries": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Parthenon_from_west.jpg/800px-Parthenon_from_west.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Kheops-Pyramid.jpg/800px-Kheops-Pyramid.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Voynich_Manuscript_%28166%29.jpg/800px-Voynich_Manuscript_%28166%29.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Nazca_monkey.jpg/800px-Nazca_monkey.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Great_Wall_of_China_July_2006.jpg/800px-Great_Wall_of_China_July_2006.jpg",
        ],
        "Religion & Philosophy": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Hagia_Sophia_Mars_2013.jpg/800px-Hagia_Sophia_Mars_2013.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Notre-Dame_de_Paris_2013-07-24.jpg/800px-Notre-Dame_de_Paris_2013-07-24.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Parthenon_from_west.jpg/800px-Parthenon_from_west.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Machu_Picchu%2C_Peru.jpg/800px-Machu_Picchu%2C_Peru.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Kheops-Pyramid.jpg/800px-Kheops-Pyramid.jpg",
        ],
        "Great Leaders & Conquerors": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseum_in_Rome%2C_Italy_-_April_2007.jpg/800px-Colosseum_in_Rome%2C_Italy_-_April_2007.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Bodiam-castle-10My8-1197.jpg/800px-Bodiam-castle-10My8-1197.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Kheops-Pyramid.jpg/800px-Kheops-Pyramid.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Great_Wall_of_China_July_2006.jpg/800px-Great_Wall_of_China_July_2006.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Machu_Picchu%2C_Peru.jpg/800px-Machu_Picchu%2C_Peru.jpg",
        ],
    }
    default_pool = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Kheops-Pyramid.jpg/800px-Kheops-Pyramid.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseum_in_Rome%2C_Italy_-_April_2007.jpg/800px-Colosseum_in_Rome%2C_Italy_-_April_2007.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Machu_Picchu%2C_Peru.jpg/800px-Machu_Picchu%2C_Peru.jpg",
    ]
    pool = IMAGE_POOL.get(category, default_pool)
    # Use topic hash so same topic always gets same image
    idx = abs(hash(topic)) % len(pool)
    return pool[idx]


def publish_to_blogger(blog_data: dict) -> str:
    service = get_blogger_service()

    style   = get_category_style(blog_data["category"])
    img_url = get_topic_image(blog_data["topic"], blog_data["category"])
    ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    now_str = datetime.datetime.now(ist).strftime("%B %d, %Y")

    full_content = f"""
<div style="font-family:'Segoe UI',Georgia,serif; max-width:860px; margin:0 auto; color:#1a1a1a; line-height:1.85;">

  <!-- HERO IMAGE -->
  <div style="position:relative; border-radius:14px; overflow:hidden; margin-bottom:30px; box-shadow:0 20px 60px rgba(0,0,0,0.4);">
    <img src="{img_url}" alt="{blog_data['topic']}" style="width:100%; height:360px; object-fit:cover; display:block; filter:sepia(30%) contrast(110%);"/>
    <div style="position:absolute; inset:0; background:linear-gradient(to top, {style['bg']}f0 0%, transparent 55%);"></div>
    <div style="position:absolute; bottom:0; left:0; right:0; padding:28px;">
      <span style="background:{style['accent']}; color:#fff; padding:5px 16px; border-radius:20px; font-size:12px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase;">
        🏛️ {blog_data['category']}
      </span>
      <p style="color:rgba(255,255,255,0.8); font-size:13px; margin:10px 0 0;">📅 {now_str}</p>
    </div>
  </div>

  <!-- CONTENT CARD -->
  <div style="background:#fffdf5; border-radius:14px; padding:40px; box-shadow:0 4px 24px rgba(0,0,0,0.08); border:1px solid {style['accent']}30;">

    <!-- Category badge -->
    <div style="display:inline-flex; align-items:center; gap:8px; background:{style['bg']}15; border:1px solid {style['accent']}50; border-radius:8px; padding:8px 16px; margin-bottom:24px;">
      <span style="width:8px; height:8px; border-radius:50%; background:{style['accent']}; display:inline-block;"></span>
      <span style="color:{style['bg']}; font-size:13px; font-weight:700; letter-spacing:0.5px;">{blog_data['category']}</span>
    </div>

    <!-- Main content -->
    <div style="color:#2d2d2d; font-size:17px; line-height:1.9;">
      <style scoped>
        h2 {{ color:{style['bg']}; font-size:22px; font-weight:800; margin:32px 0 12px; padding-left:14px; border-left:4px solid {style['accent']}; font-family:Georgia,serif; }}
        p {{ margin:0 0 18px; }}
        ul,ol {{ padding-left:24px; margin-bottom:18px; }}
        li {{ margin-bottom:8px; }}
        strong {{ color:{style['bg']}; }}
      </style>
      {blog_data['content']}
    </div>

    <hr style="border:none; border-top:2px solid {style['accent']}30; margin:32px 0;"/>

    <!-- Tags -->
    <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:24px;">
      {''.join([f'<span style="background:{style["bg"]}12; color:{style["bg"]}; border:1px solid {style["accent"]}40; padding:4px 14px; border-radius:20px; font-size:13px; font-weight:600;">#{tag}</span>' for tag in blog_data.get('tags',[])])}
    </div>

    <!-- Footer -->
    <div style="background:linear-gradient(135deg,{style['bg']},{style['bg']}dd); border-radius:12px; padding:20px 24px; display:flex; align-items:center; justify-content:space-between;">
      <div>
        <p style="color:{style['badge']}; font-size:13px; margin:0 0 4px; font-weight:600;">Published by MYRQ</p>
        <p style="color:{style['text']}; font-size:12px; margin:0; opacity:0.7;">{now_str} • {blog_data['category']}</p>
      </div>
      <span style="font-size:28px;">🏛️</span>
    </div>

  </div>
</div>
"""

    post   = {
        "title":   blog_data["title"],
        "content": full_content,
        "labels":  blog_data.get("tags", []) + [blog_data["category"]]
    }
    result = service.posts().insert(blogId=BLOGGER_BLOG_ID, body=post).execute()
    return result.get("url", "Published!")


# ============================================================
# 🔄 TOPIC MANAGER
# ============================================================

def get_next_topic() -> tuple:
    used = []
    if os.path.exists(USED_TOPICS_FILE):
        with open(USED_TOPICS_FILE) as f:
            used = json.load(f)

    category  = random.choice(list(ALL_TOPICS.keys()))
    available = [t for t in ALL_TOPICS[category] if t not in used]

    if not available:
        available = ALL_TOPICS[category]
        used = [t for t in used if t not in ALL_TOPICS[category]]

    topic = random.choice(available)
    used.append(topic)
    if len(used) > 150:
        used = used[-150:]

    with open(USED_TOPICS_FILE, "w") as f:
        json.dump(used, f)

    return topic, category


# ============================================================
# 🚀 MAIN JOB
# ============================================================

def write_and_publish():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*55}")
    print(f"⏰  {now}")
    print(f"{'='*55}")

    try:
        topic, category = get_next_topic()
        print(f"🏛️  Topic    : {topic}")
        print(f"📂  Category : {category}")

        print("✍️   Writing with Groq AI...")
        blog_data = generate_blog_post(topic, category)
        print(f"✅  Written  : {blog_data['title']}")

        print("📤  Publishing to Blogger...")
        url = publish_to_blogger(blog_data)
        print(f"🎉  Published: {url}")

        # Save log
        logs = []
        if os.path.exists("civ_blog_log.json"):
            with open("civ_blog_log.json") as f:
                logs = json.load(f)
        logs.append({"time": now, "title": blog_data["title"], "category": category, "url": url})
        with open("civ_blog_log.json", "w") as f:
            json.dump(logs, f, indent=2)
        print(f"📊  Total posts: {len(logs)}")

    except KeyboardInterrupt:
        raise
    except Exception as e:
        import traceback
        print(f"❌  Error: {e}")
        print(traceback.format_exc())
        print("⏳  Will retry next time...")


# ============================================================
# ▶️  START
# ============================================================

if __name__ == "__main__":
    print("=" * 55)
    print("🏛️   CIVILIZATION BLOG WRITER")
    print("     Powered by Groq AI — Published by MYRQ")
    print("=" * 55)

    if "--once" in sys.argv:
        print("☁️   GitHub Actions mode — single post\n")
        print(f"🔑  Using Blog ID: {BLOGGER_BLOG_ID}")
        write_and_publish()
    else:
        print(f"📅  Posting every {POST_EVERY_MINUTES} minutes (48 posts/day)")
        print("🛑  Press Ctrl+C to stop\n")
        write_and_publish()
        schedule.every(POST_EVERY_MINUTES).minutes.do(write_and_publish)
        while True:
            try:
                schedule.run_pending()
            except Exception as e:
                print(f"⚠️  Scheduler error (continuing): {e}")
            time.sleep(1)
