# AI Lead Qualification & Automation System

A complete AI automation project built to satisfy the I Vision Infotech technical test:
- **Task 1** – Custom AI Automation Workflow (n8n)
- **Task 2** – Third-Party API Integration (Telegram Bot API + Google Gemini API)
- **Task 3** – Custom Dashboard (Flask + Chart.js)
- **Task 4** – Real Client Automation Flow (AI lead-qualifying chatbot)
- **Task 5** – GitHub-ready repo

🔗 **Live Demo:** https://ai-lead-automation-ci1f.onrender.com

## Screenshots

**AI chatbot qualifying leads on Telegram (Gemini-powered):**

![Telegram bot conversation](screenshots/telegram-bot.png)

**Live dashboard — lead pipeline and scoring breakdown:**

![Dashboard](screenshots/dashboard.png)

**n8n automation workflow — auto-notifies on Hot leads:**

![n8n workflow](screenshots/n8n-workflow.png)

## What it does
1. A **Telegram bot** talks to potential customers (stand-in for a WhatsApp lead-gen bot — same architecture, easier to test without Meta business verification).
2. Every message is sent to **Google Gemini (free tier)**, which qualifies the lead (asks for name, need, budget, timeline) and scores them Hot / Warm / Cold.
3. Each conversation + lead score is saved to **SQLite**.
4. An **n8n workflow** watches for new "Hot" leads via a webhook and auto-notifies you (email/Slack/Sheet — configurable) — this is the automation layer a real client would pay for.
5. A **Flask dashboard** shows all leads, their scores, and conversation history in real time with charts.

---

## STEP-BY-STEP SETUP GUIDE

### Step 0: Prerequisites
```bash
python --version   # 3.9+
pip install -r requirements.txt
```

### Step 1: Get FREE API keys (5 minutes)

**A. Telegram Bot Token (100% free, instant)**
1. Open Telegram, search for `@BotFather`
2. Send `/newbot`, follow prompts, name your bot
3. Copy the token it gives you (looks like `123456:ABC-xyz`)

**B. Google Gemini API Key (free tier — 1500 requests/day)**
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google → "Create API Key"
3. Copy the key

### Step 2: Configure environment
Create a `.env` file in the project root:
```
TELEGRAM_BOT_TOKEN=your_telegram_token_here
GEMINI_API_KEY=your_gemini_key_here
N8N_WEBHOOK_URL=http://localhost:5678/webhook/hot-lead
```

### Step 3: Run the bot
```bash
python bot.py
```
Open Telegram, message your bot, e.g.:
> "Hi, I need an automation system for my e-commerce store, budget around $2000, need it in 3 weeks"

The bot will reply with a qualifying question, then log the lead + score to `leads.db`.

### Step 4: Run the dashboard
```bash
python app.py
```
Open http://localhost:5000 — you'll see:
- Total leads, Hot/Warm/Cold breakdown chart
- Full conversation log per lead
- Live refresh

### Step 5: Set up n8n workflow (Task 1 — the automation piece)
1. Install n8n free (no signup needed for local use):
   ```bash
   npx n8n
   ```
2. Open http://localhost:5678
3. Import `n8n/lead_notification_workflow.json` (File → Import from File)
4. This workflow: **Webhook Trigger → IF (score == Hot) → Send Email/Slack/Log**
5. Activate it. The bot automatically POSTs every "Hot" lead to this webhook (see `bot.py` → `notify_n8n()`).

### Step 6: Push to GitHub (Task 5)
```bash
cd ai-lead-automation
git init
git add .
echo ".env" >> .gitignore
echo "leads.db" >> .gitignore
git commit -m "AI Lead Qualification & Automation System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-lead-automation.git
git push -u origin main
```

---

## How this maps to the job's real responsibilities
- **AI Chatbots & AI Agents** → `bot.py` (Gemini-powered qualification agent)
- **REST API / Webhook integration** → Telegram Bot API (polling/webhook) + Gemini REST API + n8n webhook
- **Custom Dashboards** → `app.py` + `templates/dashboard.html`
- **Client automation flow** → n8n hot-lead notification pipeline
- **MySQL/MongoDB** → swap SQLite for MySQL by changing the connection string in `db.py` (schema is identical — noted in comments)

## Extending for WhatsApp (mention in your interview)
Same architecture — swap `bot.py`'s Telegram polling loop for Meta's WhatsApp Cloud API webhook receiver (Flask route `/webhook`, verify token + POST handler). Everything downstream (Gemini call, DB, n8n) stays identical. This is worth saying explicitly to the interviewer — it shows you understand the pattern, not just one API.
