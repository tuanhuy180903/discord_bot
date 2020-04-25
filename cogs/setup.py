import discord
from discord.ext import commands
import database as db
import random
import asyncio

def is_everyone(ctx):
        return len(ctx.author.roles)==1

def format_name(name:str):
    if name.find('.') != -1:
        pos = name.find('.')
        return name[0].upper() + name[1:pos+1].lower() + name[pos+1].upper() + name[pos+2:].lower()
    else:
        return name[0].upper() + name[1:].lower()

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.test = []

    @commands.command(help='Set up a teaching server.',description='Only use it once when creating the server.\nAfter that, you can ignore this command.')
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        guild = ctx.guild
        #db.createdb('bot.db','student')
        await self.rename(ctx)
        existing_role = discord.utils.get(guild.roles, name='Teacher') 
        if not existing_role:
            await guild.create_role(name='Teacher',permissions=discord.Permissions(administrator=True),hoist=True,mentionable=True,colour=discord.Colour.red())
        await ctx.author.add_roles(discord.utils.get(guild.roles, name='Teacher'))

        def_perms = discord.Permissions(read_messages=True, read_message_history=True,send_messages=True)
        await guild.default_role.edit(permissions=def_perms)

        perms = discord.Permissions(read_messages=True,send_messages=True,send_tts_messages=True,read_message_history=True,connect=True,speak=True,use_voice_activation=True,add_reactions=True,embed_links=True,attach_files=True) 
        existing_role = discord.utils.get(guild.roles, name='Student') 
        if not existing_role:
            await guild.create_role(name='Student',permissions=perms,hoist=True,mentionable=True,colour=discord.Colour.green())
        
        await self.rules(ctx)

        st_role = discord.utils.get(guild.roles, name='Student')
        for channel in guild.channels:
            if not channel.name == 'rules':
                await channel.set_permissions(guild.default_role, read_messages=False)
                await channel.set_permissions(st_role, read_messages=True)

        await self.join_leave(ctx)  

        await self.create_invite(ctx)

        await ctx.send('Setup completed')

    @commands.command(brief='Included in setup, you can ignore this.')
    @commands.has_permissions(administrator=True)
    async def join_leave(self, ctx):
        guild = ctx.guild
        existing_channel = channel = discord.utils.get(guild.channels, name='join-leave')
        if not existing_channel:
            await guild.create_text_channel(name='join-leave', topic='notification channel for student joining/leaving this server')
        channel = discord.utils.get(guild.channels, name='join-leave')
        await guild.edit(system_channel=channel, system_channel_flags=discord.SystemChannelFlags(join_notifications=False))
        for role in guild.roles:
            if (role.name != 'Teacher'):
                await channel.set_permissions(role, read_messages=True,send_messages=False,add_reactions=False,embed_links=False)
        await channel.set_permissions(guild.default_role, read_messages=False)

    @commands.command(brief='Register as a student in this server', usage='<student_name> <class_name>', description='Only used once by a user when he/she joins the server for the first time.\nThen he/she would be regconized as a student to access the server completely.')
    @commands.check(is_everyone)
    async def signup(self, ctx, stu_name:str, *, class_name:str):
        if class_name.find(' ')>0:
            return
        guild = ctx.guild
        stu_role = discord.utils.get(guild.roles,name='Student')
        await ctx.author.add_roles(stu_role)
        stu_name = format_name(stu_name)
        await ctx.author.edit(nick=stu_name)

        class_name = class_name.upper()
        existing_role = discord.utils.get(guild.roles, name=class_name)
        if not existing_role:
            await guild.create_role(name=class_name,hoist=True,mentionable=True,colour=discord.Colour.purple())
        
        embed = discord.Embed(
            title = f'Thanks for registering {stu_name}!',
            description = 'The default prefix is `;`\nPlease use `;help` to see all commands available for you.',
            colour = discord.Colour.green()
        )
        embed.set_footer(text='Copyright © 2020 EEIT2017')
        embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')
        await ctx.author.create_dm()
        await ctx.author.dm_channel.send(embed=embed)

        new_role = discord.utils.get(guild.roles,name=class_name)
        await ctx.author.add_roles(new_role)

        existing_category = discord.utils.get(guild.categories, name=class_name)
        if not existing_category:
            await guild.create_category(name=class_name)
            category = discord.utils.get(guild.categories, name=class_name)
            await category.set_permissions(new_role, read_messages=True)
            for role in guild.roles:
                if not new_role == role:
                    await category.set_permissions(role, read_messages=False, speak=False)
            text_name = class_name.lower() + '-chat'
            voice_name = class_name + ' Classroom'
            await category.create_text_channel(name=text_name, topic=f'text chat channel only for students in class {class_name}')
            await category.create_voice_channel(name=voice_name)
        
        channel = discord.utils.get(guild.text_channels,name='join-leave')
        await channel.send(f'Welcome **{stu_name}**!')

    @commands.command(brief='Included in setup, you can ignore this.')
    @commands.has_permissions(administrator=True)
    async def rename(self, ctx):
        guild = ctx.guild
        category = discord.utils.get(guild.categories, name='Text Channels')
        if not category is None:
            await category.edit(name='General Channels')
        category = discord.utils.get(guild.categories, name='General Channels')
        channel = discord.utils.get(guild.voice_channels,name='General')
        if not channel is None:
            await channel.edit(name='Voice', category=category)
        category = discord.utils.get(guild.categories, name='Voice Channels')
        if not category is None:    
            await category.delete()
        channel = discord.utils.get(guild.text_channels, name='general')
        if not channel is None:
            await channel.edit(name='chat', topic='text chat channel for students of all classes')

    @commands.command(brief='Included in setup, you can ignore this.')
    @commands.has_permissions(administrator=True)
    async def rules(self, ctx):
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.text_channels, name='rules')
        st_role = discord.utils.get(guild.roles, name='Student') 
        if not existing_channel:
            await guild.create_text_channel('rules')
            channel = discord.utils.get(guild.text_channels, name='rules')
            embed = discord.Embed(
                title = f'Hello, I\'m {self.bot.user.name}!',
                description = f'You must sign up for a student of **{ctx.author.name}**\'s server.',
                colour = discord.Colour.green()
            )
            #embed.set_author(name=ctx.author.name)
            embed.set_footer(text='Copyright © 2020 EEIT2017')
            embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')
            embed.add_field(name='Please type', value='`;signup <your_name> <your_class>`', inline=True)
            example = '`;signup Huy eeit2017`\n`;signup T.Huy CS2016`'
            embed.add_field(name='Please follow the correct format like examples below:', value=example, inline=False)
            embed.add_field(name='__**Note**__',value='- If you use bad words in any channels (including registering in this channel), your message will be deleted immediately!\n- There must be no whitespaces in your name and your class name.', inline=False)
            message = await channel.send(embed=embed)
            await message.pin()

        channel = discord.utils.get(guild.text_channels, name='rules')
        await channel.set_permissions(st_role, read_messages=True, send_messages=False, add_reactions=False, embed_links=False)

    @commands.command(aliases=['cr_inv'],brief='Create invites to this server.', description='Included in setup.\nAfter using this command, bot will automatically send the invite URL to you via DM Channel.')
    @commands.has_role('Teacher')
    async def create_invite(self, ctx):
        channel = discord.utils.get(ctx.guild.channels, name='rules')
        invite = await channel.create_invite(max_age=43200)
        await ctx.author.create_dm()
        await ctx.author.dm_channel.send(invite)

    async def change_embed(self, num):
        await self.bot.wait_until_ready()
        index = len(self.test)-1
        while not self.bot.is_closed():
            await asyncio.sleep(5)
            print(num)
            self.test[index].cancel()
            

    @commands.command(description='Only for the developer!') 
    @commands.is_owner()
    async def pinn(self, ctx):
        embed = discord.Embed(
            title = 'Test',
            description = 'Start',
            colour = discord.Colour.red()
        )
        message = await ctx.send(embed=embed)
        kk = len(self.test)
        number = random.choice(range(1,20))
        self.bg_task = self.bot.loop.create_task(self.change_embed(number))
        self.test.append(self.bg_task)

    @pinn.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            return await ctx.send('Sorry, you found a developer-only command!')

    @commands.command(description='Only for the developer!')
    @commands.is_owner()
    async def stop(self, ctx):
        print(self.test)
        for task in self.test:
            task.cancel()
    
    @stop.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            return await ctx.send('Sorry, you found a developer-only command!')

    @commands.command(brief='Delete everything related to a class.', description='Please use this command carefully!\n It will delete everything related to a class including role and channels and kick students out of that class.\nYou have to assign students to another class manually.')
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx, class_name:str):
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=class_name.upper())
        if role is not None:
            await role.delete()
        for channel in guild.channels:
            cname = channel.name.lower()
            if cname == class_name:
                await channel.delete()
        
        return await ctx.send('Delete completed!')

