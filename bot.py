import discord
from discord.ext import commands, tasks
import datetime
from flask import Flask
from threading import Thread
import os
import json
import random
from discord.ext.commands import MissingPermissions

# Bot setup
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Keep alive server
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8080))  # Use the PORT environment variable or default to 8080
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Variables
dev_mode = False
dev_code = "973829582958285938582592859285829581067263502832958273495"
PUNISHMENT_FILE = "punishment_logs.json"

def load_punishments():
    try:
        with open(PUNISHMENT_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_punishments(punishments):
    with open(PUNISHMENT_FILE, 'w') as f:
        json.dump(punishments, f, indent=4)

punishment_logs = load_punishments()  # Load existing punishments on startup

# Utility Functions
def create_embed(title, description, color=discord.Color.blue()):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text="Elite Honor Guard Overwatch")
    return embed

# Status messages
status_messages = [
    ("watching", "Elite Honor Guard"),
    ("playing", "with commands"),
    ("listening", "to reports"),
    ("watching", "over the server"),
    ("playing", "Prismatrix Studios")
]
current_status = 0

# Events
@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')
    change_status.start()
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="Elite Honor Guard"
    ))

# Commands
@bot.command()
async def promote(ctx, member: discord.Member, *, reason=None):
    embed = create_embed(
        "Promotion Announcement",
        f"{member.mention} has been promoted by {ctx.author.mention}!\nReason: {reason if reason else 'No reason provided'}"
    )
    await ctx.send(f"{member.mention}", embed=embed)

@bot.command()
async def demote(ctx, member: discord.Member, *, reason=None):
    embed = create_embed(
        "Demotion Notice",
        f"{member.mention} has been demoted by {ctx.author.mention}.\nReason: {reason if reason else 'No reason provided'}",
        discord.Color.red()
    )
    await ctx.send(f"{member.mention}", embed=embed)

@bot.command()
async def terminate(ctx, member: discord.Member, *, reason=None):
    embed = create_embed(
        "Termination Notice",
        f"{member.mention} has been terminated by {ctx.author.mention}.\nReason: {reason if reason else 'No reason provided'}",
        discord.Color.dark_red()
    )
    await ctx.send(f"{member.mention}", embed=embed)

@bot.command()
async def deploy(ctx, *, details):
    embed = create_embed(
        "Deployment Announcement",
        f"New Deployment\n\nDetails: {details}",
        discord.Color.green()
    )
    await ctx.send("@everyone", embed=embed)

@bot.command()
async def training(ctx, *, details):
    embed = create_embed(
        "Training Announcement",
        f"Training Session\n\nDetails: {details}",
        discord.Color.gold()
    )
    await ctx.send("@everyone", embed=embed)

