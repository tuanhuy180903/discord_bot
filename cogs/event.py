import discord
import json
from discord.ext import commands


def get_dirty(file):
    with open(file,'r') as f:
        dirty = f.readlines()
    for i in range(len(dirty)):
        dirty[i] = dirty[i].strip('\n')
    return dirty

def is_teacher(member):
    return member == member.guild.owner

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        #print(message.channel)
        if (message.author == self.bot.user) or (message.author == message.guild.owner):
            return
        if message.channel.type == discord.ChannelType.private:
            return
        if message.channel.name == 'rules':
            await message.channel.purge(limit=1)
        else:
            bad_words = get_dirty('dirty.txt')
            for word in bad_words:
                mes_low = message.content.lower()
                #word_low = word.lower()
                if mes_low.count(word.lower()) > 0:
                    await message.channel.purge(limit=1)
                    await message.channel.send('Warning! A bad word was said!')
                    break
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member != member.guild.owner:
            return
        if before.channel is None and after.channel is not None:
            voice_name = after.channel.name
            pos = voice_name.find(' ')
            role = discord.utils.get(member.guild.roles, name=voice_name[0:pos]) 
            
            name = voice_name[0:pos] + '-chat'
            channel = discord.utils.get(member.guild.channels, name=name.lower())
            await channel.send(role.mention)
            embed = discord.Embed(
                title = f'Hello everyone!',
                description = f'**{member.name}** is teaching in **{voice_name}**.\nPlease click **{voice_name}** on the left side of Discord UI to connect to the classroom.',
                colour = discord.Colour.gold()
            )
            embed.set_footer(text='Copyright © 2020 EEIT2017')
            embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        if len(reaction.message.embeds)==0:
            return
        with open('./cogs/question.json', 'r') as f:
            question = json.load(f)
        mess_id = str(reaction.message.id)
        uzer = self.bot.get_user(user.id)
        channel = reaction.message.channel
        if mess_id in question:
            if reaction.emoji == question[mess_id]:
                await uzer.create_dm()
                message = await channel.fetch_message(reaction.message.id)
                embed = message.embeds
                await uzer.dm_channel.send(f'> **{embed[0].description}**\nYou chose the **correct** answer for the question!')
            else:
                await uzer.create_dm()
                message = await channel.fetch_message(reaction.message.id)
                embed = message.embeds
                await uzer.dm_channel.send(f'> **{embed[0].description}**\nYou chose the **wrong** answer for the question!')

        '''channel = reaction.message.channel
        #await channel.send(f'{user.name} has added {reaction.emoji} to the message: {reaction.message.content}')'''

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return
        if len(reaction.message.embeds)==0:
            return
        with open('./cogs/question.json', 'r') as f:
            question = json.load(f)
        mess_id = str(reaction.message.id)
        uzer = self.bot.get_user(user.id)
        channel = reaction.message.channel
        if mess_id in question:
            if reaction.emoji == question[mess_id]:
                await uzer.create_dm()
                message = await channel.fetch_message(reaction.message.id)
                embed = message.embeds
                await uzer.dm_channel.send(f'> **{embed[0].description}**\nYou chose the **correct** answer for the question!')
            else:
                await uzer.create_dm()
                message = await channel.fetch_message(reaction.message.id)
                embed = message.embeds
                await uzer.dm_channel.send(f'> **{embed[0].description}**\nYou chose the **wrong** answer for the question!')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title = f'Welcome to {member.guild.owner.name}\'s server!',
            description = f'Hi __**{member.name}**__! This is a teaching server run by {self.bot.user.name}.',
            colour = discord.Colour.green()
        )

        embed.set_footer(text='Copyright © 2020 EEIT2017')
        embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')
        embed.add_field(name='You must register for accessing the server', value='Please follow the instruction in `#rules` channel in the server.', inline=False)

        await member.create_dm()
        await member.dm_channel.send(embed=embed) 

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = discord.utils.get(member.guild.channels, name='join-leave')
        await channel.send(f'__**{member.nick}**__ has left the server.')

def setup(bot):
    bot.add_cog(Event(bot))