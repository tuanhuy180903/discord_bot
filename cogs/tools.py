import discord
import json
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

class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #des = 'fdsaf'
    
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

    @commands.command(aliases=['cl'], help='Check attendances of a class')
    @commands.has_role('Student')
    async def check_list(self, ctx, class_name):
        class_name = class_name.upper()
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
            await ctx.send('Unknown class name')
            return
        if not existing_role.members:
            await ctx.send('There is no student in this class')
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

    @commands.command(aliases=['ms'])
    @commands.has_role('Teacher')
    async def missing(self, ctx):
        if not ctx.author.voice:
            return await ctx.send('You haven\'t been in a voice channel yet!')
        channel_name = ctx.author.voice.channel.name
        class_name = channel_name.strip(' Classroom')
        '''CHECK GENERAL VOICE CHANNEL'''
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

    '''@missing.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRole):
            return await ctx.send('You do not have specific roles to use this command')
        if isinstance(error, commands.errors.CheckFailure):
            return await ctx.send('You haven\'t been in a voice channel yet!')'''

    @commands.command(aliases=['um'])
    @commands.has_role('Teacher')
    async def unmute(self, ctx, stu_name):
        if not ctx.author.voice:
            return await ctx.send('You haven\'t been in a voice channel yet!')
        if stu_name[0] == '<':
            stu_name = stu_name[3:len(stu_name)-1]
            student = ctx.guild.get_member(int(stu_name))
            if student == ctx.guild.owner:
                await ctx.send('Can\'t use on yourself.')
                return
            stu_name = student.nick
        else:
            student = discord.utils.get(ctx.guild.members, nick=stu_name)
        if not student.voice:
            await ctx.send(f'**{stu_name}** hasn\'t been in a voice channel yet.')
            return
        await student.edit(mute=False)
        await ctx.send(f'**{stu_name}** is un-muted.')

    @commands.command(aliases=['q'])
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
            await ctx.send(f'You have not specified the correct answer yet!\n Please use `{ctx.prefix}help question` for format the command exactly!')
        ans = ('\n'.join(ans))

        embed = discord.Embed(
            title = f'A question from Teacher {ctx.author.name}:',
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

    @commands.command()
    @commands.has_role('admin')
    async def emoji(self, ctx, search_term):
        bot = ctx.bot
        if isinstance(search_term, int):
            return bot.get_emoji(search_term)
        if isinstance(search_term, str):
            return discord.utils.get(bot.emojis, name=search_term) 
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
