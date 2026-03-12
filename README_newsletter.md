# 📧 Auto Newsletter Writer — Complete Setup Guide

> Automatically writes and sends beautiful long-form newsletters twice a day (Morning + Evening) using FREE Groq AI + Mailchimp. Zero cost forever.

---

## 📁 Files in This Project

| File | Purpose |
|---|---|
| `auto_newsletter_FREE.py` | Main Python script — writes and sends newsletters |
| `.github/workflows/auto_newsletter.yml` | GitHub Actions schedule — runs twice daily |
| `newsletter_used_topics.json` | Tracks used topics so nothing repeats |
| `newsletter_log.json` | Log of every newsletter sent |

---

## 🧠 How It Works

```
8:00 AM IST (GitHub Actions wakes up)
        ↓
Picks a random unused MORNING topic
        ↓
Groq AI (Llama 3.3 70B) writes 1000-1200 word newsletter
        ↓
Wrapped in beautiful HTML email template (Orange theme)
        ↓
Mailchimp creates campaign → sends to all subscribers
        ↓
Log saved to newsletter_log.json
        ↓
Sleeps until 7:00 PM IST

7:00 PM IST (GitHub Actions wakes up again)
        ↓
Picks a random unused EVENING topic
        ↓
Groq AI writes 1000-1200 word newsletter
        ↓
Wrapped in beautiful HTML email template (Purple theme)
        ↓
Mailchimp creates campaign → sends to all subscribers
        ↓
Log saved → sleeps until 8:00 AM next day
```

---

## 🛠️ Full Setup — Step by Step

### Step 1 — Get FREE Groq API Key
1. Go to https://console.groq.com
2. Sign up with Google (free, no credit card)
3. Click **API Keys** → **Create API Key**
4. Copy the key (starts with `gsk_...`)

---

### Step 2 — Create FREE Mailchimp Account
1. Go to https://mailchimp.com
2. Click **Sign Up Free**
3. Register with your Gmail
4. Complete setup — Business name: `Daily Tips World`

---

### Step 3 — Get 4 things from Mailchimp

#### API Key:
1. Click your profile (top right) → **Account & Billing**
2. Go to **Extras** → **API Keys**
3. Click **"Create A Key"**
4. Copy the key

#### Server Prefix:
1. Look at your Mailchimp URL when logged in
2. Example: `https://us21.admin.mailchimp.com`
3. Your prefix = `us21` (just the `usXX` part)

#### Audience ID:
1. Click **Audience** in left menu
2. Click **Audience dashboard**
3. Click **`...`** (three dots) → **Settings**
4. Scroll down → copy the **Audience ID**

#### Verified From Email:
- Use the Gmail you signed up with
- Mailchimp auto-verifies it during signup

---

### Step 4 — Add yourself as first subscriber
1. Mailchimp → **Audience** → **Add contacts** → **Copy and paste**
2. Type your Gmail address
3. Complete the import steps
4. Now you'll receive every newsletter as a test!

---

### Step 5 — Fill in the script settings

Open `auto_newsletter_FREE.py` and fill in these 6 lines:

```python
GROQ_API_KEY        = "gsk_...your groq key here..."
MAILCHIMP_API_KEY   = "...your mailchimp api key here..."
MAILCHIMP_SERVER    = "us21"                          # your usXX prefix
MAILCHIMP_LIST_ID   = "...your audience id here..."
FROM_NAME           = "Daily Tips World"              # your newsletter name
FROM_EMAIL          = "your_email@gmail.com"          # your verified email
```

---

### Step 6 — Install libraries & test locally

```bash
pip install groq mailchimp-marketing schedule

# Test morning edition
python auto_newsletter_FREE.py --morning

# Test evening edition
python auto_newsletter_FREE.py --evening
```

Check your inbox in 5-10 minutes — newsletter should arrive! ✅

---

### Step 7 — Deploy to GitHub Actions (runs 24/7 free)

