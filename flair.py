# fun commands start here
# say, custc, snipe, esnipe, choose, who, howgay, rps, 8ball, roulette, trivia, quote
import discord
import os
import csv
from discord.ext import commands
from keep_alive import keep_alive
import random
import pandas as pd
import asyncio
import datetime
import requests
import json
import urllib.parse
from utils import *

# flair commands start here
# addf, delf, lf, im
class Flair(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='addflair', aliases=['addf'])
    async def addflair(self, ctx, role: discord.Role):
        try:
            if not ctx.author.guild_permissions.administrator:
                return await ctx.reply('Wups! Only administrators can use this command...', mention_author=False)
            if role.position >= ctx.me.top_role.position:
                return await ctx.reply("Wups! I can't add this role as a flair because it is above my highest role...", mention_author=False)
            if role.name in lists["flairs"].keys():
                return await ctx.reply(f"Wups! '{role.name}' is already a flair...", mention_author=False)
            
            with open('flairs.csv', 'a', newline='') as csvfile:
                fieldnames = ['role_name', 'role_id']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames) 
                if file_checks["flairs"]:
                    writer.writeheader()
                writer.writerow({'role_name': role.name, 'role_id': role.id})
            create_list("flairs")
            await ctx.message.add_reaction('✅')
            await asyncio.sleep(3)
            return await ctx.message.delete()
        except:
            return await ctx.reply('Wups! Something went wrong. Try doing `!w addflair @Role`...', mention_author=False)

    @commands.command(name='deleteflair', aliases=['delf'])
    async def deleteflair(self, ctx, role:discord.Role):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.reply('Wups, you do not have the required permissions...', mention_author=False)
        if not role.name in list(lists["flairs"].keys()):
            return await ctx.reply('Wups! This role is not a flair...', mention_author=False)
        if len(list(lists["flairs"].keys())) == 0:
            return await ctx.reply('Wups! There are no flairs to delete in the first place...', mention_author=False)
        
        flairs = pd.read_csv('flairs.csv')
        flairs = flairs[flairs.role_name != role.name]
        flairs.to_csv('flairs.csv', index=False)
        create_list("flairs")
        await ctx.message.add_reaction('✅')
        await asyncio.sleep(3)
        return await ctx.message.delete()

    @commands.command(name='listflairs', aliases=['lf'])
    async def listflairs(self, ctx):
        try:
            await ctx.send('\n'.join(list(lists["flairs"].keys())))
            return await ctx.message.delete()
        except:
            return await ctx.reply('Wups! There are no self-assignable roles in this server...', mention_author=False)

    @commands.command(name='im')
    async def im(self, ctx, *roleName:str):
        roleName = ' '.join(roleName) # finds the role from the name given
        role = discord.utils.get(ctx.guild.roles, name=roleName)
        if role is None:
            return await ctx.reply("Wups! Invalid role...", mention_author=False)
        if role.name not in list(lists["flairs"].keys()): # checks if it is a flair
            return await ctx.reply("Wups! That is not a self-assignable role...", mention_author=False)
        
        hasRole = False # checks if the user already has the role
        for userRole in ctx.author.roles:
            if userRole.id == role.id:
                hasRole = True
                break
            
        if hasRole: # gives or removes role
            await ctx.author.remove_roles(role)
        else:
            await ctx.author.add_roles(role)
        await ctx.message.add_reaction('✅')
        await asyncio.sleep(3)
        return await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(Flair(bot))