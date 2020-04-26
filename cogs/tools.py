import discord
import json
import random
from discord.ext import commands

online = [discord.Status.online, discord.Status.idle, discord.Status.dnd]

def is_roled(ctx):
    return len(ctx.author.roles)>1

def get_dirty(file):
    with open(file,'r') as f:
        dirty = f.readlines()
    for i in range(len(dirty)):
        dirty[i] = dirty[i].strip('\n')
    return dirty
async def in_voice(ctx):
    return ctx.author.voice

async def in_chat(ctx):
    role = ctx.author.top_role
    channel_name = role.name.lower() + '-chat' 
    if ctx.channel.name != channel_name:
        await ctx.send(f'You are not in the chatting channel of **{role.name}** classroom.')
        return False
    else:
        return True

def have_prefix(id):
    with open('./cogs/prefixes.json', 'r') as f:
        prefix = json.load(f)
    return prefix[id]

class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dice_list = {}
    
    @commands.command(aliases=['bw'], brief='Show/add bad words', help='Show a list of bad words banned in this server when {list_of_bad_words} is blank.\nAdd a list of bad words when {list_of_bad_words} is filled.',description='Examples:\n;bw\n;bw abcd, efgh',usage='{list_of_bad_words}')
    @commands.check(is_roled)
    async def bad_word(self, ctx, *, bad_words=None):
        role_tc = discord.utils.get(ctx.guild.roles, name='Teacher')
        if not bad_words:
            with open('dirty.txt','r') as f:
                list_dirty = f.readlines()
            list_dirty = (''.join(list_dirty))
            list_dirty = list_dirty.rstrip('\n')
            embed = discord.Embed(
                title = 'Bad words banned are:',
                description = list_dirty,
                colour = discord.Colour.red()
            )
            embed.set_footer(text='Copyright © 2020 EEIT2017')
            embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')

            await ctx.send(embed=embed)
        else:
            if role_tc in ctx.author.roles:
                new_list = bad_words.split(',')
                list_dirty = get_dirty('dirty.txt')
                with open('dirty.txt','a') as f:
                    for i in range(len(new_list)):
                        new_list[i] = new_list[i].lstrip()
                        if new_list[i] in list_dirty:
                            await ctx.send(f'The word `{new_list[i]}` is on the list already.')
                            continue
                        f.write(new_list[i] + '\n')
                
                await ctx.send(f'Added a list of {str(new_list)} bad words')
            else:
                await ctx.send('You are not allowed to use this command')

    @commands.command(aliases=['cl'], brief='Check attendances of a class', description='To check out a list of signed-up students of a class, you can use this command and for example:\n;cl EEIT2017\n;check_list ba2015')
    @commands.has_permissions(administrator=True)
    async def check_list(self, ctx, class_name):
        class_name = class_name.upper()
        if class_name == 'BOT':
            return await ctx.send('Can\'t use on bot!')
        embed = discord.Embed(
            title = f'List of {class_name} students',
            description = f'Use `{ctx.prefix}missing` to show a list of students missing when you are in a classroom.',
            colour = discord.Colour.blurple()
        )
        stu_name= []
        is_online = []
        #append a role when new signup
        existing_role = discord.utils.get(ctx.guild.roles,name=class_name)
        if not existing_role:
            await ctx.send('Invalid class name.')
            return
        if not existing_role.members:
            await ctx.send(f'There is no student in class {class_name}.')
            return
        for member in existing_role.members:
            if not member.nick:
                stu_name.append(member.name)
            else:
                stu_name.append(member.nick)
            if member.status in online:
                is_online.append(':white_check_mark:')
            else:
                is_online.append(':x:')
        stu_name = ('\n'.join(stu_name))  
        is_online = ('\n'.join(is_online)) 
        embed.set_footer(text='Copyright © 2020 EEIT2017')
        #embed.set_author(name=ctx.author.name,icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')
        embed.add_field(name='**Student name**',value=stu_name,inline=True)
        embed.add_field(name='**Online**',value=is_online,inline=True)
        
        await ctx.send(embed=embed)
    
    @check_list.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('You are missing permissions to use this command!')
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f'You are missing required arguments for this command!\nTo find out the right way to use this command, type: `{ctx.prefix}help` cl')
            
    @commands.command(aliases=['ms'], brief='Show a list of students who are absent from classroom.', description='First, you have to connect to a voice channel.\nThen, type ;ms or ;missing to show a list of students who are absent from classroom.')
    @commands.has_permissions(administrator=True)
    async def missing(self, ctx):
        if not ctx.author.voice:
            return await ctx.send('You haven\'t been in a voice channel yet!')
        channel_name = ctx.author.voice.channel.name
        if channel_name == 'Voice':
            return await ctx.send('Can\'t use in here!')
        class_name = channel_name.strip(' Classroom')
        exist_role = discord.utils.get(ctx.guild.roles,name=class_name)
        mention = []
        for member in exist_role.members:
            if not member.voice:
            #if member.voice.channel.name == channel_name:
                mention.append(member.mention)
        if mention == []:
            await ctx.send(f'There is no students missing in {class_name} classroom.')
            return
        mention = ('\n'.join(mention))
        embed = discord.Embed(
            title = f'Students missing in {class_name} classroom are:',
            description = mention,
            colour = discord.Colour.blue()
        )
        embed.set_footer(text='Copyright © 2020 EEIT2017')
        embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')
        await ctx.send(embed=embed)

    @missing.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('You are missing permissions to use this command!')

    @commands.command(aliases=['um'], brief='Unmute a student', description='When you are teaching in a voice channel and there is a student who wants to speak, let him/her talk by typing a command likes this example:\n;um @Phuoc\nor\n;ummute Phuoc')
    @commands.has_permissions(administrator=True)
    async def unmute(self, ctx, student: discord.Member):
        if not ctx.author.voice:
            return await ctx.send('You haven\'t been in a voice channel yet!')
        if student == ctx.author:
            return await ctx.send('Can\'t use on yourself!')
        if student == self.bot.user:
            return await ctx.send('Can\'t use on bot!')
        if not student.voice:
            return await ctx.send(f'**{student.nick}** hasn\'t been in a voice channel yet.')

        await student.edit(mute=False)
        channel = ctx.author.voice.channel
        await channel.set_permissions(student, speak=True, stream=True)
        await ctx.send(f'**{student.nick}** is un-muted.')

    @unmute.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('You are missing permissions to use this command!')
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f'You are missing required arguments for this command!\nTo find out the right way to use this command, type: `{ctx.prefix}help` um')

    @commands.command(aliases=['q'], brief='Public a multiple-choice question', description='To release a multiple choice question, you can follow this example:\n;q 1+1=2? .right, wrong\nRemember to put a dot "." before the right answer to specify it.', usage='<question>? {list_of_answers}')
    @commands.check(is_roled)
    async def question(self, ctx, *, qa:str):
        await ctx.channel.purge(limit=1)
        list_choice = ['a:', 'b:', 'c:', 'd:', 'e:', 'f:']
        list_reaction = ['\U0001F1E6', '\U0001F1E7', '\U0001F1E8', '\U0001F1E9', '\U0001F1EA', '\U0001F1EB']
        qs, ans = qa.split('?')
        ans = ans.split(',')
        choice = ''
        length = len(ans)
        cor_ans = -1
        for i in range(length):
            ans[i] = ans[i].lstrip()
            if ans[i].startswith('.'):
                cor_ans = i
                ans[i] = ans[i].lstrip('.')
            choice += ':regional_indicator_' + list_choice[i] + '\n'
        if cor_ans == -1:
            await ctx.send(f'You have not specified the correct answer yet!\n Please use `{ctx.prefix}help question` to format the command exactly!')
        ans = ('\n'.join(ans))
        if not ctx.author.nick:
            namee = ctx.author.name
        else:
            namee = ctx.author.nick
        embed = discord.Embed(
            title = f'A question from Teacher {namee}:',
            description = qs + '?',
            colour = discord.Colour.orange()
        )
        embed.add_field(name='Choice',value=choice, inline=True)
        embed.add_field(name='Answer', value=ans)
        embed.set_footer(text='Copyright © 2020 EEIT2017')
        embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')
        #:regional_indicator_a: 
        message = await ctx.send(embed=embed)
        with open('./cogs/question.json','r') as f:
            question = json.load(f)

        question[message.id] = list_reaction[cor_ans]

        with open('./cogs/question.json','w') as f:
            json.dump(question, f, indent=4)

        for i in range(length):
            await message.add_reaction(list_reaction[i])
    @question.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f'You are missing required arguments for this command!\nTo find out the right way to use this command, type: `{ctx.prefix}help` q')

    @commands.command(brief='Invite a class to that classroom.',description='After using this command, bot will automatically send invites to students of the class via DM Channel.')
    @commands.has_permissions(administrator=True)
    async def invite(self, ctx, class_name):
        guild = ctx.guild
        class_name = class_name.upper()
        if class_name == 'BOT':
            return await ctx.send('Can\'t use on bot!')
        role = discord.utils.get(guild.roles,name=class_name)
        if not role:
            return await ctx.send('Invalid class name.')
        if not role.members:
            return await ctx.send(f'There is no student in class {class_name}.')

        voice_name = class_name + ' Classroom'
        voice_channel = discord.utils.get(guild.voice_channels,name=voice_name)
        print(voice_channel)
        invite_link = await voice_channel.create_invite(max_age=3600)
        print(invite_link)
        embed = discord.Embed(
                title = 'Hello!',
                description = f'Teacher **{ctx.author.name}** is going to teach in **{voice_name}** in couple minutes.\nPlease follow the link below to connect to the classroom.\n{invite_link}',
                colour = discord.Colour.gold()
            )
        embed.set_footer(text='Copyright © 2020 EEIT2017')
        embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')
        for member in role.members:
            if member.voice is not None:
                if member.voice.channel == voice_channel:
                    return
            embed.title = f'Hello {member.nick}!'
            await member.create_dm()
            await member.dm_channel.send(embed=embed)
        return await ctx.send(f'Invited {class_name}!')

    @invite.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('You are missing permissions to use this command!')
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f'You are missing required arguments for this command!\nTo find out the right way to use this command, type: `{ctx.prefix}help` invite')


    @commands.command(aliases=['clr'], brief='Clear texts in a chat channel', description='To clear texts in a chat channel, type this:\n;clear 20\nor\n;clr 5\nIf the amout of lines is not specified, bot will automatically delete 10 lines.')
    @commands.has_permissions(manage_channels=True)
    async def clear(self, ctx, amount=10):
        await ctx.channel.purge(limit=amount)

    @clear.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('You are missing permissions to use this command!')

    @commands.command(brief='Kick member.', description='To kick a member out of this server, use this command, for example:\n;kick @Phuoc')
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if member == ctx.author:
            return await ctx.send('Can\'t use on yourself!')
        if member == self.bot.user:
            return await ctx.send('Can\'t use on bot!')
        await member.kick(reason=reason)
    
    @kick.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('You are missing permissions to use this command!')
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f'You are missing required arguments for this command!\nTo find out the right way to use this command, type: `{ctx.prefix}help` kick')

    @commands.command(brief='Ban member.', description='To ban a member from this server, use this command, for example:\n;ban @Phuoc')
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, member: discord.Member, *, reason='Annoying'):
        if member == ctx.author:
            return await ctx.send('Can\'t use on yourself!')
        if member == self.bot.user:
            return await ctx.send('Can\'t use on bot!')
        await member.ban(reason=reason)
    
    @ban.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('You are missing permissions to use this command!')
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f'You are missing required arguments for this command!\nTo find out the right way to use this command, type: `{ctx.prefix}help` ban')

    @commands.command(
        brief='Unban member.',  
        description='To unban a member. First, you have to know the member\'s name and discriminator. Then use this command, for example:\n;unban Pidv#0671', 
        usage='<user_name>#<user_discriminator>')
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                return await ctx.guild.unban(user)

    @unban.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('You are missing permissions to use this command!')
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f'You are missing required arguments for this command!\nTo find out the right way to use this command, type: `{ctx.prefix}help` unban')

    @commands.command(aliases=['r'], brief='Simulates rolling dice.', description='If [player] is left blank, it will simulate rolling dice. Otherwise, it will challenge someone to roll a dice.')
    @commands.check(is_roled)
    async def roll(self, ctx, player:discord.Member=None):
        dice = random.choice(range(1, 7))
        if player == ctx.author:
            return await ctx.send('Can\'t use on yourself!')
        if player == self.bot.user:
            return await ctx.send('Can\'t use on bot!')
        if not ctx.author.nick:
            name = ctx.author.name
        else:
            name = ctx.author.nick
        await ctx.send(f':game_die: **|** **{name}** rolls a 6-sided dice and it\'s a ...**{dice}**!')
        if player is not None:
            if ctx.author.id in self.dice_list:
                if dice > self.dice_list[ctx.author.id]:
                    await ctx.send('> You are the **winner**!')
                elif dice < self.dice_list[ctx.author.id]:
                    await ctx.send('> You are the **loser**!')
                else:   
                    await ctx.send('> **Draw**!')
                self.dice_list.pop(ctx.author.id)
            self.dice_list[player.id] = dice
            await ctx.send(f'{player.mention}, **{name}** is challenging you for rolling a dice.\n> Use command **`{have_prefix(str(player.id))}roll`** to join!')
        else:
            if ctx.author.id in self.dice_list:
                if dice > self.dice_list[ctx.author.id]:
                    await ctx.send('> You are the **winner**!')
                elif dice < self.dice_list[ctx.author.id]:
                    await ctx.send('> You are the **loser**!')
                else:   
                    await ctx.send('> **Draw**!')
                self.dice_list.pop(ctx.author.id)
        print(self.dice_list)