#### Create/use existing GitHub Repository
- Use your existing `autoblog` repo OR create new one named `newsletter`
- Keep it **Private** to protect your API keys

#### Upload Files
- `auto_newsletter_FREE.py` → repo root
- `auto_newsletter.yml` → `.github/workflows/`

#### Add GitHub Secrets
Go to repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 4 secrets:

| Secret Name | Value |
|---|---|
| `GROQ_API_KEY` | your `gsk_...` Groq key |
| `MAILCHIMP_API_KEY` | your Mailchimp API key |
| `MAILCHIMP_SERVER` | e.g. `us21` |
| `MAILCHIMP_LIST_ID` | your Audience ID |

#### Test on GitHub
1. Go to **Actions** tab
2. Click **"Auto Newsletter Sender"**
3. Click **"Run workflow"**
4. Select edition: `morning` or `evening`
5. Click **"Run workflow"**
6. Wait ~25 seconds → should show green ✅

---

## ⚙️ Configuration

```python
GROQ_API_KEY        = "gsk_..."       # From console.groq.com
MAILCHIMP_API_KEY   = "..."           # From Mailchimp account
MAILCHIMP_SERVER    = "us21"          # From your Mailchimp URL
MAILCHIMP_LIST_ID   = "..."           # From Mailchimp Audience settings
FROM_NAME           = "Daily Tips World"
FROM_EMAIL          = "your@gmail.com"
```

---

## 📚 Newsletter Topics (8 Categories, 40 Topics)

### 🌅 Morning Topics (energy + productivity):
| Category | Sample Topics |
|---|---|
| Technology & AI | AI transforming jobs, free AI tools, future of work... |
| Money & Finance | Money habits, investing ₹1000, passive income... |
| Motivational & Life Tips | Morning routines, unstoppable confidence, success... |
| Education & Self Improvement | Learn faster, top skills 2026, read 52 books/year... |

### 🌙 Evening Topics (relax + reflect):
| Category | Sample Topics |
|---|---|
| Health & Fitness | Better sleep, evening workout, reduce anxiety... |
| Food & Cooking | Quick dinner recipes, healthy Indian dinner... |
| Travel & Adventure | Hyderabad getaways, budget vacation, hidden India gems... |
| Motivational & Life Tips | Evening reflection, journaling, gratitude habits... |

> Topics rotate automatically — never repeats until all are used, then resets

---

## 🎨 Newsletter Design

### Morning Edition 🌅
- **Header color**: Orange gradient (`#f97316` → `#fb923c`)
- **Tone**: Energetic, motivating, action-oriented
- **Greeting**: "Good Morning ☀️"

### Evening Edition 🌙
- **Header color**: Purple gradient (`#4f46e5` → `#7c3aed`)
- **Tone**: Calm, reflective, wind-down friendly
- **Greeting**: "Good Evening 🌙"

### Each newsletter includes:
- 🎨 Beautiful color-coded header with edition label + date
- 📖 Real story or hook at the beginning
- 📝 3-4 main sections with bold headers
- 💡 Practical actionable tips throughout
- 🎯 **"Today's Challenge"** — one small action box
- 💬 **"Quote of the Day"** — motivating quote
- 📬 Professional footer with unsubscribe note

---

## ⏰ Schedule

| Edition | Time (IST) | Time (UTC) | Cron |
|---|---|---|---|
| 🌅 Morning | 8:00 AM | 2:30 AM | `30 2 * * *` |
| 🌙 Evening | 7:00 PM | 1:30 PM | `30 13 * * *` |

---

## 💰 Free Tier Limits — You Are Safe!

| Service | Your Daily Usage | Free Limit | Usage % |
|---|---|---|---|
| Groq AI | 2 requests/day | 14,400/day | 0.01% ✅ |
| Mailchimp campaigns | 2/day | 1,000/month | 6%/month ✅ |
| Mailchimp emails | 2 × subscribers | 500 subs free | ✅ |
| GitHub Actions | 2 runs/day | 2,000/day | 0.1% ✅ |

