# 🤖 Auto Blog Writer — Complete Setup Guide

> Automatically writes and publishes blog posts every hour using FREE AI (Groq) to Blogger.com, hosted on GitHub Actions. Zero cost forever.

---

## 📁 Files in This Project

| File | Purpose |
|---|---|
| `auto_blog_writer_FREE.py` | Main Python script — writes and publishes blogs |
| `credentials.json` | Google OAuth credentials (never commit this publicly!) |
| `token.json` | Google auth token — auto generated on first run |
| `used_topics.json` | Tracks used topics so nothing repeats |
| `blog_log.json` | Log of every post published |
| `.github/workflows/auto_blog.yml` | GitHub Actions schedule — runs every hour |

---

## 🧠 How It Works

```
Every Hour (GitHub Actions)
        ↓
Picks a random unused topic from 7 categories
        ↓
Groq AI (Llama 3.3 70B) writes a 600-800 word blog post
        ↓
Fetches a beautiful free image from Picsum Photos
        ↓
Applies color theme based on category
        ↓
Publishes to Blogger.com via Google Blogger API
        ↓
Saves log entry to blog_log.json
        ↓
Sleeps until next hour
```

---

## 🛠️ Full Setup — Step by Step

### Step 1 — Get FREE Groq API Key
1. Go to https://console.groq.com
2. Sign up with Google (free)
3. Click **API Keys** → **Create API Key**
4. Copy the key (starts with `gsk_...`)
5. Add it to the script: `GROQ_API_KEY = "gsk_..."`

---

### Step 2 — Create Blogger Blog
1. Go to https://www.blogger.com
2. Sign in with Google account
3. Click **Create New Blog**
4. Give it a name (e.g. *Daily Tips World*)
5. Choose a free URL (e.g. *dailytipsworld.blogspot.com*)
6. Click **Create**
7. Copy the Blog ID from the dashboard URL:
   - URL looks like: `blogger.com/blog/posts/1234567890`
   - The number at the end is your **Blog ID**
8. Add it to the script: `BLOGGER_BLOG_ID = "1234567890"`

---

### Step 3 — Enable Blogger API on Google Cloud

1. Go to https://console.cloud.google.com
2. Create a new project — name it `AutoBlog`
3. Go directly to this URL to enable Blogger API:
   ```
   https://console.cloud.google.com/apis/library/blogger.googleapis.com
   ```
4. Click **Enable**

---

### Step 4 — Set Up OAuth Credentials

1. In Google Cloud Console → **APIs & Services** → **OAuth consent screen**
   - Click **Audience** on the left
   - Select **External** → Click **Next**
2. Click **Clients** on the left → **Create client**
   - Application type: **Desktop App**
   - Name: `AutoBlog`
   - Click **Create**
3. Click on **AutoBlog** client → **Download JSON**
4. Rename downloaded file to: `credentials.json`
5. Place `credentials.json` in the same folder as the Python script

---

### Step 5 — Add Yourself as Test User
1. Google Cloud Console → **APIs & Services** → **OAuth consent screen**
2. Click **Audience** → scroll to **Test users**
3. Click **+ Add Users**
4. Add your Gmail address
5. Click **Save**

> ⚠️ Without this step you get "Access blocked: AutoBlog has not completed verification" error

---

### Step 6 — Run Locally First (One Time Only)
This generates the `token.json` file needed for GitHub Actions.

```bash
# Install dependencies
pip install groq google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client schedule

# Run the script
python auto_blog_writer_FREE.py
```

- A browser window will open automatically
- Login with your Google account
- Click **Allow**
- Script will write and publish your first blog post!
- A `token.json` file is created — you need this for GitHub

---

### Step 7 — Set Up GitHub Actions (Run 24/7 Free)

#### Create GitHub Repository
1. Go to https://github.com/new
2. Name: `autoblog`
3. Select **Private** (keeps your keys safe)
4. Click **Create repository**

#### Upload Files
Upload these to the repo root:
- `auto_blog_writer_FREE.py`

Create this file at `.github/workflows/auto_blog.yml`:
- Upload `auto_blog.yml`

#### Add GitHub Secrets
Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 4 secrets:

| Secret Name | Where to get it |
|---|---|
| `GROQ_API_KEY` | From https://console.groq.com |
| `BLOGGER_BLOG_ID` | From your Blogger dashboard URL |
| `GOOGLE_TOKEN` | Run `type token.json` in PowerShell, copy everything |
| `GOOGLE_CREDENTIALS` | Run `type credentials.json` in PowerShell, copy everything |

#### Trigger First Run
1. Go to **Actions** tab in GitHub
2. Click **Auto Blog Writer**
3. Click **Run workflow** → **Run workflow**
4. Wait ~30 seconds → should show green ✅

---

## ⚙️ Configuration

Open `auto_blog_writer_FREE.py` and edit these at the top:

```python
GROQ_API_KEY    = "gsk_your_key_here"       # From console.groq.com
BLOGGER_BLOG_ID = "your_blog_id_here"        # From Blogger dashboard URL
POST_EVERY_MINUTES = 60                       # Change to 30 for every 30 mins
```

---

## 📚 Blog Topics (7 Categories, 70 Topics)

| Category | Topics |
|---|---|
| Technology & AI | AI tools, cybersecurity, smartphones, coding apps... |
| Health & Fitness | Workouts, sleep, stress, nutrition, immunity... |
| Money & Finance | Saving, investing, passive income, budgeting... |
| Motivational & Life Tips | Habits, goals, confidence, productivity... |
| Food & Cooking | Quick meals, meal prep, recipes, coffee... |
| Travel & Adventure | Budget travel, Hyderabad, Goa, packing tips... |
| Education & Self Improvement | Online courses, resume, job interviews, English... |

> Topics rotate automatically and never repeat until all are used. Then they reset.

---

## 🎨 Blog Post Design

Each post includes:
- **Hero image** — random beautiful photo from Picsum Photos (free)
- **Color theme** — unique per category:
  - Technology = Dark purple (`#0f172a` / `#6366f1`)
  - Health = Dark green (`#052e16` / `#22c55e`)
  - Money = Dark gold (`#1c1917` / `#f59e0b`)
  - Motivation = Dark pink (`#4a044e` / `#e879f9`)
  - Food = Dark orange (`#431407` / `#f97316`)
  - Travel = Dark blue (`#0c4a6e` / `#38bdf8`)
  - Education = Dark violet (`#1e1b4b` / `#a78bfa`)
- **Category badge** with accent color
- **Styled headings** with left border accent
- **Hashtag pills** for tags
- **Styled footer** with publish date

---

## 💰 Free Tier Limits — You Are Safe!

| Service | Your Daily Usage | Free Limit | Usage % |
|---|---|---|---|
| Groq AI | 24 requests | 14,400/day | 0.16% ✅ |
| Blogger API | 24 requests | 750/day | 3.2% ✅ |
| GitHub Actions | 24 runs | 2,000/day | 1.2% ✅ |
| Picsum Images | 24 requests | Unlimited | 0% ✅ |

**Total monthly cost = ₹0** 🎉

---

## 🔧 Common Errors & Fixes

### `ModuleNotFoundError: No module named 'groq'`
```bash
pip install groq
```

### `ModuleNotFoundError: No module named 'schedule'`
```bash
pip install schedule
```

### `400 API key not valid`
- Wrong API key in script
- Go to https://aistudio.google.com/app/apikey and copy fresh key

### `429 RESOURCE_EXHAUSTED` (Gemini)
- Switched to Groq instead — Groq has much higher free limits

### `403 access_denied — AutoBlog has not completed verification`
- Add your Gmail as a test user in Google Cloud Console
- Go to: APIs & Services → OAuth consent screen → Audience → Test users

### `404 models/gemini-1.5-flash is not found`
- Old model name — updated to `gemini-2.0-flash-lite` then switched to Groq

### Image not loading in blog
- `source.unsplash.com` is shut down
- Fixed by switching to `picsum.photos` which always works

---

## 📈 Expected Blog Growth

| Time | Posts Published | Expected Daily Visitors |
|---|---|---|
| Day 1 | 24 | 0-5 |
| Week 1 | 168 | 10-50 |
| Month 1 | 720 | 100-500 |
| Month 3 | 2,160 | 500-2,000 |
| Month 6 | 4,320 | 2,000-5,000 |

---

## 💵 How to Monetize

### Google AdSense (Main Income)
1. Go to https://www.google.com/adsense
2. Sign in → Click **Get started**
3. Enter your Blogger blog URL
4. Submit for approval (takes 1-2 weeks)
5. Once approved → ads appear automatically → you earn per visitor

### Affiliate Marketing (Bonus Income)
- Add Amazon affiliate links to relevant posts
- Finance posts → link to books, courses
- Fitness posts → link to equipment
- Each purchase = commission for you

---

## 🚀 Future Ideas to Scale Up

- [ ] Create 5 blogs on different niches (5x income)
- [ ] Auto-share posts to Twitter/Facebook
- [ ] Add Amazon affiliate links automatically
- [ ] Generate YouTube scripts from same topics
- [ ] Sell blog writing service to businesses (₹5,000-20,000/month per client)

---

## 📞 Tech Stack Summary

| Component | Tool | Cost |
|---|---|---|
| AI Writing | Groq (Llama 3.3 70B) | FREE |
| Blog Platform | Blogger.com | FREE |
| Hosting/Scheduling | GitHub Actions | FREE |
| Images | Picsum Photos | FREE |
| Blog API | Google Blogger API v3 | FREE |
| Auth | Google OAuth 2.0 | FREE |
| **Total** | | **₹0/month** |

---

*Built with ❤️ using Claude AI — March 2026*