# New Announcement Command
@bot.command()
async def annc(ctx, *, announcement):
    embed = create_embed(
        "Announcement",
        announcement,
        discord.Color.blue()
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()  # Delete the command message

# Moderation Commands
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    embed = create_embed(
        "Member Kicked",
        f"{member.mention} has been kicked.\nReason: {reason if reason else 'No reason provided'}",
        discord.Color.orange()
    )
    await ctx.send(embed=embed)

    punishment_logs.append({
        "type": "kick",
        "user": str(member),
        "user_id": member.id,
        "reason": reason,
        "moderator": str(ctx.author),
        "moderator_id": ctx.author.id,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    save_punishments(punishment_logs)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    embed = create_embed(
        "Member Banned",
        f"{member.mention} has been banned.\nReason: {reason if reason else 'No reason provided'}",
        discord.Color.dark_red()
    )
    await ctx.send(embed=embed)

    punishment_logs.append({
        "type": "ban",
        "user": str(member),
        "user_id": member.id,
        "reason": reason,
        "moderator": str(ctx.author),
        "moderator_id": ctx.author.id,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    save_punishments(punishment_logs)

@bot.command()
async def warn(ctx, member: discord.Member, *, reason):
    embed = create_embed(
        "Warning Issued",
        f"{member.mention} has been warned.\nReason: {reason}",
        discord.Color.gold()
    )
    punishment_logs.append({
        "type": "warning",
        "user": str(member),
        "user_id": member.id,
        "reason": reason,
        "moderator": str(ctx.author),
        "moderator_id": ctx.author.id,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    save_punishments(punishment_logs)
    await ctx.send(f"{member.mention}", embed=embed)

@bot.command()
async def strike(ctx, member: discord.Member, *, reason):
    embed = create_embed(
        "Strike Issued",
        f"{member.mention} has received a strike.\nReason: {reason}",
        discord.Color.red()
    )
    punishment_logs.append({
        "type": "strike",
        "user": str(member),
        "user_id": member.id,
        "reason": reason,
        "moderator": str(ctx.author),
        "moderator_id": ctx.author.id,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    save_punishments(punishment_logs)
    await ctx.send(f"{member.mention}", embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command()
async def devmode(ctx, code):
    global dev_mode
    if code == dev_code:
        dev_mode = True
        embed = create_embed(
            "Developer Mode",
            "Developer mode activated successfully.",
            discord.Color.green()
        )
        await ctx.message.delete()
        await ctx.send(embed=embed)
    else:
        embed = create_embed(
            "Error",
            "Invalid developer code.",
            discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command()
async def tell(ctx, *, message):
    if not dev_mode:
        embed = create_embed(
            "Error",
            "Developer mode must be activated to use this command.",
            discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    await ctx.message.delete()
    await ctx.send(message)

@bot.command()
async def shutdown(ctx):
    global dev_mode
    if dev_mode:
        embed = create_embed(
            "Shutdown",
            "Bot is shutting down...",
            discord.Color.red()
        )
        await ctx.send(embed=embed)
        await bot.close()
    else:
        embed = create_embed(
            "Error",
            "Developer mode must be activated to use this command.",
            discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command()
async def commands(ctx):
    embed = discord.Embed(
        title="Elite Honor Guard Overwatch Commands",
        description="Here are all available commands:",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.utcnow()
    )

    # Administrative Commands
    embed.add_field(
        name=" Administrative",
        value=""" 
        `!promote @user [reason]` - Promote a member
        `!demote @user [reason]` - Demote a member
        `!terminate @user [reason]` - Terminate a member
        """,
        inline=False
    )

    # Announcement Commands
    embed.add_field(
        name=" Announcements",
        value=""" 
        `!deploy <details>` - Make a deployment announcement
        `!training <details>` - Make a training announcement
        `!annc <announcement>` - Make an announcement
        """,
        inline=False
    )

    # Moderation Commands
    embed.add_field(
        name=" Moderation",
        value=""" 
        `!kick @user [reason]` - Kick a member
        `!ban @user [reason]` - Ban a member
        `!warn @user <reason>` - Warn a member
        `!strike @user <reason>` - Issue a strike
        `!punishments` - View punishment history
        `!removepunishment <index>` - Remove a punishment from logs
        """,
        inline=False
    )

    # Utility Commands
    embed.add_field(
        name=" Utility",
        value=""" 
        `!ping` - Check bot latency
        `!commands` - Show this help message
        """,
        inline=False
    )

    embed.set_footer(text="Elite Honor Guard Overwatch")
    await ctx.send(embed=embed)

@bot.command()
async def punishments(ctx):
    if not punishment_logs:
        embed = create_embed("Punishment Logs", "No punishments have been recorded.")
        await ctx.send(embed=embed)
        return

    embed = create_embed("Punishment Logs", "Here are all recorded punishments:")
    
    for index, punishment in enumerate(punishment_logs):
        timestamp = datetime.datetime.fromisoformat(punishment["timestamp"]).strftime("%Y-%m-%d %H:%M UTC")
        embed.add_field(
            name=f"{index + 1}. {punishment['type'].title()} - {punishment['user']}",
            value=f"Reason: {punishment['reason']}\nModerator: {punishment['moderator']}\nTime: {timestamp}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command()
async def removepunishment(ctx, index: int):
    if not 1 <= index <= len(punishment_logs):
        await ctx.send("Invalid punishment index!")
        return

    removed = punishment_logs.pop(index - 1)
    save_punishments(punishment_logs)
    
    embed = create_embed(
        "Punishment Removed",
        f"Removed {removed['type']} for {removed['user']}\nReason was: {removed['reason']}"
    )
    await ctx.send(embed=embed)

@bot.command()
async def test(ctx):
    await ctx.send("The bot is working!")

@bot.command()
async def depend(ctx):
    response = "The Deployment Has Ended"
    await ctx.send(response)  # Send the response
    await ctx.message.delete()  # Delete the command message

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument! Usage: {ctx.command.name} {ctx.command.signature}")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found!")
    else:
        print(f"Command error: {str(error)}")
        await ctx.send(f"An error occurred: {str(error)}")

# Status rotation
@tasks.loop(seconds=30)
async def change_status():
    global current_status
    status_type, status_message = status_messages[current_status]

    if status_type == "watching":
        activity_type = discord.ActivityType.watching
    elif status_type == "playing":
        activity_type = discord.ActivityType.playing
    elif status_type == "listening":
        activity_type = discord.ActivityType.listening
    
    await bot.change_presence(activity=discord.Activity(
        type=activity_type,
        name=status_message
    ))
    
    current_status = (current_status + 1) % len(status_messages)

# Start the bot
keep_alive()
bot.run(os.environ['TOKEN'])

class ChatBot:
    def __init__(self):
        self.responses = [
            "Hello! How can I assist you today?",
            "I'm here to help you with your queries.",
            "What would you like to know?",
            "Feel free to ask me anything!"
        ]
        self.commands = {
            "!depend": self.depend_command
        }

    def get_response(self):
        return random.choice(self.responses)

    def depend_command(self):
        response = "The Deployment Has Ended"
        # Remove the command from the commands list
        del self.commands["!depend"]
        return response

    def handle_command(self, command):
        if command in self.commands:
            return self.commands[command]()
        return "Unknown command."

if __name__ == "__main__":
    bot = ChatBot()
    print(bot.get_response())