def setup(bot):
    bot.add_cog(Setup(bot))

'''list_name = db.fetch('bot.db','name')
        list_class = db.fetch('bot.db', 'class')
        if not class_name.upper() in list_class:
            await ctx.send('Clssass is not found in database')
            return'''
'''@commands.command(aliases=['m'])
    @commands.has_permissions(administrator=True)
    async def moverole(self, ctx, ab, pos: int):
        role = discord.utils.get(ctx.guild.roles, name=ab)
        try:
            await role.edit(position=pos)
            await ctx.send("Role moved.")
        except discord.Forbidden:
            await ctx.send("You do not have permission to do that")
        except discord.HTTPException:
            await ctx.send("Failed to move role")
        except discord.InvalidArgument:
            await ctx.send("Invalid argument")'''
'''embed = discord.Embed(
            title = f'Hello! I am ',
            colour = discord.Colour.green()
        )
        dash = '\n\U00002500\U00002500\U00002500\U00002500\U00002500\U00002500\U00002500\U00002500\U00002500\n'
        board = ':one: \U00002502 :two: \U00002502 :three:' + dash + ':four: \U00002502 :five: \U00002502 :six:' + dash + ':seven: \U00002502 :eight: \U00002502 :nine:'
        embed.set_footer(text='Copyright © 2020 EEIT2017')
        embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')
        embed.add_field(name='Please type', value=board, inline=True)
        embed1 = embed.copy()
        message = await ctx.send(embed=embed)
        embed1.colour = discord.Colour.dark_red()
        await message.edit(embed=embed1)
        ss = embed1.fields[0].value
        ss = ss.replace('\U00002502','')
        ss = ss.replace('\U00002500','')
        ss = ss.replace(' ','')
        ss = ss.replace('\n','')
        print(ss)'''