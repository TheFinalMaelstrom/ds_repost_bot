import discord
from discord import Message
import os
import re
import io
from dotenv import load_dotenv

# Set up the intents
intents = discord.Intents.default()
intents.message_content = True  # Must be enabled in Dev Portal

# ==========================================
# CONSTANTS & HELPER FUNCTIONS
# ==========================================
BLUR_ROLE_ID = 1573815516982935692

# Single source of truth for which domains trigger a repost
SOCIAL_LINK_RE = re.compile(
    r'https?://(?:www\.)?(twitter\.com|x\.com|tiktok\.com|instagram\.com)'
)

def fix_social_links(text: str) -> str:
    """Finds social media links and replaces them with embedding-friendly domains."""
    # Twitter / X
    text = re.sub(r'https?://(?:www\.)?(twitter\.com|x\.com)', 'https://cunnyx.com', text)
    # TikTok
    text = re.sub(r'https?://(?:www\.)?(tiktok\.com)', 'https://tnktok.com', text)
    # Instagram
    text = re.sub(r'https?://(?:www\.)?(instagram\.com)', 'https://toinstagram.com', text)
    return text

def _is_link_spoilered(text: str, match: re.Match) -> bool:
    """True if the given URL match sits entirely inside a ||...|| spoiler region."""
    # The link must start inside an open spoiler (odd number of '||' before it)...
    if text[:match.start()].count("||") % 2 != 1:
        return False
    # ...and a closing '||' must appear after it. URLs never contain '||',
    # so any '||' after the match's end closes the current spoiler.
    return "||" in text[match.end():]

def all_social_links_spoilered(text: str) -> bool:
    """
    True if the text contains at least one social link AND every single one
    is already wrapped in ||...||.
    """
    matches = list(SOCIAL_LINK_RE.finditer(text))
    if not matches:
        return False
    return all(_is_link_spoilered(text, m) for m in matches)

def is_keto(message: Message) -> bool:
    """True if the message was authored by the Keto bot."""
    if not message.author.bot:
        return False
    # Preferred: set KETO_BOT_ID in .env for a 100 % reliable match
    keto_id = int(os.getenv("KETO_BOT_ID", "0") or 0)
    if keto_id:
        return message.author.id == keto_id
    # Fallback: match by bot username
    return "keto" in message.author.name.lower()

