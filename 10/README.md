# Telegram Keyword Alerts & Auto-Replies

1. **Alerts:** get a private Telegram notification whenever a message in **any
   chat you're in** mentions a keyword **you** choose: "school fees",
   "result", "account", anything.
2. **Auto-replies:** when people keep asking the same question ("what time is
   class?", "when are we submitting the assignment?"), your account answers
   each of them for you, with the reply **you** wrote.

- **No admin needed and nothing is added to the group.** It works through your
  own account, the same way Telegram Desktop or Web would.
- **Works in every kind of chat:** public and private groups, supergroups and
  topics, channel comment sections, and private chats.
- **Nothing built in.** You write every keyword and every reply from Telegram.
- Alerts arrive from your own private bot, so your phone actually notifies you.
- It never posts anything except the auto-replies you wrote.

```
Chats you're in ──► this program (logged in as you) ─┬─ keyword?  ──► your bot DMs you 📱
                                                      └─ question? ──► you reply to them (automatically)
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

## Auto-replies

Auto-replies are sent **from your account**, as a reply to the person's
message, so to them it looks like you answered. (A bot can't do this: Telegram
won't let a bot message people who never opened it.)

### Writing a rule
```
/reply class + time => Class is 10am in LT2 every Monday.
```
- Before `=>`: the words that must appear in the question. `+` means **all**
  of them, in any order. So `class + time` answers "What time is class?" and
  "abeg class starts what time".
- Commas give **alternatives**, so one rule can catch different wordings:
  ```
  /reply assignment + submit, assignment + due, assignment + deadline => Submit on the portal by Friday 11:59pm.
  ```
- After `=>`: your answer, exactly as it will be sent. It can be several lines.
- The same matching as keywords applies: capital letters don't matter, whole
  words only, and `*` means "any letters" (`submi*` matches submit and submission).
- If a message matches more than one rule, the lowest-numbered rule answers.

| Command | What it does |
|---|---|
| `/reply words => answer` | Add a rule |
| `/replies` | List rules with their numbers |
| `/editreply 2 => new answer` | Change rule 2's answer |
| `/delreply 2` | Delete rule 2 |
| `/testreply what time is class?` | See which rule would answer |
| `/autoreply on` / `off` | Switch auto-replies on or off (on by default) |
| `/approve on` / `off` | **Ask me first:** each reply comes to you with **Send / Skip** buttons. Off = fully automatic (default) |
| `/replyin chat` / `dm` | `chat` (default): reply in the chat where they asked. `dm`: reply privately to people in your contacts; everyone else still gets it in the chat |
| `/cooldown 24` | Hours before the same person can get the same answer again (default 12) |

You get a short note from your bot every time it answers someone
("↩️ Auto-replied to Ada in Class of 2026"), so you always know what was said.

### Built-in safety limits
Telegram restricts accounts that look like spam bots, so auto-replies:
- answer **each person once** per rule per cooldown, even if they ask again;
- wait a **random 5–20 seconds** before replying;
- send at most **10 per chat and 30 in total per hour**;
- **switch themselves off** and tell you if Telegram says "slow down";
- don't reply to bots, anonymous admins, or your own messages;
- don't answer questions more than 15 minutes old (e.g. after a restart);
- **never post in broadcast channels.** That would go to every subscriber.
  Questions in a channel's *comments* are answered normally.

`/mute` and `/only` apply to auto-replies too, and `/pause` stops everything.
Private chats are always eligible for auto-replies; `/dms` only controls keyword alerts.

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
- Apart from the auto-replies you write, the program only **reads** your
  chats. Keep the safety limits on: a personal account that mass-messages
  people can get restricted by Telegram. Private replies are limited to your
  contacts for the same reason.
- The bot ignores messages from anyone but you.

## Project layout

```
kwalert/
  app.py       Telegram connections: your account (reads, sends auto-replies)
               + your bot (alerts, commands, Send/Skip buttons)
  autoreply.py reply rules, who was already answered, safety limits
  core.py      which chats to watch, alert formatting, bot commands
  matcher.py   keyword matching rules
  kinds.py     chat types (group / channel / private)
  storage.py   SQLite: keywords, reply rules, muted/only chats, settings
tests/         pytest suite (no Telegram login needed)
```

Run the tests with `pip install pytest && python -m pytest`.
