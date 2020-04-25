# bot.py
import os
import json

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
#bot.remove_command('help')

def get_dirty(file):
    with open(file,'r') as f:
        dirty = f.readlines()
    for i in range(len(dirty)):
        dirty[i] = dirty[i].strip('\n')
    return dirty

def check_dirty(message):
    bad_words = get_dirty('dirty.txt')
    for word in bad_words:
        mes_low = message.content.lower()
        if mes_low.count(word.lower()) > 0:
            return True
    return False

def get_prefix(bot, message):
    key = str(message.author.id)
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
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(name="this server | Stay Home - Stay Safe", type=discord.ActivityType.watching))
    channel = discord.utils.get(bot.get_all_channels(), name = 'chat')
    await channel.send('Hey I\'m online!')

@bot.command(description='Only for the developer!')
@commands.is_owner()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@load.error
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        return await ctx.send('Sorry, you found a developer-only command!')

@bot.command(description='Only for the developer!')
@commands.is_owner()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

@unload.error
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        return await ctx.send('Sorry, you found a developer-only command!')

@bot.command(aliases=['rl'],description='Only for the developer!')
@commands.is_owner()
async def reload_cogs(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')   
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'Reload `{extension}` completed')

@reload_cogs.error
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        return await ctx.send('Sorry, you found a developer-only command!')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_message(message):
    if message.channel.type == discord.ChannelType.private:
        return
    if (message.author == bot.user) or (message.author.top_role.name == 'Teacher'):
        return await bot.process_commands(message)
    if message.channel.name == 'rules':
        if message.content.startswith(';signup'):
            if check_dirty(message):
                await message.channel.purge(limit=1)
            else:
                await bot.process_commands(message)
                await message.channel.purge(limit=1)
        else:
            await message.channel.purge(limit=1)
    else:
        if check_dirty(message):
            await message.channel.purge(limit=1)
            await message.channel.send('Warning! A bad word was said!')
        else:
            await bot.process_commands(message)

@bot.command(name='ping', help='Show ping.')
async def ping(ctx):
    await ctx.send(f'Pong! In {round(bot.latency*1000)}ms.')
  
@bot.command(aliases=['create','cr'], help='Create a channel',description='Only for the developer!')
@commands.is_owner()
async def create_channel(ctx, channel_name: str):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

@create_channel.error
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        return await ctx.send('Sorry, you found a developer-only command!')

bot.run(TOKEN)

'''@bot.command()
async def help(ctx):
    embed = discord.Embed(     
        colour = discord.Colour.orange()
    )
    embed.set_author(name='help')
    embed.add_field(name='ping',value='Show ping.', inline=True)

    await ctx.author.send(embed=embed)'''
'''key = '#'.join([message.author.name, message.author.discriminator])'''
'''@commands.command(name="help", description="Returns all commands available")
    async def help(self, ctx):
        helptext = "```"
        for command in self.bot.commands:
            helptext+=f"{command}\n"
        helptext+="```"
        await ctx.send(helptext)''' 

'''@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
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
    await member.dm_channel.send(embed=embed) '''