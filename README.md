# ClassBot
AI-powered Discord assistant built for a high school class server using Python, Google Gemini, and SQLite. ClassBot uses natural-language AI to manage homework and deadlines, summarize recent conversations, answer class questions, and send proactive reminders, combining LLM function calling with persistent database storage.
readme = """# ClassBot 🤖

ClassBot is an AI-powered Discord assistant built for a high school class server. It uses Python, Google Gemini, and SQLite to help students keep track of deadlines, catch up on missed conversations, and stay informed through automatic reminders.

## Features

### 📚 Natural-Language Deadline Tracking

ClassBot can understand requests such as:

> "@ClassBot add a physics test for September 25. Chapters 3-5."

Gemini determines when a deadline should be saved and uses a Python function to store it in the SQLite database.

### 📅 Deadline Database

ClassBot uses SQLite to permanently store class deadlines, including:

- Subject
- Due date
- Description
- Deadline ID

Deadlines can be retrieved by asking ClassBot for assignments within a specific date range.

### 💬 "What Did I Miss?"

ClassBot can review the most recent messages in a Discord channel and use Gemini to summarize important information.

For example:

> "@ClassBot what did I miss?"

The bot reviews recent conversations and focuses its summary on:

- Homework and upcoming assignments
- Important announcements
- Decisions
- Other information students may need to know

### ⏰ Automatic Reminders

ClassBot can automatically check the deadline database each day and post a reminder when an assignment is due the following day.

Example:

> ⏰ Heads up — tomorrow:
> Physics — Test on Chapters 3-5

## Technologies

- **Python** — Core programming language
- **discord.py** — Discord bot framework
- **Google Gemini API** — Natural-language understanding and summarization
- **SQLite** — Persistent deadline storage
- **Google GenAI SDK** — Gemini API integration and function calling

## How It Works

ClassBot combines an AI model with traditional Python functions and a database.

```text
Discord Message
       ↓
   ClassBot
       ↓
  Gemini AI
       ↓
┌───────────────────┐
│ Understands       │
│ the request       │
└───────────────────┘
       ↓
┌──────────────────────────┐
│ Python Functions         │
│                          │
│ add_deadline()           │
│ get_deadlines()          │
│ summarize_channel()      │
└──────────────────────────┘
       ↓
     SQLite
