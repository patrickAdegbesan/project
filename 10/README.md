# Telegram Keyword Alerts

Get a private Telegram notification whenever a message in **any group you're in**
mentions a keyword **you** choose: "school fees", "result", "account", anything.

- **No admin needed and nothing is added to the group.** It reads your groups
  through your own account, the same way Telegram Desktop or Web would.
- **Nobody in the group can tell.** It never posts in your groups.
- **No built-in keywords.** You add, remove and test them yourself from Telegram.
- Alerts arrive from your own private bot, so your phone actually notifies you.

```
Groups you're in ──► this program (logged in as you) ──► keyword? ──► your bot DMs you 📱
```

## What an alert looks like

> 🔔 **school fees**
> 💬 **Class of 2026**
> 👤 John Doe
>
> Pls note: **<u>School fees</u>** deadline is Friday
>
> [Open message]

## Setup (about 10 minutes)

You need Python 3.10+ and a computer or server that stays on (see *Hosting*).

### 1. Get your Telegram API keys
1. Go to <https://my.telegram.org> and log in with your phone number.
2. Open **API development tools** and create an app (any name and short name).
3. Copy the **api_id** and **api_hash**.

### 2. Create your alert bot
1. In Telegram, open **@BotFather** and send `/newbot`.
2. Pick a name and username. Copy the **token** it gives you.
3. Open your new bot and press **START**. Without this, the bot isn't
   allowed to message you.

You **don't** add this bot to any group. It only talks to you.

### 3. Install and configure
```bash
cd 10
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then fill in the three values
```

### 4. Run
```bash
python -m kwalert
```
The first time, it asks for your **phone number**, the **login code** Telegram
sends you, and your **2-step verification password** if you have one. After
that it remembers the login (in `data/`).

Your bot will message you: *"Keyword alerts are running."* Send it `/help`.

## Using it

Everything is done by chatting with your bot:

| Command | What it does |
|---|---|
| `/add school fees, result, account` | Add one or more keywords (comma-separated) |
| `/remove result` | Remove keywords |
| `/list` | Show your keywords |
| `/test School fees due Friday` | Check which keywords would fire |
| `/clear yes` | Delete all keywords |
| `/regex <pattern>` | Advanced: add a regular expression |
| `/groups` | Numbered list of your chats and whether they're watched |
| `/mute 2 5` / `/unmute 2` | Stop or restart alerts from specific chats |
| `/only 1 4` | Watch **only** those chats; `/only off` to go back to all |
| `/channels on` | Also watch channels (off by default) |
| `/dms on` | Also watch private chats (off by default) |
| `/pause` / `/resume` | Pause or restart all alerts |
| `/status` | Show current settings |

### How matching works
- **Capital letters don't matter:** `school fees` matches "SCHOOL FEES".
- **Whole words only:** `account` will **not** fire on "accountability".
- **Phrases are flexible about spacing:** `school fees` also matches
  "school-fees" and "school   fees".
- **`*` means "any letters":** `fee*` matches "fee", "fees"; `result*` matches
  "result", "results".
- **Photo/document captions** are checked too, and so are **edited** messages
  (you're only alerted again if the edit adds a new keyword).
- Your own messages never trigger alerts.
- Text *inside* images or PDFs isn't read, only the message text and caption.

## Hosting (keeping it running 24/7)

It must stay connected to catch messages, so run it somewhere that's always on:

- **A cheap VPS** (any Linux server): run it with `systemd`, `tmux` or
  `screen`. Log in once interactively, then it keeps going.
- **Railway / Render / Fly.io:** you can't type the login code there, so on
  your own computer run
  ```bash
  python -m kwalert --session-string
  ```
  log in, and copy the long string it prints into the host's `TG_SESSION`
  setting, along with `TG_API_ID`, `TG_API_HASH` and `TG_BOT_TOKEN`. Attach a
  persistent volume and set `DATA_DIR` to it so your keywords survive restarts.
- **An old laptop or Raspberry Pi at home** works too.

Serverless platforms (Vercel, Netlify functions) won't work: they can't hold a
connection open.

If it restarts, it fetches messages it missed while offline.

## Safety

- `TG_SESSION` and the files in `data/` **are a login to your Telegram
  account**. Keep them private and never commit them (they're git-ignored).
- To revoke access at any time: Telegram → Settings → Devices → end the session.
- The program only **reads** your chats and sends alerts to you. Keep it that
  way: using a personal account to mass-message people can get it restricted.
- The bot ignores messages from anyone but you.

## Project layout

```
kwalert/
  app.py       Telegram connections: your account (reader) + your bot (alerts, commands)
  core.py      which chats to watch, alert formatting, bot commands
  matcher.py   keyword matching rules
  storage.py   SQLite: keywords, muted/only chats, settings
tests/         pytest suite (no Telegram login needed)
```

Run the tests with `pip install pytest && python -m pytest`.
