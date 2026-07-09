"""
AI Lead Qualification Bot
- Integrates Telegram Bot API (Task 2 - REST API/webhook)
- Uses Google Gemini free tier as the AI agent (Task 4 - AI chatbot/agent)
- Extracts structured lead data (name, need, budget, timeline) via Gemini JSON mode
- Pushes "Hot" leads to an n8n webhook (Task 1 - automation trigger)
"""
import os
import json
import logging
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

import db

load_dotenv()
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/hot-lead")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")  # free-tier friendly model

SYSTEM_PROMPT = """You are a friendly sales qualification assistant for an AI automation agency.
Your job: chat naturally with the lead, and try to learn their (1) name, (2) automation need,
(3) budget, (4) timeline. Ask ONE question at a time, don't overwhelm them.

After each user message, respond with ONLY valid JSON, no markdown, in this exact shape:
{
  "reply": "your conversational reply to send back to the user",
  "extracted": {"name": null or string, "need": null or string, "budget": null or string, "timeline": null or string},
  "score": "Hot" | "Warm" | "Cold" | "Unqualified"
}
Scoring rule: Hot = budget + timeline + clear need all known. Warm = 2 of 3 known. Cold = vague/no budget.
"""


def ask_gemini(chat_id: str, user_message: str) -> dict:
    history = db.get_messages(chat_id)
    convo = "\n".join(f"{m['sender']}: {m['message']}" for m in history[-10:])
    prompt = f"{SYSTEM_PROMPT}\n\nConversation so far:\n{convo}\nuser: {user_message}\n\nJSON response:"

    response = model.generate_content(prompt)
    text = response.text.strip()
    logging.info(f"RAW GEMINI RESPONSE: {text}")  # DEBUG LINE - remove later

    # Strip markdown code fences if Gemini wraps the JSON in them
    if text.startswith("```"):
        text = text.split("```")[1]
        text = text.replace("json", "", 1).strip() if text.lower().startswith("json") else text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logging.warning(f"JSON parse failed: {e}")
        return {"reply": "Could you tell me a bit more about what you need?", "extracted": {}, "score": "Unqualified"}


def notify_n8n(chat_id, lead_data):
    try:
        requests.post(N8N_WEBHOOK_URL, json={"chat_id": chat_id, **lead_data}, timeout=5)
    except requests.RequestException as e:
        logging.warning(f"n8n webhook not reachable: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user_message = update.message.text

    db.log_message(chat_id, "user", user_message)
    result = ask_gemini(chat_id, user_message)

    extracted = result.get("extracted", {})
    score = result.get("score", "Unqualified")
    db.upsert_lead(
        chat_id,
        name=extracted.get("name"),
        need=extracted.get("need"),
        budget=extracted.get("budget"),
        timeline=extracted.get("timeline"),
        score=score,
    )

    reply = result.get("reply", "Thanks! Tell me more about your project.")
    db.log_message(chat_id, "bot", reply)
    await update.message.reply_text(reply)

    if score == "Hot":
        notify_n8n(chat_id, extracted)


def main():
    db.init_db()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logging.info("Bot running... Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()