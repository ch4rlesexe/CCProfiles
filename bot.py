import discord
from discord.ext import commands
import json
import os

# path to profile data file
PROFILE_FILE = "profiles.json"

# load profiles from file if exists
if os.path.exists(PROFILE_FILE):
    with open(PROFILE_FILE, "r") as f:
        profiles = json.load(f)
else:
    profiles = {}

def hex_to_int(hex_str):
    """Convert a hex color string (e.g., '#FF5733') to an integer."""
    try:
        if hex_str.startswith("#"):
            hex_str = hex_str[1:]
        return int(hex_str, 16)
    except Exception:
        return None

def int_to_hex(value):
    """Convert an integer color value to a hex string (e.g., #RRGGBB)."""
    if value is None:
        return ""
    return f"#{value:06X}"

class UnifiedProfileModal(discord.ui.Modal, title="Edit Your Profile"):
    def __init__(self, defaults: dict = None):
        super().__init__()
        defaults = defaults or {}
        
        # bio: Long description field
        self.bio = discord.ui.TextInput(
            label="Bio",
            style=discord.TextStyle.long,
            placeholder="Your bio",
            required=False,
            max_length=500,
            default=defaults.get("bio", "")
        )
        # programming languages field
        self.programming_languages = discord.ui.TextInput(
            label="Programming Languages",
            style=discord.TextStyle.short,
            placeholder="e.g., Python, JavaScript",
            required=False,
            max_length=200,
            default=defaults.get("programming_languages", "")
        )
        # technologies fields
        self.technologies = discord.ui.TextInput(
            label="Technologies",
            style=discord.TextStyle.short,
            placeholder="e.g., Docker, AWS",
            required=False,
            max_length=200,
            default=defaults.get("technologies", "")
        )
        self.image = discord.ui.TextInput(
            label="Profile Image URL",
            style=discord.TextStyle.short,
            placeholder="Image URL",
            required=False,
            max_length=300,
            default=defaults.get("image", "")
        )
        self.embed_color = discord.ui.TextInput(
            label="Embed Color",
            style=discord.TextStyle.short,
            placeholder="e.g., #FF5733",
            required=False,
            max_length=7,
            default=int_to_hex(defaults.get("embed_color"))
        )
        self.add_item(self.bio)
        self.add_item(self.programming_languages)
        self.add_item(self.technologies)
        self.add_item(self.image)
        self.add_item(self.embed_color)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        color_input = self.embed_color.value.strip() if self.embed_color.value else ""
        color_int = hex_to_int(color_input) if color_input else None

        extra_links = profiles.get(user_id, {}).get("extra_links", {})

        profiles[user_id] = {
            "bio": self.bio.value or "Not set",
            "programming_languages": self.programming_languages.value or "Not set",
            "technologies": self.technologies.value or "Not set",
            "image": self.image.value or "Not set",
            "embed_color": color_int,
            "extra_links": extra_links,
        }
        with open(PROFILE_FILE, "w") as f:
            json.dump(profiles, f, indent=4)
        await interaction.response.send_message("Your profile has been updated!", ephemeral=True)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    # bot status
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Managing profiles"))
    print(f"Logged in as {bot.user}!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print("Error syncing commands:", e)

# profile slash command
@bot.tree.command(name="profile", description="View a user's profile")
async def profile(interaction: discord.Interaction, user: discord.User):
    user_id = str(user.id)
    if user_id not in profiles:
        await interaction.response.send_message("This user does not have a profile set up yet.", ephemeral=True)
        return
    data = profiles[user_id]
    # default blue embed color, if specified, grab from user
    color_value = data.get("embed_color")
    if color_value is None:
        embed_color = discord.Color.blue()
    else:
        try:
            embed_color = discord.Color(value=int(color_value))
        except Exception:
            embed_color = discord.Color.blue()
    embed = discord.Embed(title=f"{user.display_name}'s Profile", color=embed_color)
    embed.add_field(name="Bio", value=data.get("bio", "Not set"), inline=False)
    embed.add_field(name="Programming Languages", value=data.get("programming_languages", "Not set"), inline=False)
    embed.add_field(name="Technologies", value=data.get("technologies", "Not set"), inline=False)
    if data.get("image") and data.get("image") != "Not set":
        embed.set_image(url=data.get("image"))
    extra_links = data.get("extra_links", {})
    if extra_links:
        links_str = "\n".join([f"**{label}:** {url}" for label, url in extra_links.items()])
        embed.add_field(name="Extra Links", value=links_str, inline=False)
    await interaction.response.send_message(embed=embed)

# edit profile slash command
@bot.tree.command(name="editprofile", description="Edit your profile with pre-populated fields")
async def editprofile(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    defaults = profiles.get(user_id, {})
    modal = UnifiedProfileModal(defaults)
    await interaction.response.send_modal(modal)

# extra links
@bot.tree.command(name="addlink", description="Add an extra link to your profile")
async def addlink(interaction: discord.Interaction, label: str, url: str):
    user_id = str(interaction.user.id)
    if user_id not in profiles:
        profiles[user_id] = {}
    extra_links = profiles[user_id].get("extra_links", {})
    extra_links[label] = url
    profiles[user_id]["extra_links"] = extra_links
    with open(PROFILE_FILE, "w") as f:
        json.dump(profiles, f, indent=4)
    await interaction.response.send_message(f"Added link **{label}**.", ephemeral=True)

@bot.tree.command(name="removelink", description="Remove an extra link from your profile")
async def removelink(interaction: discord.Interaction, label: str):
    user_id = str(interaction.user.id)
    if user_id not in profiles or "extra_links" not in profiles[user_id]:
        await interaction.response.send_message("No extra links found.", ephemeral=True)
        return
    extra_links = profiles[user_id]["extra_links"]
    if label in extra_links:
        del extra_links[label]
        profiles[user_id]["extra_links"] = extra_links
        with open(PROFILE_FILE, "w") as f:
            json.dump(profiles, f, indent=4)
        await interaction.response.send_message(f"Removed link **{label}**.", ephemeral=True)
    else:
        await interaction.response.send_message("Link not found.", ephemeral=True)

@bot.tree.command(name="editlink", description="Edit an extra link in your profile")
async def editlink(interaction: discord.Interaction, label: str, url: str):
    user_id = str(interaction.user.id)
    if user_id not in profiles or "extra_links" not in profiles[user_id]:
        await interaction.response.send_message("No extra links found.", ephemeral=True)
        return
    extra_links = profiles[user_id]["extra_links"]
    if label in extra_links:
        extra_links[label] = url
        profiles[user_id]["extra_links"] = extra_links
        with open(PROFILE_FILE, "w") as f:
            json.dump(profiles, f, indent=4)
        await interaction.response.send_message(f"Updated link **{label}**.", ephemeral=True)
    else:
        await interaction.response.send_message("Link not found.", ephemeral=True)

bot.run("YOUR_BOT_TOKEN")
