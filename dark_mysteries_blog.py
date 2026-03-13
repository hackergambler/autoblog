"""
👻 AUTO DARK MYSTERIES BLOG WRITER - 100% FREE
===============================================
Automatically writes and publishes dark, mysterious blog posts
every 30 minutes using FREE Groq AI to Blogger.com

48 posts per day — Ghosts, Rituals, Cryptids, Mysteries & more!

SETUP:
1. Create new Blogger blog at https://www.blogger.com
2. Get new Blog ID from dashboard URL
3. Reuse same credentials.json and token.json
4. Fill in GROQ_API_KEY and BLOGGER_BLOG_ID below
5. Run: python dark_mysteries_blog.py
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
BLOGGER_BLOG_ID = os.environ.get("BLOGGER_BLOG_ID", "2282255122948388275")

POST_EVERY_MINUTES = 30

# ============================================================
# 👻 DARK MYSTERIES TOPICS - 200+ unique topics!
# ============================================================

ALL_TOPICS = {

    "Ghost Stories & Hauntings": [
        "The Winchester Mystery House — why Sarah Winchester never stopped building",
        "The Amityville Horror — real haunting or elaborate hoax?",
        "The Bell Witch of Tennessee — America's most documented haunting",
        "The Stanley Hotel — the real haunted hotel that inspired The Shining",
        "Tower of London ghosts — centuries of royal apparitions",
        "The Myrtles Plantation — the most haunted house in America",
        "Gettysburg battlefield ghosts — soldiers who never left",
        "The Flying Dutchman — the ghost ship that sailors fear",
        "Poveglia Island — Italy's most terrifying haunted island",
        "The Haunting of Eastern State Penitentiary — prisoners who stayed",
        "Raynham Hall's Brown Lady — the most famous ghost photograph ever taken",
        "The ghost of Anne Boleyn — haunting the Tower of London",
        "Borley Rectory — England's most haunted house destroyed by fire",
        "The SS Ourang Medan — the ghost ship with a crew of corpses",
        "Japan's Aokigahara Forest — the haunted suicide forest",
        "The ghost children of San Antonio railroad tracks",
        "Edinburgh's underground vaults — Scotland's most haunted place",
        "The haunted Alcatraz prison — spirits that never escaped",
        "Screaming tunnels of Niagara — the dark legend explained",
        "The haunted Paris Catacombs — 6 million souls beneath the city",
        "The White House ghosts — presidents who never left",
        "Highgate Cemetery vampires — London's most chilling legend",
        "The ghost ship Mary Celeste — abandoned with no explanation",
        "Pluckley — England's most haunted village with 12 ghosts",
        "The haunted Fairmont Banff Springs Hotel — Canada's dark secret",
    ],

    "Dark Rituals & Occult": [
        "The real history of voodoo — not what Hollywood shows you",
        "Satanic rituals through history — separating fact from fiction",
        "The black mass — history of the most forbidden ritual",
        "Ancient Egyptian death rituals — preparing for the afterlife",
        "The Aztec ritual of human sacrifice — why they really did it",
        "Witchcraft trials — the real story behind Salem",
        "The Hellfire Club — Britain's most notorious secret society",
        "Blood rituals in ancient civilizations — the shocking truth",
        "Santeria — the misunderstood Afro-Caribbean religion",
        "The Book of Shadows — what Wiccans really practice",
        "Skull and Bones — Yale's most secretive occult society",
        "The real history of exorcism — from ancient times to today",
        "Dark rituals of the Druids — what Caesar witnessed in Britain",
        "Alchemy — the occult science that created modern chemistry",
        "The Hermetic Order of the Golden Dawn — magic and madness",
        "Aleister Crowley — the wickedest man in the world explained",
        "Ancient Sumerian demon rituals — the first exorcisms in history",
        "The dark history of tarot cards — not what you think",
        "Voodoo dolls — the real history behind the myth",
        "The Rosicrucians — the mysterious brotherhood of the rose cross",
        "Ancient Greek necromancy — consulting the dead for prophecy",
        "The real history of werewolf rituals in medieval Europe",
        "Haitian zombie rituals — the terrifying truth behind the myth",
        "The dark magic of the Aztec priests — forbidden knowledge",
        "Ancient Indian Aghori monks — the most extreme ritual practice",
    ],

    "Unsolved Mysteries & Conspiracies": [
        "The Zodiac Killer — was he ever really identified?",
        "The Dyatlov Pass incident — nine hikers died in unexplained terror",
        "The disappearance of Amelia Earhart — what really happened",
        "The Voynich Manuscript — a book nobody can read",
        "The Bermuda Triangle — real danger or media myth?",
        "D.B. Cooper — the only unsolved airplane hijacking in US history",
        "The Tamam Shud case — history's most mysterious unidentified body",
        "The Roanoke Colony — 117 people who vanished without a trace",
        "The Wow! Signal — the alien message we received once and never again",
        "The Black Dahlia murder — Hollywood's most gruesome cold case",
        "The mystery of the Mary Celeste — abandoned ship with no explanation",
        "The Tunguska event — the massive explosion with no crater",
        "The Somerton Man — the unidentified body that baffled Australia",
        "The disappearance of the crew of the Carroll A. Deering",
        "The Paulding Light — Michigan's unexplained phenomenon",
        "The lead masks case — two men dead with no cause of death",
        "The Max Headroom broadcast intrusion — TV's strangest mystery",
        "The Green children of Woolpit — medieval England's strangest story",
        "The mysterious death of Edgar Allan Poe — still unsolved",
        "The Oakville blobs — mysterious gelatinous substance fell from the sky",
        "The Overtoun Bridge — why dogs keep jumping to their deaths",
        "The Solway Firth Spaceman — the photo that shocked the world",
        "The mystery of the Circleville letters — terror by anonymous mail",
        "The Dancing Plague of 1518 — when hundreds danced until they died",
        "The Hinterkaifeck murders — Germany's most chilling cold case",
    ],

    "Paranormal & Supernatural": [
        "The Philadelphia Experiment — did the US Navy make a ship invisible?",
        "Skinwalker Ranch — America's most paranormal place explained",
        "The Mothman prophecies — the creature that predicted disaster",
        "Shadow people — what are they and why do people see them?",
        "Sleep paralysis demons — science vs supernatural explained",
        "The Hat Man — the dark figure seen across the world",
        "Poltergeists — real phenomenon or psychological trick?",
        "The Enfield Poltergeist — the most investigated case in history",
        "Near death experiences — what people see when they die",
        "Past life memories of children — cases science cannot explain",
        "The Flatwoods Monster — the alien encounter of 1952",
        "Men in Black — the dark truth behind the legend",
        "Out of body experiences — what science says about them",
        "The Slender Man phenomenon — when fiction became real",
        "Electronic Voice Phenomena — are the dead speaking to us?",
        "The Cottingley Fairies — the hoax that fooled Arthur Conan Doyle",
        "Spontaneous human combustion — the terrifying mystery explained",
        "The Black Eyed Children — the disturbing encounters explained",
        "Time slips — people who claim to have traveled through time",
        "Demon possession — the cases doctors could not explain",
        "The Incubus and Succubus — night demons through history",
        "The Jersey Devil — 300 years of terror in the Pine Barrens",
        "Crop circles — who or what is really making them",
        "Ouija boards — dangerous toy or portal to the dead?",
        "The Stull Cemetery — the gateway to hell in Kansas",
    ],

    "Cursed Objects & Places": [
        "The Hope Diamond — the cursed gem that destroyed its owners",
        "The Crying Boy painting — the cursed artwork that survived fires",
        "Annabelle the doll — the real story behind the horror movie",
        "The cursed tomb of Tutankhamun — did the mummy's curse kill 20 people?",
        "Robert the Doll — Key West's most terrifying haunted toy",
        "The cursed Basano Vase — the Italian artifact that killed its owners",
        "The Dybbuk Box — the haunted wine cabinet that terrorized owners",
        "The Little Bastard — James Dean's cursed car that killed again",
        "The cursed Black Aggie statue — the graveyard horror of Baltimore",
        "The Ötzi Iceman curse — the mummy that killed its discoverers",
        "The cursed editions of the book 'The Hands of Orlac'",
        "Zak Bagans' haunted museum — the most cursed collection on Earth",
        "The Conjure Chest — the Kentucky antique with a deadly history",
        "The cursed island of Poveglia — Italy's forbidden island",
        "The Paris Catacombs — the city beneath the city of the dead",
        "The Devil's Pool at Babinda — Australia's most cursed swimming hole",
        "The Bermuda Triangle — zone of disappearances and strange events",
        "The cursed village of Kuldhara — abandoned overnight 200 years ago",
        "The island of the dolls in Mexico — thousands of haunted dolls",
        "The cursed Unlucky Mummy of the British Museum",
        "The Hands Resist Him painting — the eBay listing that terrified buyers",
        "The cursed seat 113 at the Estadio Olímpico Universitario",
        "The Malay Kris — the cursed daggers of Southeast Asia",
        "The cursed Myrtles Plantation mirror — trapping souls since 1800s",
        "The Devil's Chair at Cassadaga Cemetery — sit and meet the Devil",
    ],

    "Urban Legends & Folklore": [
        "The Hook — America's most enduring urban legend explained",
        "Bloody Mary — the ritual millions of children have tried",
        "The Slit-Mouthed Woman — Japan's most terrifying urban legend",
        "The legend of Spring Heeled Jack — Victorian England's demon",
        "The Vanishing Hitchhiker — the ghost story told worldwide",
        "La Llorona — the weeping woman of Mexican folklore",
        "The Kentucky Meat Shower — when meat fell from the sky",
        "The Pied Piper of Hamelin — the dark truth behind the fairy tale",
        "Charlie Charlie Challenge — the Mexican demon summoning game",
        "The legend of the Beast of Gévaudan — France's mysterious killer",
        "Slender Man — the internet legend that drove girls to murder",
        "The Bunny Man of Virginia — the axe-wielding rabbit legend",
        "The Black-Eyed Susan — the ghost of Route 40",
        "The legend of Stingy Jack — the real origin of Jack-o-lanterns",
        "The Seven Gates of Hell in Pennsylvania — urban legend explored",
        "The Wendigo — the cannibalistic monster of Native American legend",
        "The Chupacabra — the blood-sucking creature of Latin America",
        "The real story behind Hansel and Gretel — darker than you know",
        "The Banshee — Ireland's death messenger explained",
        "The Legend of the Flying Dutchman — ghost ship of the seas",
        "Mothman — the legend of Point Pleasant West Virginia",
        "The real origin of vampire legends — it's not Dracula",
        "The Kuchisake-onna — the slit-mouthed woman of Japan",
        "The Bunyip — Australia's most feared mythological creature",
        "The real story behind the legend of El Coco",
    ],

    "True Crime & Dark History": [
        "Jack the Ripper — the unsolved murders that shocked Victorian London",
        "H.H. Holmes — America's first serial killer's murder castle",
        "The Zodiac Killer's unsolved ciphers — what they really say",
        "Ted Bundy — the charming monster who fooled everyone",
        "The Jonestown Massacre — how 900 people were led to their deaths",
        "The Manson Family murders — how Charles Manson controlled minds",
        "The real story of Ed Gein — the killer who inspired Psycho",
        "The Black Dahlia — Hollywood's most gruesome unsolved murder",
        "The Villisca Axe Murders — a family slaughtered in their sleep",
        "Albert Fish — the most disturbing serial killer in American history",
        "The Stanford Prison Experiment — when psychology turned dark",
        "Operation Paperclip — the US government's darkest secret",
        "Unit 731 — Japan's horrific secret biological warfare experiments",
        "The real story of Bloody Mary Tudor — England's darkest queen",
        "The Milgram Experiment — how ordinary people commit evil acts",
        "The dark history of lobotomies — when doctors drilled into brains",
        "Project MKUltra — the CIA's mind control experiments exposed",
        "The Tuskegee Syphilis Study — America's most shameful experiment",
        "The Radium Girls — the workers who glowed and died",
        "The Dancing Plague of 1518 — mass hysteria that killed dancers",
        "The Axeman of New Orleans — the jazz-loving serial killer",
        "The Nithari killings — India's most disturbing serial murder case",
        "The real story of Vlad the Impaler — Dracula's inspiration",
        "The Enfield Horror — the Illinois creature that terrorized a town",
        "The West Memphis Three — the Satanic panic that imprisoned innocents",
    ],
}

USED_TOPICS_FILE = "dark_used_topics.json"

# ============================================================
# 🧠 GROQ AI — Blog Writer
# ============================================================

def generate_blog_post(topic: str, category: str) -> dict:
    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""Write a dark, gripping, spine-chilling blog post about: "{topic}"
Category: {category}

Requirements:
- Write like a master horror storyteller — gripping, atmospheric, creepy
- Length: 700-900 words
- Open with a terrifying hook that immediately creates dread
- Build suspense throughout — keep reader hooked
- Include real facts, dates, names where relevant
- Use vivid descriptions that paint dark imagery
- Include the most shocking or disturbing details
- End with an unsettling conclusion or open question

Return ONLY a JSON object (no markdown, no extra text):
{{
  "title": "dark, chilling, curiosity-driving title",
  "content": "full post in HTML using <h2>, <p>, <ul>, <li> tags",
  "meta_description": "dark SEO description under 155 characters",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=2000
    )

    import re
    response_text = response.choices[0].message.content.strip()

    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    response_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', response_text)

    try:
        blog_data = json.loads(response_text)
    except json.JSONDecodeError:
        simple = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f'Write dark blog about "{topic}". ONLY JSON: {{"title":"t","content":"<p>c</p>","meta_description":"d","tags":["t1","t2","t3"]}}'}],
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
# 🎨 DARK SPOOKY STYLING
# ============================================================

CATEGORY_STYLES = {
    "Ghost Stories & Hauntings":        {"bg": "#0a0a0a", "accent": "#ff4444", "badge": "#ff6666", "text": "#ffcccc", "emoji": "👻"},
    "Dark Rituals & Occult":            {"bg": "#0d0010", "accent": "#cc00ff", "badge": "#dd44ff", "text": "#f5ccff", "emoji": "🕯️"},
    "Unsolved Mysteries & Conspiracies":{"bg": "#000a14", "accent": "#ff8800", "badge": "#ffaa33", "text": "#fff0cc", "emoji": "🔍"},
    "Paranormal & Supernatural":        {"bg": "#000d0a", "accent": "#00ff88", "badge": "#33ffaa", "text": "#ccffe8", "emoji": "👁️"},
    "Cursed Objects & Places":          {"bg": "#0f0000", "accent": "#ff2200", "badge": "#ff5533", "text": "#ffd0cc", "emoji": "💀"},
    "Urban Legends & Folklore":         {"bg": "#0a0800", "accent": "#ffcc00", "badge": "#ffdd44", "text": "#fff8cc", "emoji": "🐺"},
    "True Crime & Dark History":        {"bg": "#080808", "accent": "#ff3366", "badge": "#ff6688", "text": "#ffccdd", "emoji": "🩸"},
}


def get_style(category: str) -> dict:
    return CATEGORY_STYLES.get(category, {"bg": "#0a0a0a", "accent": "#ff4444", "badge": "#ff6666", "text": "#ffcccc", "emoji": "👻"})


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
        "Ghost Stories & Hauntings": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Winchester_Mystery_House.jpg/800px-Winchester_Mystery_House.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Alcatraz_Island_photo_D_Ramey_Logan.jpg/800px-Alcatraz_Island_photo_D_Ramey_Logan.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Eastern_State_Penitentiary_main_entrance.jpg/800px-Eastern_State_Penitentiary_main_entrance.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Edinburghs_underground_vaults.jpg/800px-Edinburghs_underground_vaults.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Highgate_Cemetery_-_geograph.org.uk_-_1070814.jpg/800px-Highgate_Cemetery_-_geograph.org.uk_-_1070814.jpg",
        ],
        "Dark Rituals & Occult": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Candles_and_a_skull.jpg/800px-Candles_and_a_skull.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Altar_of_Mysteries_Pompeii.jpg/800px-Altar_of_Mysteries_Pompeii.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Stonehenge2007_07_30.jpg/800px-Stonehenge2007_07_30.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat_03.jpg/800px-Cat_03.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Codex_Gigas_devil.jpg/400px-Codex_Gigas_devil.jpg",
        ],
        "Unsolved Mysteries & Conspiracies": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/400px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Voynich_Manuscript_%28166%29.jpg/800px-Voynich_Manuscript_%28166%29.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Nazca_monkey.jpg/800px-Nazca_monkey.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/The_Bermuda_Triangle.jpg/800px-The_Bermuda_Triangle.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Stonehenge_at_dusk.jpg/800px-Stonehenge_at_dusk.jpg",
        ],
        "Paranormal & Supernatural": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Edinburghs_underground_vaults.jpg/800px-Edinburghs_underground_vaults.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Abandoned_house.jpg/800px-Abandoned_house.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Highgate_Cemetery_-_geograph.org.uk_-_1070814.jpg/800px-Highgate_Cemetery_-_geograph.org.uk_-_1070814.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Stonehenge2007_07_30.jpg/800px-Stonehenge2007_07_30.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Alcatraz_Island_photo_D_Ramey_Logan.jpg/800px-Alcatraz_Island_photo_D_Ramey_Logan.jpg",
        ],
        "Cursed Objects & Places": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Hope_Diamond.jpg/400px-Hope_Diamond.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Tutankhamun_Egyptian_Museum.jpg/400px-Tutankhamun_Egyptian_Museum.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Koh-i-Noor_replica.jpg/400px-Koh-i-Noor_replica.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Eastern_State_Penitentiary_main_entrance.jpg/800px-Eastern_State_Penitentiary_main_entrance.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Winchester_Mystery_House.jpg/800px-Winchester_Mystery_House.jpg",
        ],
        "Urban Legends & Folklore": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Stonehenge_at_dusk.jpg/800px-Stonehenge_at_dusk.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Stonehenge2007_07_30.jpg/800px-Stonehenge2007_07_30.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Nazca_monkey.jpg/800px-Nazca_monkey.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Voynich_Manuscript_%28166%29.jpg/800px-Voynich_Manuscript_%28166%29.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Abandoned_house.jpg/800px-Abandoned_house.jpg",
        ],
        "True Crime & Dark History": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Eastern_State_Penitentiary_main_entrance.jpg/800px-Eastern_State_Penitentiary_main_entrance.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Alcatraz_Island_photo_D_Ramey_Logan.jpg/800px-Alcatraz_Island_photo_D_Ramey_Logan.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Edinburghs_underground_vaults.jpg/800px-Edinburghs_underground_vaults.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Codex_Gigas_devil.jpg/400px-Codex_Gigas_devil.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Highgate_Cemetery_-_geograph.org.uk_-_1070814.jpg/800px-Highgate_Cemetery_-_geograph.org.uk_-_1070814.jpg",
        ],
    }
    default_pool = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Stonehenge2007_07_30.jpg/800px-Stonehenge2007_07_30.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Stonehenge_at_dusk.jpg/800px-Stonehenge_at_dusk.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Abandoned_house.jpg/800px-Abandoned_house.jpg",
    ]
    pool = IMAGE_POOL.get(category, default_pool)
    # Use topic hash so same topic always gets same image
    idx = abs(hash(topic)) % len(pool)
    raw_url = pool[idx]
    # Wrap with wsrv.nl proxy — bypasses hotlink protection, works from any domain
    import urllib.parse
    return f"https://wsrv.nl/?url={urllib.parse.quote(raw_url, safe='')}&w=800&h=400&fit=cover&output=jpg"


def publish_to_blogger(blog_data: dict) -> str:
    service = get_blogger_service()
    style   = get_style(blog_data["category"])
    img_url = get_topic_image(blog_data["topic"], blog_data["category"])
    IST     = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    now_str = datetime.datetime.now(IST).strftime("%B %d, %Y")

    full_content = f"""
