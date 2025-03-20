# Discord Profile Bot

A Discord bot that lets users create, edit, and view personal profiles using modern slash commands and modals. Users can customize their bio, programming languages, technologies, profile image, embed color, and dynamically manage extra links (such as GitHub, website, Twitter, LinkedIn, etc.).

## Features

- **Profile Management**  
  Users can set up their profile with their bio, programming languages, technologies, and profile image.

- **Customizable Embeds**  
  Choose your own embed color with hex codes and display your profile image in your profile embed.

- **Dynamic Extra Links**  
  Easily add, edit, or remove extra links with dedicated slash commands.

- **Modern Slash Commands & Modals**  
  Built with [discord.py](https://github.com/Rapptz/discord.py) 2.0+, using modals for an interactive user interface.

- **Custom Bot Status**  
  The bot sets a custom "watching" status on startup.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/discord-profile-bot.git
   cd discord-profile-bot
   ```
2. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Configure the Bot:**

- Open bot.py.
- Replace "YOUR_BOT_TOKEN" with your actual Discord bot token.

4. **Run the Bot:**
```bash
python bot.py
```


## Commands:

/profile [user]
View a user's profile.

/editprofile
Edit your main profile fields (Bio, Programming Languages, Technologies, Profile Image URL, Embed Color) via a modal with pre-populated values.

/addlink <label> <url>
Dynamically add an extra link to your profile.

/editlink <label> <url>
Edit an existing extra link in your profile.

/removelink <label>
Remove an extra link from your profile.

Profile Storage:
All profiles are stored persistently in profiles.json in the project directory.
