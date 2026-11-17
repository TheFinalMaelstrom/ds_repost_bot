import discord
from discord import Message
import os
from dotenv import load_dotenv

# Set up the intents
intents = discord.Intents.default()
intents.message_content = True  # Required to read message contents

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message: Message):
        # Ignore messages sent by the bot itself
        if message.author == self.user:
            return

        # Check if the message contains forwarded snapshots
        if message.message_snapshots:
            for snapshot in message.message_snapshots:
                # Extract the text content from the snapshot
                forwarded_content = snapshot.content
                
                if forwarded_content:
                    # Repost it as a normal message from the bot
                    # The global allowed_mentions setting will automatically prevent pings
                    await message.channel.send(
                        f"COPY: {forwarded_content}"
                    )

# Create the client, load intents, and apply the global mention block
client = MyClient(
    intents=intents,
    allowed_mentions=discord.AllowedMentions.none() # <--- Global no-ping setting
)

# Load variables from the .env file
load_dotenv()

# Retrieve the token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Run the bot using the retrieved token
client.run(TOKEN)
