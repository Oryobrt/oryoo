import discord
from discord import app_commands, ui
from discord.ext import commands
import secrets
import string
import time
import django
import os
from django.db import transaction
from asgiref.sync import sync_to_async
from django.utils import timezone

# === CONFIG ===
TOKEN = ("MTM2NTAyMTM0OTUwODAyMjMyMw.GA2cBX.j4PGN1i1Q8d9BGMwjg4XGsWfm-52l5oXGqWalQ")  # Loading token from environment variables

GUILD_ID = 1367778913081626624  # Replace with your server's ID

# === DJANGO SETUP ===
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "keissho.settings")
django.setup()

# Import the License model from your Django app
from licenses.models import License  # Adjust this based on your actual app name

# === LICENSE HANDLING ===
def generate_license():
    """Generate a random license key."""
    segments = [''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6)) for _ in range(7)]
    return '-'.join(segments)

@sync_to_async
def generate_and_save_license():
    """Generate a new license key and save it to the database."""
    license_key = generate_license()  # Generate license key
    expiry_date = timezone.now() + timezone.timedelta(days=30)  # Set expiry date (example: 30 days)
    
    # Create a new License object based on the fields defined in the model
    new_license = License(
        license_key=license_key,
        hwid="",  # Initially no HWID
        expiry_date=expiry_date,
        activated_on=timezone.now(),
        meta={"last_hwid_reset": 0}  # Save the last HWID reset time as part of the meta field
    )
    
    # Save the License to the database
    new_license.save()

    return license_key

from asgiref.sync import sync_to_async

@sync_to_async
def get_license(license_key):
    """Retrieve the license from the database by its key."""
    try:
        return License.objects.get(license_key=license_key)
    except License.DoesNotExist:
        return None


# === DISCORD SETUP ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# === MODALS ===
from asgiref.sync import sync_to_async

# Wrap ORM queries with sync_to_async
@sync_to_async
def get_license(license_key):
    """Retrieve the license from the database by its key."""
    try:
        return License.objects.get(license_key=license_key)
    except License.DoesNotExist:
        return None

@sync_to_async
def save_license(license):
    """Save the updated license to the database."""
    license.save()

# In your modal, use the async functions to interact with the database
class VerifyModal(ui.Modal, title='Verify License'):
    license_input = ui.TextInput(label='License Key', placeholder='Enter your license key')
    email_input = ui.TextInput(label='Email', placeholder='Enter your email')
    confirm_email = ui.TextInput(label='Confirm Email', placeholder='Re-enter your email')

    async def on_submit(self, interaction: discord.Interaction):
        lic = self.license_input.value.strip()
        email = self.email_input.value.strip()
        conf = self.confirm_email.value.strip()

        if email != conf:
            return await interaction.response.send_message('❌ Emails do not match.', ephemeral=True)

        # Use the async get_license method
        license = await get_license(lic)

        if not license:
            return await interaction.response.send_message('❌ Invalid license key.', ephemeral=True)

        if license.email:
            return await interaction.response.send_message('⚠️ License already used.', ephemeral=True)

        # Now update the license with the new email
        license.email = email
        license.hwid = ""  # Reset HWID if necessary

        # Use the async save_license method
        await save_license(license)

        await interaction.response.send_message('✅ License verified!', ephemeral=True)

class ResetModal(ui.Modal, title='Reset License'):
    license_input = ui.TextInput(label='License Key', placeholder='Enter your license key')
    email_input = ui.TextInput(label='Email', placeholder='Enter your email')
    confirm_email = ui.TextInput(label='Confirm Email', placeholder='Re-enter your email')

    async def on_submit(self, interaction: discord.Interaction):
        lic = self.license_input.value.strip()
        email = self.email_input.value.strip()
        conf = self.confirm_email.value.strip()

        if email != conf:
            return await interaction.response.send_message('❌ Emails do not match.', ephemeral=True)

        license = await get_license(lic)  # Await the coroutine to get the license
        if not license:
            return await interaction.response.send_message('❌ Invalid license key.', ephemeral=True)

        if license.email.lower() != email.lower():
            return await interaction.response.send_message('❌ Email mismatch.', ephemeral=True)

        license.email = None
        license.save()

        await interaction.response.send_message('✅ License information reset!', ephemeral=True)

class ResetHwidModal(ui.Modal, title='Reset HWID'):
    license_input = ui.TextInput(label='License Key', placeholder='Enter your license key')
    email_input = ui.TextInput(label='Email', placeholder='Enter your email')
    confirm_email = ui.TextInput(label='Confirm Email', placeholder='Re-enter your email')

    async def on_submit(self, interaction: discord.Interaction):
        lic = self.license_input.value.strip()
        email = self.email_input.value.strip()
        conf = self.confirm_email.value.strip()

        if email != conf:
            return await interaction.response.send_message('❌ Emails do not match.', ephemeral=True)

        license = await get_license(lic)  # Await the coroutine to get the license
        if not license:
            return await interaction.response.send_message('❌ Invalid license key.', ephemeral=True)

        if license.email.lower() != email.lower():
            return await interaction.response.send_message('❌ Email mismatch.', ephemeral=True)

        # 24 HOUR COOLDOWN CHECK
        last_reset = license.last_hwid_reset
        current_time = time.time()
        if current_time - last_reset < 86400:
            remaining = 86400 - (current_time - last_reset)
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            seconds = remaining % 60

# === VIEWS ===
class VerifyView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label='Verify License', style=discord.ButtonStyle.green, custom_id='verify_btn'))

class ResetView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label='Reset License', style=discord.ButtonStyle.blurple, custom_id='reset_btn'))

class ResetHwidView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label='Reset HWID', style=discord.ButtonStyle.red, custom_id='reset_hwid_btn'))

# === COMMANDS ===
@bot.command(name="genkey")
@commands.has_permissions(administrator=True)
async def generate_key(ctx):
    new_key = await generate_and_save_license()  # Using the Django ORM function to save
    await ctx.send(f"🔑 New license key generated:\n{new_key}")

# === EVENTS ===
@bot.event
async def on_ready():
    print(f'🚀 Bot ready as {bot.user}')
    guild = bot.get_guild(GUILD_ID)
    if guild:
        # Channels and buttons setup
        verify_ch = discord.utils.get(guild.text_channels, name='verify-license')
        reset_ch = discord.utils.get(guild.text_channels, name='reset-license')
        hwid_ch = discord.utils.get(guild.text_channels, name='reset-hwid')

        if verify_ch:
            await verify_ch.send(
                '**Verify Your License**\nClick the button below and complete the form.',
                view=VerifyView()
            )

        if reset_ch:
            await reset_ch.send(
                '**Reset Your License**\nClick the button below and complete the form.',
                view=ResetView()
            )

        if hwid_ch:
            await hwid_ch.send(
                '**Reset Your HWID**\nClick the button below and complete the form.',
                view=ResetHwidView()
            )

    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        cid = interaction.data.get('custom_id')
        if cid == 'verify_btn':
            await interaction.response.send_modal(VerifyModal())
        elif cid == 'reset_btn':
            await interaction.response.send_modal(ResetModal())
        elif cid == 'reset_hwid_btn':
            await interaction.response.send_modal(ResetHwidModal())

bot.run(TOKEN)
