# bot.py
import os
import random
import json

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
#bot.remove_command('help')

def get_prefix(bot, message):
    key = '#'.join([message.author.name, message.author.discriminator])
    with open('./cogs/prefixes.json', 'r') as f:
        prefixes = json.load(f)

    if not key in prefixes:
        prefixes[key] = ';'
        with open('./cogs/prefixes.json', 'w') as f:
            json.dump(prefixes, f , indent=4)  
    
    return prefixes[key]

bot = commands.Bot(command_prefix=get_prefix) 

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(name="this server", type=discord.ActivityType.watching))
    channel = discord.utils.get(bot.get_all_channels(), name = 'command')
    await channel.send('Hey I\'m online')

@bot.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

@bot.command(aliases=['rl'])
@commands.has_permissions(administrator=True)
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')   
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'Reload `{extension}` completed')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
    
@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the :+1: emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)

@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='ping', help='Show ping.')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency*1000)}ms')

@bot.command()
@commands.has_permissions(administrator=True)
async def displayembed(ctx, member: discord.Member):
    embed = discord.Embed(
        title = 'Title',
        description = 'This is a description.',
        colour = discord.Colour.green()
    )

    embed.set_footer(text='This is a footer.')
    embed.set_image(url='http://data.owobot.com/background/1.png')
    embed.set_thumbnail(url='http://data.owobot.com/background/1.png')
    embed.set_author(name='Author Name', icon_url='http://data.owobot.com/background/1.png')
    embed.add_field(name='Field Name', value='Field Value', inline=False)

    #await ctx.send(embed=embed)
    await member.create_dm()
    await member.dm_channel.send(embed=embed) 
  
@bot.command(aliases=['create','cr'], help='Create a channel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name: str):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

@create_channel.error
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(f'You do not have the correct role for this command')

'''@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('You are missing permissions for this command')'''
bot.run(TOKEN)

'''@bot.command()
async def help(ctx):
    embed = discord.Embed(     
        colour = discord.Colour.orange()
    )
    embed.set_author(name='help')
    embed.add_field(name='ping',value='Show ping.', inline=True)

    await ctx.author.send(embed=embed)'''