async def assign_role(interaction: discord.Interaction, role_id_str: str):
    try:
        role_id = int(role_id_str)
        if interaction.guild is None:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return

        role = interaction.guild.get_role(role_id)
        if not role:
            await interaction.response.send_message("❌ Error: Role not found. Please check the Role ID in the code.", ephemeral=True)
            return

        member = interaction.user
        await member.add_roles(role) # type: ignore
        await interaction.response.edit_message(content=f"✅ You have been given the **{role.name}** role!", view=None)
        
    except ValueError:
        await interaction.response.send_message("❌ Error: The Role ID in the code is invalid (not a number).", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to give you this role. Make sure my bot role is higher in the Role settings.", ephemeral=True)

# ==========================================
# BRANCH 1: GAMES
# ==========================================
class GamesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Choose your main game...",
        options=[
            discord.SelectOption(label="Zenless Zone Zero", value="1532406509810487439"),
            discord.SelectOption(label="Pokemon", value="1558776797141925978"),
            discord.SelectOption(label="Fate Series", value="1557308005735727164"),
            discord.SelectOption(label="Blue Archive", value="1572323433960702153")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        await assign_role(interaction, select.values[0])

# ==========================================
# BRANCH 2: KINKS
# ==========================================
class KinksView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Choose your interest...",
        options=[
            discord.SelectOption(label="Lolicon", value="1569713677215469662"),
            discord.SelectOption(label="Futanari", value="1566145637270167632"),
            discord.SelectOption(label="Yuri", value="1526456128458985542"),
            discord.SelectOption(label="Guro & Ryona", value="1573815516982935692")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        await assign_role(interaction, select.values[0])

# ==========================================
# BRANCH 3: MUSIC
# ==========================================
class MusicView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Choose your favorite genre...",
        options=[
            discord.SelectOption(label="Vocaloid", value="1573812371137372170"),
            discord.SelectOption(label="R&B", value="1573812584446955681"),
            discord.SelectOption(label="Rock", value="1573812659319742605")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        await assign_role(interaction, select.values[0])

# ==========================================
# MAIN MENU
# ==========================================
class MainRoleMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Games", style=discord.ButtonStyle.primary, emoji="🎮")
    async def games_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Please select your game:", view=GamesView(), ephemeral=True)

    @discord.ui.button(label="Kinks", style=discord.ButtonStyle.danger, emoji="🎀")
    async def kinks_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Please select your interest:", view=KinksView(), ephemeral=True)

    @discord.ui.button(label="Music", style=discord.ButtonStyle.success, emoji="🎵")
    async def music_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Please select your music genre:", view=MusicView(), ephemeral=True)

# ==========================================
# MAIN BOT CLASS
# ==========================================
class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message: Message):
        if message.author == self.user or message.guild is None:
            return

        # ==========================================
        # 0. DELETE ANY KETO REPLY to a @Guro & Ryona message
        # ==========================================
        if is_keto(message):
            if message.reference and message.reference.message_id:
                try:
                    ref = await message.channel.fetch_message(message.reference.message_id)
                except (discord.NotFound, discord.HTTPException) as e:
                    print(f"Keto reply: could not fetch referenced message: {e}")
                    return
                if any(r.id == BLUR_ROLE_ID for r in ref.role_mentions):
                    # NEW: if the user already spoilered every link themselves,
                    # treat the referenced message as if the blur role weren't
                    # mentioned at all — leave Keto's reply alone.
                    if all_social_links_spoilered(ref.content):
                        return
                    try:
                        await message.delete()
                        print("Deleted Keto's reply to a blurred message.")
                    except discord.Forbidden:
                        print("Missing 'Manage Messages' to delete Keto's reply.")
                    except discord.HTTPException as e:
                        print(f"Failed to delete Keto's reply: {e}")
            # Never let other handlers process Keto's own output
            return

        content_lower = message.content.lower()

        # Define our checks
        has_blur_role = any(role.id == BLUR_ROLE_ID for role in message.role_mentions)
        has_social_link = bool(SOCIAL_LINK_RE.search(message.content))
        links_all_spoilered = all_social_links_spoilered(message.content)

        # ==========================================
        # 1. HANDLE SOCIAL LINKS (Only when Guro & Ryona role is tagged
        #    AND the user hasn't already spoilered the link(s) themselves)
        # ==========================================
        if has_social_link and has_blur_role and not links_all_spoilered:
            # Suppress the original embed (Requires Manage Messages)
            try:
                await message.edit(suppress=True)
            except discord.Forbidden:
                print("Missing 'Manage Messages' permission to suppress original embed.")
            except Exception as e:
                print(f"Could not suppress embed: {e}")

            fixed_content = fix_social_links(message.content)
            role = message.guild.get_role(BLUR_ROLE_ID)
            role_name = role.name if role else "Sensitive Content"

            # Wrapping the link in || spoiler tags usually blurs the embed
            repost_text = (
                f"⚠️ **{message.author.display_name} triggered `{role_name}`:**\n"
                f"||{fixed_content}||"
            )
            await message.channel.send(repost_text)
            return

        # ==========================================
        # 2. HANDLE BLUR ROLE (For direct image attachments)
        # ==========================================
        if has_blur_role and message.attachments:
            images = [a for a in message.attachments if a.content_type and a.content_type.startswith('image/')]
            
            if images:
                spoiled_files = []
                for img in images:
                    img_bytes = await img.read()
                    spoiled_files.append(discord.File(io.BytesIO(img_bytes), filename=img.filename, spoiler=True))
                
                try:
                    await message.delete()
                except discord.Forbidden:
                    pass # We'll just repost it anyway
                
                role = message.guild.get_role(BLUR_ROLE_ID)
                role_name = role.name if role else "Sensitive Content"
                
                warning = f"⚠️ **{message.author.mention} triggered the `{role_name}` role.**\n"
                await message.channel.send(content=warning, files=spoiled_files)
                return 

        # ==========================================
        # 3. COMMANDS (!roles and !relay)
        # ==========================================
        if content_lower.startswith("!roles"):
            embed = discord.Embed(
                title="Select Your Roles",
                description="Click the buttons below to choose your roles!",
                color=discord.Color.blue()
            )
            await message.channel.send(embed=embed, view=MainRoleMenuView())
            return 

        is_command = "relay" in content_lower and (self.user.mentioned_in(message) or content_lower.startswith("!relay")) # type: ignore

        if not is_command:
            return

        if not message.reference:
            await message.reply("You must use this command as a reply to the message you want to relay.")
            return

        assert message.reference is not None

        try:
            replied_message = await message.channel.fetch_message(message.reference.message_id)
        except discord.NotFound:
            await message.reply("Could not find the original replied message.")
            return

        target_thread_id_str = os.getenv('TARGET_THREAD_ID')
        if not target_thread_id_str:
            await message.reply("Target Thread ID is not configured in the bot's `.env` file.")
            return

        try:
            target_thread = self.get_channel(int(target_thread_id_str))
            if not target_thread:
                target_thread = await self.fetch_channel(int(target_thread_id_str))
        except Exception as e:
            await message.reply(f"Could not find the target thread. Error: {e}")
            return

        if not isinstance(target_thread, (discord.TextChannel, discord.Thread, discord.VoiceChannel)):
            await message.reply("The target channel is not a text channel or thread that I can send messages to.")
            return

        content = replied_message.content
        attachments = replied_message.attachments

        if not content and not attachments:
            await message.reply("The replied message has no text or attachments to relay.")
            return

        jump_link = f"➡️ **[Jump to original message]({replied_message.jump_url})**"
        relay_text = f"**Relayed from {replied_message.author.display_name}:**\n{jump_link}\n\n{content}"

        files_to_send = []
        for attachment in attachments:
            try:
                file = await attachment.to_file()
                files_to_send.append(file)
            except Exception as e:
                print(f"Failed to download attachment: {e}")

        try:
            allowed_mentions = discord.AllowedMentions(everyone=False, users=False, roles=False)
            await target_thread.send(
                content=relay_text, 
                files=files_to_send, 
                allowed_mentions=allowed_mentions
            )
            await message.add_reaction("✅")
        except discord.Forbidden:
            await message.reply("I do not have permission to send messages in that target thread.")
        except Exception as e:
            await message.reply(f"An error occurred while relaying: {e}")

# ==========================================
# LOAD ENV AND RUN
# ==========================================
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN is None:
    raise ValueError("DISCORD_TOKEN is missing from the .env file")

client = MyClient(intents=intents)
client.run(TOKEN)