def setup(bot):
    bot.add_cog(Tools(bot))

'''@commands.command(aliases=['jj'])
    @commands.has_role('Student')
    @commands.check(in_chat)
    async def join(self, ctx):
        role = ctx.author.top_role
        if not ctx.guild.owner.voice:
            await ctx.send(f'Teacher hasn\'t been in **{role.name}** Classroom yet!')
            return
        voice_channel = ctx.guild.owner.voice.channel
        channel_name = role.name + ' Classroom'
        if voice_channel.name != channel_name:
            await ctx.send(f'Teacher hasn\'t been in **{role.name}** Classroom yet!')
            return
        client = await voice_channel.connect()

        await ctx.send(client.user)
        await client.disconnect()'''
'''@commands.command(aliases=['dm'],brief='Create a DM to someone.',description='')
    @commands.check(is_roled)
    async def createdm(self, ctx, user: discord.Member):
        if not user.nick:
            namee1 = user.name
        else:
            namee1 = user.nick
        if not ctx.author.nick:
            namee2 = ctx.author.name
        else:
            namee2 = ctx.author.nick    
        await user.create_dm()
        await user.dm_channel.send(f'Hello **{namee1}**!\n**{namee2}** wants to contact you, please respond this message.')
'''

'''if stu_name[0] == '<':
            stu_name = stu_name[3:len(stu_name)-1]
            student = ctx.guild.get_member(int(stu_name))
            if student == ctx.author:
                await ctx.send('Cant use on yourself.')
                return
            stu_name = student.nick
        else:
            student = discord.utils.get(ctx.guild.members, nick=stu_name)'''