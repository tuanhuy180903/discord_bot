import discord
import json
from discord.ext import commands
import asyncio

def is_roled(ctx):
    return len(ctx.author.roles)>1

async def create_ttt(channel, user: discord.Member):
    if not user.nick:
        name = user.name
    else:
        name = user.nick
    embed = discord.Embed(
        title = 'Tic-Tac-Toe',
        description = 'Setting up board...',
        colour = discord.Colour.teal()
    )
    embed.set_footer(text='Copyright © 2020 EEIT2017')
    embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')
    dash = '\n\U00002500\U00002500\U00002500\U00002500\U00002500\U00002500\U00002500\U00002500\U00002500\n'
    board = ':one: \U00002502 :two: \U00002502 :three:' + dash + ':four: \U00002502 :five: \U00002502 :six:' + dash + ':seven: \U00002502 :eight: \U00002502 :nine:'
    embed.add_field(name='Board',value=board)
    number = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣']
    message = await channel.send(embed=embed)
    for i in range(len(number)):
        await message.add_reaction(number[i])
    embed.description = f'**{name}** goes first  :o:'
    await message.edit(embed=embed)
    return message.id

async def edit_board(channel, message_id:str, num:int, id: int, emoji: str):
    m_id = int(message_id)
    message = await channel.fetch_message(m_id)
    user = await channel.guild.fetch_member(id)
    embed = message.embeds[0]
    if not user.nick:
        name = user.name
    else:
        name = user.nick
    sym = ''
    if num == 1: 
        sym = ':x:'
        embed.description = f'**{name}** goes next :o:'
    elif num == 2:
        sym = ':o:'
        embed.description = f'**{name}** goes next :x:'

    value = embed.fields[0].value
    if emoji == '1️⃣':
        value = value.replace(':one:',sym)
    elif emoji == '2️⃣':
        value = value.replace(':two:',sym)
    elif emoji == '3️⃣':
        value = value.replace(':three:',sym)
    elif emoji == '4️⃣':
        value = value.replace(':four:',sym)
    elif emoji == '5️⃣':
        value = value.replace(':five:',sym)
    elif emoji == '6️⃣':
        value = value.replace(':six:',sym)
    elif emoji == '7️⃣':
        value = value.replace(':seven:',sym)
    elif emoji == '8️⃣':
        value = value.replace(':eight:',sym)
    elif emoji == '9️⃣':
        value = value.replace(':nine:',sym)

    embed.clear_fields()
    embed.add_field(name='Board',value=value)
    await message.edit(embed=embed)

def check_board(board:dict):
    check_full = True
    for i in board:
        if board[i] == 0:
            check_full = False
            break
    if check_full:
        return 3
    if (board['1️⃣'] == board['2️⃣'] == board['3️⃣']) and (board['1️⃣'] != 0):
        return 1
    elif (board['1️⃣'] == board['4️⃣'] == board['7️⃣']) and (board['1️⃣'] != 0):
        return 1
    elif (board['1️⃣'] == board['5️⃣'] == board['9️⃣']) and (board['1️⃣'] != 0):
        return 1
    elif (board['2️⃣'] == board['5️⃣'] == board['8️⃣']) and (board['2️⃣'] != 0):
        return 1
    elif (board['3️⃣'] == board['6️⃣'] == board['9️⃣']) and (board['3️⃣'] != 0):
        return 1
    elif (board['3️⃣'] == board['5️⃣'] == board['7️⃣']) and (board['3️⃣'] != 0):
        return 1
    elif (board['4️⃣'] == board['5️⃣'] == board['6️⃣']) and (board['4️⃣'] != 0):
        return 1
    elif (board['7️⃣'] == board['8️⃣'] == board['9️⃣']) and (board['7️⃣'] != 0):
        return 1
    else:
        return 0

async def end_board_draw(channel, message_id:str):
    m_id = int(message_id)
    message = await channel.fetch_message(m_id)
    embed = message.embeds[0]
    embed.description = '**Draw**!'
    embed.colour = discord.Colour.default()
    await message.edit(embed=embed)

