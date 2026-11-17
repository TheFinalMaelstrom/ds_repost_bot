# 🐦 Discord Message Relay Bot (ds_repost_bot)

A custom Discord bot designed to solve channel clutter. It allows users to relay specific messages from a busy chat into a read-only archive thread or channel. 

By moving the bot's trigger from message forwarding to a **reply-based command**, it allows the target channel to be locked down (read-only) for regular users while the bot seamlessly handles the posting.

## ✨ Features

*   **Reply-to-Relay:** Users simply reply to a message with `!relay` or `@BotName relay`.
*   **Read-Only Archiving:** Keeps target threads clean and strictly for archived messages.
*   **No Ping Mentions:** Preserves `@user` and `@role` formatting so they are searchable and clickable, but **does not** send push notifications or pings.
*   **Jump Links:** Automatically generates a clickable `➡️ [Jump to original message]` link so users can instantly see the original context.
*   **Attachment Support:** Downloads and re-uploads images and files from the original message.
*   **Success Reaction:** Reacts with a ✅ to the command message to silently confirm the relay was successful without cluttering the chat with bot replies.

---

## 🛠️ Prerequisites

*   **Python 3.8+** installed on your machine.
*   A Discord Account and a Discord Server where you have Admin permissions.
*   Access to the [Discord Developer Portal](https://discord.com/developers/applications).

---

## 🚀 Setup & Installation

### 1. Discord Developer Portal Setup
1.  Go to the [Discord Developer Portal](https://discord.com/developers/applications) and click **New Application**.
2.  Go to the **Bot** tab on the left.
3.  Click **Reset Token** and copy your **Bot Token** (save this for later).
4.  Scroll down to **Privileged Gateway Intents** and toggle **ON** the `Message Content Intent`. *(This is strictly required for the bot to read the messages you reply to).*

### 2. Invite the Bot to Your Server
1.  Go to the **OAuth2** -> **URL Generator** tab.
2.  Under **Scopes**, check `bot`.
3.  Under **Bot Permissions**, check:
    *   `Read Message History` (to read the messages being replied to)
    *   `Send Messages` (to send the relay confirmation/replies)
    *   `Send Messages in Threads` (to post into the archive thread)
    *   `Add Reactions` (for the ✅)
4.  Copy the generated URL at the bottom, paste it into your browser, and invite the bot to your server.

### 3. Local Installation
Clone this repository or download the files to a folder on your computer.

Open your terminal/command prompt in that folder and install the required dependencies:
```bash
pip install discord.py python-dotenv
```

### 4. Environment Variables (`.env`)
Create a file named `.env` in the exact same folder as your Python script. Add the following lines to it:

```env
# Your bot token from the Developer Portal
DISCORD_TOKEN=your_long_bot_token_goes_here

# The ID of the channel/thread where messages will be sent
TARGET_THREAD_ID=123456789012345678
```

**How to get the `TARGET_THREAD_ID`:**
1. Enable **Developer Mode** in Discord (User Settings -> Advanced).
2. Right-click the target thread/channel and click **Copy Channel ID** (or Copy Thread ID).
3. Ensure you only copy the ID itself, not the whole URL.

---

## 💻 Running the Bot Locally

To start the bot, run:
```bash
python ds_repost_bot.py
```

If successful, your terminal will display:
```text
Logged in as Forwarded Message Archiver#1234 (ID: 1234567890)
------
```

---

## ☁️ Deployment (Railway)

If you are hosting this bot 24/7 on Railway:
1.  Push this code to a GitHub repository.
2.  Create a new project on [Railway](https://railway.app/) and deploy from your GitHub repo.
3.  Go to your Railway service's **Variables** tab and add `DISCORD_TOKEN` and `TARGET_THREAD_ID` with their respective values.
4.  **Important:** If you are testing locally, ensure you remove/pause the Railway deployment so two instances of the bot don't run at the same time (which causes connection errors).

---

## 📖 How to Use

1.  Go to a standard chat channel where the bot can see messages.
2.  Find the message you want to archive.
3.  Click the **Reply** arrow on that message.
4.  In the text box, type **`!relay`** (or ping the bot and type `relay`).
5.  Press Enter.
6.  The bot will react with a ✅, and the message will instantly appear in your target thread with a Jump Link, intact mentions, and any attachments.

---

## 🔧 Troubleshooting

*   **Error: `invalid literal for int() with base 10`**
    You pasted the entire Discord URL into the `.env` file. Discord URLs look like `discord.com/channels/SERVER_ID/CHANNEL_ID`. You only need the last long number (the `CHANNEL_ID`).
*   **The bot isn't responding to my command:**
    Ensure you are actually using Discord's **Reply** feature before typing the command. The bot ignores commands that aren't attached to a message.
*   **The bot sends the message but the jump link is broken text:**
    Ensure you didn't accidentally modify the Markdown syntax in the code. The link must be formatted exactly as `**[Text](URL)**`.
*   **Bot has no permission to send:**
    Check the permissions of the target channel. Make sure the bot has `Send Messages in Threads` permission for that specific channel.
