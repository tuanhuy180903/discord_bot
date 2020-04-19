import discord
from discord.ext import commands
import database as db

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

    @commands.command(help='Set up a teaching server')
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        guild = ctx.guild
        #db.createdb('bot.db','student')

        existing_role = discord.utils.get(guild.roles, name='Teacher') 
        if not existing_role:
            await guild.create_role(name='Teacher',permissions=discord.Permissions(administrator=True),hoist=True,mentionable=True,colour=discord.Colour.red())
        await ctx.author.add_roles(discord.utils.get(guild.roles, name='Teacher'))

        def_perms = discord.Permissions(read_messages=True, read_message_history=True,send_messages=True)
        await guild.default_role.edit(permissions=def_perms)

        perms = discord.Permissions(read_messages=True,send_messages=True,send_tts_messages=True,read_message_history=True,connect=True,speak=True,use_voice_activation=True,add_reactions=True,embed_links=True) 
        existing_role = discord.utils.get(guild.roles, name='Student') 
        if not existing_role:
            await guild.create_role(name='Student',permissions=perms,hoist=True,mentionable=True,colour=discord.Colour.green())
        
        st_role = discord.utils.get(guild.roles, name='Student')
        for channel in guild.channels:
            if not channel.name == 'rules':
                await channel.set_permissions(guild.default_role, read_messages=False)
                await channel.set_permissions(st_role, read_messages=True)

        await st_role.edit(position=1)

        await self.join_leave(ctx)
        '''RUN RULES'''
        await ctx.send('Setup completed')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def join_leave(self, ctx):
        guild = ctx.guild
        existing_channel = channel = discord.utils.get(guild.channels, name='join-leave')
        if not existing_channel:
            await guild.create_text_channel(name='join-leave')
        channel = discord.utils.get(guild.channels, name='join-leave')
        await guild.edit(system_channel=channel)
        for role in guild.roles:
            if (role.name != 'Teacher'):
                await channel.set_permissions(role, read_messages=True,send_messages=False,add_reactions=False,embed_links=False)
        await channel.set_permissions(guild.default_role, read_messages=False)

    @commands.command()
    @commands.check(is_everyone)
    async def signup(self, ctx, stu_name:str, class_name:str):
        guild = ctx.guild
        stu_role = discord.utils.get(guild.roles,name='Student')
        await ctx.author.add_roles(stu_role)
        stu_name = format_name(stu_name)
        await ctx.author.edit(nick=stu_name)
        class_name = class_name.upper()
        existing_role = discord.utils.get(guild.roles, name=class_name)
        if not existing_role:
            print('Role created')
            await guild.create_role(name=class_name,hoist=True,mentionable=True,colour=discord.Colour.purple())
        
        '''await new_role.edit(position=2)'''
        await stu_role.edit(position=1)
        embed = discord.Embed(
            title = f'Thanks for registering {stu_name}!',
            description = 'The default prefix is `;`. Please use `;help` to see all commands available for you.',
            colour = discord.Colour.green()
        )
        embed.set_footer(text='Copyright © 2020 EEIT2017')
        embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')
        await ctx.author.create_dm()
        await ctx.author.dm_channel.send(embed=embed)

        new_role = discord.utils.get(guild.roles,name=class_name)
        print(new_role.id)
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
            await category.create_text_channel(name=text_name)
            await category.create_voice_channel(name=voice_name)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rules(self, ctx):
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.text_channels, name='rules')
        if not existing_channel:
            await guild.create_text_channel('rules')
            channel = discord.utils.get(guild.text_channels, name='rules')
            embed = discord.Embed(
                title = f'Hello! I am {self.bot.user.name}',
                description = f'You must sign up for a student of {ctx.author.name}\'s server',
                colour = discord.Colour.green()
            )
            #embed.set_author(name=ctx.author.name)
            embed.set_footer(text='Copyright © 2020 EEIT2017')
            embed.set_thumbnail(url='https://vgu.edu.vn/cms-vgu-theme-4/images/cms/vgu_logo.png')
            embed.add_field(name='Please type', value='`;signup <your_name> <your_class>`', inline=True)
            example = '`;signup Huy eeit2017`\n`;signup T.Huy CS2016`'
            embed.add_field(name='Please follow the correct format like examples below:', value=example, inline=False)
            message = await channel.send(embed=embed)
            await message.pin()
        channel = discord.utils.get(guild.text_channels, name='rules')
        role = discord.utils.get(guild.roles, name='Student') 
        await channel.set_permissions(role, read_messages=True, send_messages=False, add_reactions=False, embed_links=False)

    @commands.command(aliases=['invite'])
    @commands.has_role('Teacher')
    async def create_invite(self, ctx):
        channel = discord.utils.get(ctx.guild.channels, name='rules')
        invite = await channel.create_invite(max_age=3600)
        await ctx.author.create_dm()
        await ctx.author.dm_channel.send(invite)

    @commands.command() 
    @commands.has_permissions(administrator=True)
    async def pinn(self, ctx):
        embed = discord.Embed(
            title = 'Title',
            description = 'This is a description.',
            colour = discord.Colour.green()
        )
        message = await ctx.send(embed=embed)
        
        new_message = await ctx.fetch_message(701434573174734939)
        print(new_message)

def setup(bot):
    bot.add_cog(Setup(bot))

'''list_name = ['z','x','c','s','d']
        stu_name = ('\n'.join(list_name))
        print(len(list_name))
        is_online = [
            ':white_check_mark:'
            for _ in range(len(list_name))
        ]
        list_online = ('\n'.join(is_online))'''

'''list_name = db.fetch('bot.db','name')
        list_class = db.fetch('bot.db', 'class')
        if not class_name.upper() in list_class:
            await ctx.send('Clssass is not found in database')
            return'''