async def end_board_win(channel, message_id:str, user: discord.User):
    m_id = int(message_id)
    message = await channel.fetch_message(m_id)
    embed = message.embeds[0]
    if not user.nick:
        name = user.name
    else:
        name = user.nick
    embed.description = f'**{name}** wins!'
    embed.colour = discord.Colour.default()
    await message.edit(embed=embed)

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ttt = {}
        self.accept = {}
        self.opponent = {}
        self.status = {}
        self.task_list = []
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            if member.top_role.name != "Teacher":
                return
            voice_name = after.channel.name
            pos = voice_name.find(' ')
            role = discord.utils.get(member.guild.roles, name=voice_name[0:pos]) 
            name = voice_name[0:pos] + '-chat'
            channel = discord.utils.get(member.guild.channels, name=name.lower())
            await channel.send(role.mention)

            if not member.nick:
                namee = member.name
            else:
                namee = member.nick
            embed = discord.Embed(
                title = f'Hello students!',
                description = f'Teacher **{namee}** is teaching in **{voice_name}**.\nPlease click **{voice_name}** on the left side of Discord UI to connect to the classroom.',
                colour = discord.Colour.gold()
            )
            embed.set_footer(text='Copyright © 2020 EEIT2017')
            embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')
            return await channel.send(embed=embed)
        if before.channel is not None and after.channel is None:
            if member.top_role.name == 'Teacher':
                return
            if before.channel.name == 'Voice':
                return
            channel = before.channel
            #channel = discord.utils.get(member.guild.channels, name='chat')
            await channel.edit(sync_permissions=True)

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
        #print(self.ttt)
        if mess_id in question:
            if reaction.emoji == question[mess_id]:
                await uzer.create_dm()
                message = await channel.fetch_message(reaction.message.id)
                embed = message.embeds
                await uzer.dm_channel.send(f'> **{embed[0].description}**\nCongratulations! You chose {reaction.emoji} - the **correct** answer for the question.')
            else:
                await uzer.create_dm()
                message = await channel.fetch_message(reaction.message.id)
                embed = message.embeds
                await uzer.dm_channel.send(f'> **{embed[0].description}**\nUnfortunately, you chose {reaction.emoji} - the **wrong** answer for the question.')
        
        elif mess_id in self.accept:
            if user.id == self.accept[mess_id]:
                if reaction.emoji == '\U00002705':
                    message = await channel.fetch_message(reaction.message.id)
                    embed = message.embeds[0]
                    embed.colour = discord.Colour.green()
                    await message.edit(embed=embed)
                    del self.accept[mess_id]
                    game = await create_ttt(channel, user)
                    self.ttt[str(game)] = user.id
                    self.status[str(game)] = {'1️⃣':0,'2️⃣':0,'3️⃣':0,'4️⃣':0,'5️⃣':0,'6️⃣':0,'7️⃣':0,'8️⃣':0,'9️⃣':0}

                elif reaction.emoji == '\U0000274C':
                    message = await channel.fetch_message(reaction.message.id)
                    embed = message.embeds[0]
                    embed.colour = discord.Colour.red()
                    await message.edit(embed=embed)
                    del self.accept[mess_id]
                    del self.opponent[user.id]
                    if not user.nick:
                        namee = user.name
                    else:
                        namee = user.nick
                    return await channel.send(f'**{namee}** rejects the challenge!')
        
        elif mess_id in self.ttt:
            if user.id == self.ttt[mess_id]:
                if self.status[mess_id][reaction.emoji] != 0:
                    return
                for i in self.opponent:
                    if user.id == self.opponent[i]:
                        self.status[mess_id][reaction.emoji] = 2
                        self.ttt[mess_id] = i
                        check = check_board(self.status[mess_id])
                        await edit_board(channel, mess_id, 1, i, reaction.emoji)
                        if check == 0:
                            return
                        if check == 3:
                            del self.ttt[mess_id]
                            del self.opponent[i]
                            return await end_board_draw(channel,mess_id)
                        else:
                            del self.ttt[mess_id]
                            del self.opponent[i]
                            return await end_board_win(channel,mess_id,user)

                self.status[mess_id][reaction.emoji] = 1
                self.ttt[mess_id] = self.opponent[user.id]
                check = check_board(self.status[mess_id])
                await edit_board(channel, mess_id, 2, self.opponent[user.id], reaction.emoji)
                if check == 0:
                    return
                elif check == 3:
                    del self.ttt[mess_id]
                    del self.opponent[user.id]
                    return await end_board_draw(channel,mess_id)
                else:
                    del self.ttt[mess_id]
                    del self.opponent[user.id]
                    return await end_board_win(channel,mess_id,user)
            
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
                await uzer.dm_channel.send(f'> **{embed[0].description}**\nCongratulations! You chose {reaction.emoji} - the **correct** answer for the question.')
            else:
                await uzer.create_dm()
                message = await channel.fetch_message(reaction.message.id)
                embed = message.embeds
                await uzer.dm_channel.send(f'> **{embed[0].description}**\nUnfortunately, you chose {reaction.emoji} - the **wrong** answer for the question!')

    async def accept_clear(self, mess_id:str, play_id:int):
        await self.bot.wait_until_ready()
        index = len(self.task_list)-1
        while not self.bot.is_closed():
            await asyncio.sleep(30)
            del self.accept[mess_id]
            del self.opponent[play_id]
            self.task_list[index].cancel()

    @commands.command(aliases=['ttt'],help='Play tic-tac-toe with someone.',usage = '<username_to_play>')
    @commands.check(is_roled)
    async def tictactoe(self, ctx, player:discord.Member):
        if player is None:
            return await ctx.send('Please specify the user you wants to play with!')
        if player == ctx.author:
            return await ctx.send('Can\'t use on yourself!')
        if player == self.bot.user:
            return await ctx.send('Can\'t use on bot!')
        if not player.nick:
            name1 = player.name
        else:
            name1 = player.nick  
        for i in self.opponent:
            if self.opponent[i] == ctx.author.id:
                return await ctx.send('You are playing in another board!')
            if self.opponent[i] == player.id:
                return await ctx.send(f'**{name1}** is playing in another board!')
        if player.id in self.opponent:
            return await ctx.send(f'**{name1}** is playing in another board!')
        if ctx.author.id in self.opponent:
            return await ctx.send('You are playing in another board!')
        if not ctx.author.nick:
            name2 = ctx.author.name
        else:
            name2 = ctx.author.nick  
        embed = discord.Embed(
            title = 'Tic-Tac-Toe',
            description = f'{player.mention}, **{name2}** is challenging you for tic-tac-toe.\nPlease add reaction **accept** :white_check_mark: or **reject** :x: below this message!\n__Note__: This invitaion will expire in 30 seconds.',
            colour = discord.Colour.blue()
        )
        embed.set_footer(text='Copyright © 2020 EEIT2017')
        embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')
        message = await ctx.send(embed=embed)
        await message.add_reaction('\U00002705')
        await message.add_reaction('\U0000274C')
        self.accept[str(message.id)] = player.id
        self.bg_task = self.bot.loop.create_task(self.accept_clear(str(message.id),player.id))
        self.task_list.append(self.bg_task)
        self.opponent[player.id] = ctx.author.id

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title = f'Welcome to {member.guild.owner.name}\'s server!',
            description = f'Hi __**{member.name}**__! This is a teaching server run by {self.bot.user.name}.',
            colour = discord.Colour.green()
        )

        embed.set_footer(text='Copyright © 2020 EEIT2017')
        embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')
        embed.add_field(name='You must register for accessing the server', value='Please follow the instruction in **`#rules`** channel in the server.', inline=False)

        await member.create_dm()
        await member.dm_channel.send(embed=embed) 

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.nick is not None:
            channel = discord.utils.get(member.guild.channels, name='join-leave')
            await channel.send(f'**{member.nick}** has left the server.')

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        if role.name == 'Teacher' or role.name == 'Student':
            return
        guild = role.guild
        stu = discord.utils.get(guild.roles, name='Student')
        await stu.edit(position=1)

def setup(bot):
    bot.add_cog(Event(bot))