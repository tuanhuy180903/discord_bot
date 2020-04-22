import discord
import json
from discord.ext import commands

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        key = str(member.id)
        with open('./cogs/prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes[key] = ';'
        with open('./cogs/prefixes.json', 'w') as f:
            json.dump(prefixes, f , indent=4)
        
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        key = str(member.id)
        with open('./cogs/prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes.pop(key)
        with open('./cogs/prefixes.json', 'w') as f:
            json.dump(prefixes, f , indent=4)

    @commands.command(aliases=['prefix'], help= 'Change prefix', description = 'Change bot''s current prefix to a new one')
    async def change_prefix(self, ctx, new_prefix):
        key = str(ctx.author.id)
        with open('./cogs/prefixes.json', 'r') as f:
            prefixes = json.load(f)

        old_prefix = prefixes[key]
        prefixes[key] = new_prefix
        with open('./cogs/prefixes.json', 'w') as f:
            json.dump(prefixes, f , indent=4)    
        
        await ctx.send(f'Bot prefix changes from {old_prefix} to {new_prefix}')

def setup(bot):
    
    bot.add_cog(Prefix(bot))