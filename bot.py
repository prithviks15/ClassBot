import discord
import sqlite3
from google import genai
from google.genai import types
from datetime import date
from discord.ext import tasks
import datetime
from zoneinfo import ZoneInfo
import os
from dotenv import load_dotenv
load_dotenv()

gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are ClassBot, a helpful assistant on a high school
class Discord server. Be concise and casual. Today's date is {today}."""

# Database
db = sqlite3.connect("classbot.db")
db.execute("""
    CREATE TABLE IF NOT EXISTS deadlines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        due_date TEXT NOT NULL,
        description TEXT,
        added_by TEXT
    )
""")
db.commit()


# Tools
def add_deadline(subject: str, due_date: str, description: str) -> str:
    """Save a homework assignment, test, or deadline to the class database.

    Args:
        subject: school subject, e.g. "physics", "math"
        due_date: The due date in ISO format YYYY-MM-DD
        description: Short description, e.g. "test on chapters 5-6"
    """
    db.execute(
        "INSERT INTO deadlines (subject, due_date, description) VALUES (?, ?, ?)",
        (subject, due_date, description),
    )
    db.commit()
    return f"Saved: {subject} on {due_date} — {description}"


def get_deadlines(from_date: str, to_date: str) -> str:
    """Get all deadlines between two dates (inclusive), ISO format YYYY-MM-DD."""
    rows = db.execute(
        "SELECT subject, due_date, description FROM deadlines "
        "WHERE due_date BETWEEN ? AND ? ORDER BY due_date",
        (from_date, to_date),
    ).fetchall()

    if not rows:
        return "Nothing found in that range."

    return "\n".join(f"{d}: {s} — {desc}" for s, d, desc in rows)


async def summarize_channel(channel, limit=200):
    messages = []

    async for msg in channel.history(limit=limit):
        if not msg.author.bot:
            messages.append(f"{msg.author.display_name}: {msg.clean_content}")

    messages.reverse()  # oldest first
    transcript = "\n".join(messages)

    response = gemini.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"Summarize this Discord conversation in a few bullet points. "
                 f"Focus on decisions, homework mentions, and anything important:\n\n{transcript}",
    )

    return response.text


# Proactive reminders
REMINDER_TIME = datetime.time(hour=17, minute=48, tzinfo=ZoneInfo("America/New_York"))
ANNOUNCE_CHANNEL_ID = 1530342954420404236


@tasks.loop(time=REMINDER_TIME)
async def daily_reminder():
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    items = get_deadlines(tomorrow, tomorrow)

    if "Nothing found" not in items:
        channel = client.get_channel(ANNOUNCE_CHANNEL_ID)
        await channel.send(f"⏰ Heads up — tomorrow:\n{items}")


# Discord setup
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    daily_reminder.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if "what did i miss" in message.clean_content.lower():
        summary = await summarize_channel(message.channel)
        await message.channel.send(summary)
        return

    if client.user.mentioned_in(message):
        user_message = message.clean_content
        today = date.today().isoformat()

        async with message.channel.typing():
            response = gemini.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT.format(today=today),
                    tools=[add_deadline, get_deadlines],
                ),
            )

        await message.channel.send(response.text)


client.run(os.getenv("DISCORD_TOKEN"))