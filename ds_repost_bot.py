import discord
from discord import Message
import os
from dotenv import load_dotenv

# Set up the intents
intents = discord.Intents.default()
intents.message_content = True  # Must be enabled in Dev Portal

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message: Message):
        # Don't respond to our own messages
        if message.author == self.user:
            return

        # Check if the message mentions the bot or starts with !relay
        content_lower = message.content.lower()
        is_command = "relay" in content_lower and (self.user.mentioned_in(message) or content_lower.startswith("!relay"))

        if not is_command:
            return

        # 1. Check if the command was used as a reply
        if not message.reference:
            await message.reply("You must use this command as a reply to the message you want to relay.")
            return

        # 2. Fetch the replied-to message
        try:
            replied_message = await message.channel.fetch_message(message.reference.message_id)
        except discord.NotFound:
            await message.reply("Could not find the original replied message.")
            return

        # 3. Get target thread ID from environment variables
        target_thread_id_str = os.getenv('TARGET_THREAD_ID')
        if not target_thread_id_str:
            await message.reply("Target Thread ID is not configured in the bot's `.env` file.")
            return

        try:
            # Convert the ID string to an integer and find the channel
            target_thread = self.get_channel(int(target_thread_id_str))
            if not target_thread:
                target_thread = await self.fetch_channel(int(target_thread_id_str))
        except Exception as e:
            await message.reply(f"Could not find the target thread. Error: {e}")
            return

        # 4. Prepare content and attachments
        content = replied_message.content
        attachments = replied_message.attachments

        if not content and not attachments:
            await message.reply("The replied message has no text or attachments to relay.")
            return

        # --- FIXED: Emoji is outside the brackets, link is bolded ---
        jump_link = f"➡️ **[Jump to original message]({replied_message.jump_url})**"
        
        # Combine the author, the jump link, and the original content
        relay_text = f"**Relayed from {replied_message.author.display_name}:**\n{jump_link}\n\n{content}"

        # Download the attachments to re-send them
        files_to_send = []
        for attachment in attachments:
            try:
                file = await attachment.to_file()
                files_to_send.append(file)
            except Exception as e:
                print(f"Failed to download attachment: {e}")

        # 5. Send to the read-only thread WITHOUT pinging anyone
        try:
            # This tells Discord to format mentions visually, but NOT send notifications
            allowed_mentions = discord.AllowedMentions(everyone=False, users=False, roles=False)
            
            # Send the message, attachments, and apply the no-ping rule
            await target_thread.send(
                content=relay_text, 
                files=files_to_send, 
                allowed_mentions=allowed_mentions
            )
            
            # Optional: React to the user's command to show it succeeded
            await message.add_reaction("✅")
            
        except discord.Forbidden:
            await message.reply("I do not have permission to send messages in that target thread.")
        except Exception as e:
            await message.reply(f"An error occurred while relaying: {e}")

# Load variables from the .env file
load_dotenv()

# Retrieve the token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Run the bot
client = MyClient(intents=intents)
client.run(TOKEN)
