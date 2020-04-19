import discord
import json
from discord.ext import commands

class Testcog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def clear(self, ctx, amount=10):
        await ctx.channel.purge(limit=amount) 
    
    '''@commands.command(name="help", description="Returns all commands available")
    async def help(self, ctx):
        helptext = "```"
        for command in self.bot.commands:
            helptext+=f"{command}\n"
        helptext+="```"
        await ctx.send(helptext)''' 

def setup(bot):
    #bot.remove_command('help')
    bot.add_cog(Testcog(bot))   