import discord
from discord import Message
import os
from dotenv import load_dotenv

# Set up the intents
intents = discord.Intents.default()
intents.message_content = True  # This must be enabled for the bot to read messages

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    async def on_message(self, message: Message):
        # Don't respond to our own messages
        if message.author == self.user:
            return

        # Check if the message contains forwarded snapshots
        if message.message_snapshots:
            for snapshot in message.message_snapshots:
                # Extract the text content from the snapshot
                forwarded_content = snapshot.content
                if forwarded_content:
                    # Repost it as a normal message from the bot
                    await message.channel.send(
                        f"COPY: {forwarded_content}"
                    )
                    
                    # OPTIONAL: Delete the original forwarded message to avoid clutter.
                    # Uncomment the line below if you want this behavior.
                    # await message.delete()

# Create the client and run the bot
client = MyClient(intents=intents)
# Load variables from the .env file
load_dotenv()

# Retrieve the token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Run the bot using the retrieved token
client.run(TOKEN)