**Total monthly cost = ₹0** 🎉

---

## 🔧 Common Errors & Fixes

### `Invalid control character` JSON error
- Groq returned HTML with special characters inside JSON
- Fixed by: adding regex cleanup + retry with simpler prompt
- Script automatically retries — you'll see `⚠️ JSON parse failed, retrying...`

### Email not received
1. **Check Spam/Junk folder first** — Gmail may filter new senders
2. If in spam → click **"Not spam"** → fixed permanently
3. Check Mailchimp → Campaigns → verify status is **"Sent"** not **"Draft"**
4. Mailchimp may show **"Sending"** for 5-10 minutes before delivery

### `ApiClientError` from Mailchimp
- Wrong API key or server prefix
- Double check `MAILCHIMP_SERVER` matches your Mailchimp URL (e.g. `us21`)

### Second email not received (when testing locally)
- Normal behavior — Mailchimp deduplicates sends to same subscriber in short time
- Real subscribers will always receive every newsletter
- Not an issue in production

### GitHub Actions environment variables not loading
- Make sure all 4 secrets are added: `GROQ_API_KEY`, `MAILCHIMP_API_KEY`, `MAILCHIMP_SERVER`, `MAILCHIMP_LIST_ID`
- Script reads them via `os.environ` automatically in `--morning` / `--evening` mode

---

## 💰 How to Monetize Your Newsletter

### Stage 1 — Build your audience (0-500 subscribers)
- Share subscribe link on WhatsApp groups
- Post on Facebook, Instagram, LinkedIn
- Add subscribe form to your Blogger blog
- Ask friends and family to subscribe
- **Goal: 500 subscribers in 3 months**

### Stage 2 — Affiliate marketing (500+ subscribers)
- Add Amazon affiliate links to relevant newsletters
- Finance newsletter → link to finance books
- Health newsletter → link to fitness products
- Each purchase = commission for you
- **Earning: ₹2,000-10,000/month**

### Stage 3 — Sponsorships (1000+ subscribers)
- Brands pay to be mentioned in your newsletter
- Typical rate: ₹500-2000 per 1000 subscribers per email
- With 1000 subscribers → ₹500-2000 per sponsored email
- **Earning: ₹10,000-50,000/month**

### Stage 4 — Paid subscriptions (5000+ subscribers)
- Offer premium content for ₹99-299/month
- Even 1% conversion = 50 paid subscribers
- 50 × ₹199 = ₹9,950/month extra
- **Earning: ₹10,000-50,000/month extra**

---

## 📈 Growth Projection

| Time | Subscribers | Monthly Earning |
|---|---|---|
| Month 1 | 50-100 | ₹0 (building) |
| Month 3 | 200-500 | ₹1,000-5,000 |
| Month 6 | 500-1,500 | ₹5,000-20,000 |
| Month 12 | 2,000-5,000 | ₹20,000-1,00,000 |

---

## 📞 Tech Stack Summary

| Component | Tool | Cost |
|---|---|---|
| AI Writing | Groq (Llama 3.3 70B) | FREE |
| Email Platform | Mailchimp | FREE (up to 500 subs) |
| Scheduling | GitHub Actions | FREE |
| **Total** | | **₹0/month** |

---

## 🚀 How to Grow Subscribers Fast

1. **Add subscribe form to your blog** — blog readers become newsletter subscribers
2. **WhatsApp broadcast** — share every newsletter with your contacts
3. **Instagram/Facebook** — post newsletter highlights, link to subscribe
4. **Referral program** — ask subscribers to share with friends
5. **Cross-promote** — mention newsletter in your blog posts

---

## 🔗 Related Projects
- `auto_blog_writer_FREE.py` — Auto blog writer (24 posts/day to Blogger)
- `README.md` — Full setup guide for the blog automation

---

*Built with ❤️ using Claude AI — March 2026*
