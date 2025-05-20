import discord
from discord.ext import commands
import datetime

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, description="Advanced Bot")

muted_users = set()  # In-memory mute list

# Bot is ready
@bot.event
async def on_ready():
    print(f'Bot online as {bot.user}')

# Welcome new members
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"Welcome to the server, {member.mention}!")
    # Auto role (role must exist)
    role = discord.utils.get(member.guild.roles, name="Member")
    if role:
        await member.add_roles(role)

# Command: ping
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! `{round(bot.latency * 1000)}ms`")

# Command: echo
@bot.command()
async def echo(ctx, *, message):
    await ctx.send(message)

# Command: userinfo
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.name}'s Info", color=discord.Color.green())
    embed.set_thumbnail(url=member.avatar.url if member.avatar else "")
    embed.add_field(name="Username", value=member, inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
    await ctx.send(embed=embed)

# Kick command
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"Kicked {member.mention} for reason: {reason}")

# Ban command
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"Banned {member.mention} for reason: {reason}")

# Mute command (in-memory)
@bot.command()
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member):
    muted_users.add(member.id)
    await ctx.send(f"{member.mention} has been muted.")

# Unmute command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
    muted_users.discard(member.id)
    await ctx.send(f"{member.mention} has been unmuted.")

# Prevent muted users from speaking
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.author.id in muted_users:
        await message.delete()
        return
    await bot.process_commands(message)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing argument.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to do that.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Unknown command.")
    else:
        await ctx.send(f"Error: {str(error)}")

# Start bot
bot.run("TOKEN")  # Replace with your token