<div style="font-family:'Segoe UI',Georgia,serif; max-width:860px; margin:0 auto; background:#111; color:#e0e0e0; line-height:1.85; border-radius:14px; overflow:hidden;">

  <!-- HERO IMAGE -->
  <div style="position:relative; overflow:hidden; margin-bottom:0;">
    <img src="{img_url}" alt="{blog_data['topic']}" style="width:100%; height:380px; object-fit:cover; display:block; filter:grayscale(40%) contrast(120%) brightness(60%);"/>
    <div style="position:absolute; inset:0; background:linear-gradient(to top, #000000f5 0%, transparent 50%);"></div>
    <div style="position:absolute; bottom:0; left:0; right:0; padding:28px;">
      <span style="background:{style['accent']}; color:#000; padding:5px 16px; border-radius:4px; font-size:12px; font-weight:900; letter-spacing:2px; text-transform:uppercase;">
        {style['emoji']} {blog_data['category']}
      </span>
      <p style="color:rgba(255,255,255,0.7); font-size:13px; margin:10px 0 0;">🕐 {now_str}</p>
    </div>
  </div>

  <!-- CONTENT -->
  <div style="background:#111111; padding:40px 36px;">

    <!-- Category badge -->
    <div style="display:inline-flex; align-items:center; gap:8px; background:{style['bg']}; border:1px solid {style['accent']}; border-radius:4px; padding:8px 16px; margin-bottom:28px;">
      <span style="width:8px; height:8px; border-radius:50%; background:{style['accent']}; display:inline-block; box-shadow:0 0 8px {style['accent']};"></span>
      <span style="color:{style['badge']}; font-size:13px; font-weight:700; letter-spacing:1px;">{blog_data['category'].upper()}</span>
    </div>

    <!-- Blog content -->
    <div style="color:#cccccc; font-size:17px; line-height:1.9;">
      <style scoped>
        h2 {{ color:{style['accent']}; font-size:22px; font-weight:800; margin:32px 0 12px; padding-left:14px; border-left:4px solid {style['accent']}; text-shadow:0 0 10px {style['accent']}44; }}
        p {{ margin:0 0 18px; color:#cccccc; }}
        ul,ol {{ padding-left:24px; margin-bottom:18px; }}
        li {{ margin-bottom:8px; color:#cccccc; }}
        strong {{ color:{style['badge']}; }}
      </style>
      {blog_data['content']}
    </div>

    <!-- Divider -->
    <div style="height:1px; background:linear-gradient(to right, transparent, {style['accent']}, transparent); margin:32px 0;"></div>

    <!-- Tags -->
    <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:28px;">
      {''.join([f'<span style="background:{style["bg"]}; color:{style["badge"]}; border:1px solid {style["accent"]}; padding:4px 14px; border-radius:4px; font-size:13px; font-weight:600;">#{tag}</span>' for tag in blog_data.get("tags",[])])}
    </div>

    <!-- Footer -->
    <div style="background:{style['bg']}; border:1px solid {style['accent']}44; border-radius:8px; padding:20px 24px; display:flex; align-items:center; justify-content:space-between;">
      <div>
        <p style="color:{style['badge']}; font-size:13px; margin:0 0 4px; font-weight:700;">Published by MYRQ</p>
        <p style="color:#666; font-size:12px; margin:0;">{now_str} • {blog_data['category']}</p>
      </div>
      <span style="font-size:28px;">{style['emoji']}</span>
    </div>

  </div>
</div>
"""

    post   = {"title": blog_data["title"], "content": full_content, "labels": blog_data.get("tags",[]) + [blog_data["category"]]}
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
# 🚀 MAIN
# ============================================================

def write_and_publish():
    IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    now = datetime.datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*55}")
    print(f"⏰  {now}")
    print(f"{'='*55}")

    try:
        topic, category = get_next_topic()
        print(f"👻  Topic    : {topic}")
        print(f"📂  Category : {category}")

        print("✍️   Writing with Groq AI...")
        blog_data = generate_blog_post(topic, category)
        print(f"✅  Written  : {blog_data['title']}")

        print("📤  Publishing to Blogger...")
        url = publish_to_blogger(blog_data)
        print(f"🎉  Published: {url}")

        logs = []
        if os.path.exists("dark_blog_log.json"):
            with open("dark_blog_log.json") as f:
                logs = json.load(f)
        logs.append({"time": now, "title": blog_data["title"], "category": category, "url": url})
        with open("dark_blog_log.json", "w") as f:
            json.dump(logs, f, indent=2)
        print(f"📊  Total posts: {len(logs)}")

    except KeyboardInterrupt:
        raise
    except Exception as e:
        import traceback
        print(f"❌  Error: {e}")
        print(traceback.format_exc())
        print("⏳  Retrying next time...")


# ============================================================
# ▶️  START
# ============================================================

if __name__ == "__main__":
    print("=" * 55)
    print("👻  DARK MYSTERIES BLOG WRITER")
    print("    Powered by Groq AI — Published by MYRQ")
    print("=" * 55)

    if "--once" in sys.argv:
        print("☁️   GitHub Actions mode\n")
        print(f"🔑  Using Blog ID: {BLOGGER_BLOG_ID}")
        write_and_publish()
    else:
        print(f"📅  Posting every {POST_EVERY_MINUTES} minutes (48/day)")
        print("🛑  Press Ctrl+C to stop\n")
        write_and_publish()
        schedule.every(POST_EVERY_MINUTES).minutes.do(write_and_publish)
        while True:
            try:
                schedule.run_pending()
            except Exception as e:
                print(f"⚠️  Scheduler error (continuing): {e}")
            time.sleep(1)
