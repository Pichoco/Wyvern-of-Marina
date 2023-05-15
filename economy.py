import discord
from discord.ext import commands
import random
import datetime
import pandas as pd
import asyncio
from utils import *

# economy commands
# slots, balance, leaderboard, paypal, bet
class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.items = ['delivery', 'bomb', 'blueshell','ticket']
        self.prices = [100000, 10000, 5000, 2500]

    @commands.command(name='slots')
    async def slots(self, ctx):
        if await in_wom_shenanigans(ctx):
            if assert_cooldown('slots') != 0:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('slots')} seconds...", mention_author=False)
            if not subtract_coins(ctx.author.id, 10):
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! You don't have enough {zenny} to play...", mention_author=False)
        
            emojis = ["🍒", "🍇", "🍊", "🍋", "🍉","7️⃣"]
            reels = ["❓","❓","❓"]
            msg = await ctx.reply(f"{reels[0]} | {reels[1]} | {reels[2]}", mention_author=False)
            for i in range(0,3):
                await asyncio.sleep(1)
                reels[i] = random.choice(emojis)
                await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}", allowed_mentions=discord.AllowedMentions.none())
            if all(reel == "7️⃣" for reel in reels):
                add_coins(ctx.author.id,500)
                return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\n**Jackpot**! 500 {zenny}!", allowed_mentions=discord.AllowedMentions.none())
            elif len(set(reels)) == 1 and reels[0] != "7️⃣":
                add_coins(ctx.author.id,100)
                return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\nSmall prize! 100 {zenny}!", allowed_mentions=discord.AllowedMentions.none())
            elif len(set(reels)) == 2:
                if reels.count("7️⃣") == 2:
                    add_coins(ctx.author.id,50)
                    return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\nTwo lucky 7's! 50 {zenny}!", allowed_mentions=discord.AllowedMentions.none())
                add_coins(ctx.author.id,25)
                return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\nNice! 25 {zenny}!", allowed_mentions=discord.AllowedMentions.none())
            return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\nBetter luck next time...", allowed_mentions=discord.AllowedMentions.none())

    @commands.command(name='balance', aliases=['bal'])
    async def balance(self, ctx, member:discord.Member = None):
        member = member or ctx.author
        if not member == ctx.author:
            if subtract_coins(ctx.author.id, 10):
                add_coins(member.id, 10)
            else:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! Insufficient funds...", mention_author=False)
        for userID in lists['coins'].keys():
            if str(member.id) == userID:
                if not member == ctx.author:
                    return await ctx.reply(f"{member.name} has {lists['coins'][str(member.id)]} {zenny}!", mention_author=False)
                return await ctx.reply(f"You have {lists['coins'][str(member.id)]} {zenny}!", mention_author=False)
        await ctx.message.add_reaction('🦈')
        return await ctx.reply("Wups! Get some bread, broke ass...", mention_author=False)

    @commands.command(name='leaderboard', aliases=['lb'])
    async def leaderboard(self, ctx):
        async with ctx.typing():
            df = pd.read_csv("coins.csv")
            df_sorted = df.sort_values("coins", ascending=False)
            df_sorted.to_csv("coins.csv", index=False)
            create_list('coins')
        top_users = [(k, lists['coins'][k]) for k in list(lists['coins'])[:5]]
        embed = discord.Embed(title=f'Top {len(top_users)} Richest Users', color=discord.Color.purple())
        if len(top_users) == 1:
            embed.title='Richest User'
        elif len(top_users) == 0:
            return await ctx.reply('Wups! No one is in this economy...', mention_author=False)
        for i, (user_id, z) in enumerate(top_users):
            user = await self.bot.fetch_user(user_id)
            embed.add_field(name=f'#{i+1}: {user.name}', value=f'{z} {zenny}', inline=False)
            if i == 0:
                embed.set_thumbnail(url=user.avatar.url)
        return await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name='steal')
    async def steal(self, ctx, target: discord.Member):
        global prev_steal_targets, target_counts
        if await in_wom_shenanigans(ctx):
            if target.bot or target == ctx.author:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! You can't steal from a bot or from yourself...", mention_author=False)
            if prev_steal_targets.get(ctx.author.id) == target and target_counts.get(ctx.author.id, 0) <= 2:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! You can't target this person again so soon. Choose a different target...", mention_author=False)
            if assert_cooldown('steal') != 0:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('steal')} seconds...", mention_author=False)
        
            if prev_steal_targets.get(ctx.author.id) != target:
                target_counts[ctx.author.id] = target_counts.get(ctx.author.id, 0) + 1
                prev_steal_targets[ctx.author.id] = target
            if target_counts.get(ctx.author.id, 0) >= 2:
                target_counts[ctx.author.id] = 0

            async with ctx.typing():
                df = pd.read_csv("coins.csv")
                df_sorted = df.sort_values("coins", ascending=False)
                df_sorted.to_csv("coins.csv", index=False)
                create_list('coins')
            richest_person_list = [(k, lists['coins'][k]) for k in list(lists['coins'])[:1]]
            richest_person_id = int(richest_person_list[0][0])
            richest_person = discord.utils.get(ctx.guild.members, id=richest_person_id)
            steal_chance = 6 if target == richest_person else 4
            
            if random.randint(1,10) <= steal_chance:
                random_steal = random.randint(1,100)
                if subtract_coins(target.id, random_steal):
                    add_coins(ctx.author.id, random_steal) # successful steal
                    return await ctx.reply(f"You successfully stole {random_steal} {zenny} from {target.name}!", mention_author=False)
                else:
                    return await ctx.reply(f"You tried stealing {random_steal} {zenny} from {target.name}, but they don't have enough {zenny}...", mention_author=False) # successful steal, but couldn't do it
            
            else: 
                lost_coins = random.randint(1, 100)
                if subtract_coins(ctx.author.id, lost_coins): # unsuccessful steal
                    add_coins(target.id, lost_coins)
                    return await ctx.reply(f"You got caught trying to steal {lost_coins} {zenny} from {target.name}! You were forced to pay them back instead...", mention_author=False)
                else:
                    return await ctx.reply(f"You got caught trying to steal {lost_coins} {zenny} from {target.name}! However, you weren't able to pay them back...", mention_author=False) # successful steal, couldn't pay back

    @commands.command(name='paypal')
    async def paypal(self, ctx, recipient:discord.Member, amount:int):
        if await in_wom_shenanigans(ctx):
            if amount <= 0:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! Invalid payment amount...", mention_author=False)
            if recipient.bot or recipient.id == ctx.author.id:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! You can't pay a bot or yourself...", mention_author=False)
            if subtract_coins(ctx.author.id,amount):
                add_coins(recipient.id,amount)
                return await ctx.reply(f"{recipient.name} has received {amount} {zenny} from you!", mention_author=False)
            await ctx.message.add_reaction('🦈')
            return await ctx.reply(f"Wups! You don't have that much {zenny}...", mention_author=False)

    @commands.command(name='bet')
    async def bet(self, ctx, amount:int):
        if await in_wom_shenanigans(ctx):
            if assert_cooldown('bet'):
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('bet')} seconds...", mention_author=False)
            if subtract_coins(ctx.author.id, amount):
                roll = random.randint(1,6)
                roll2 = random.randint(1,6)
                result = roll + roll2
                if result == 7:
                    add_coins(ctx.author.id, 2*amount)
                    return await ctx.reply(f"You rolled a {result}! You win!", mention_author=False)
                return await ctx.reply(f"You rolled a {result}! Sorry, you lost...", mention_author=False)
            await ctx.message.add_reaction('🦈')
            return await ctx.reply(f"Wups! You can't bet that much {zenny} as you don't have that much...",mention_author=False)

    @commands.command(name='marketplace', aliases=['mp'])
    async def marketplace(self, ctx):
        if await in_wom_shenanigans(ctx):
            embed = discord.Embed(title='Marketplace', color=discord.Color.green())
            embed.add_field(name=f'delivery, 100,000 {zenny}', value='Have Blues personally deliver their WoM plushie to you!', inline=False)
            embed.add_field(name=f'bomb, 10,000 {zenny}', value='Mute a random member for 30 minutes!', inline=False)
            embed.add_field(name=f'blueshell, 5,000 {zenny}', value='Siphon half of the Zenny from the richest person! This will have no effect if you are the richest person.', inline=False)
            embed.add_field(name=f'ticket, 2,500 {zenny}', value='Redeem this ticket for a custom role!', inline=False)
            embed.set_footer(text='If you want to purchase any of these items, use !w buy (item name). The item name is exactly as you see it in this marketplace!')
            return await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name='buy')
    async def buy(self, ctx, item:str):
        if await in_wom_shenanigans(ctx):
            for item_name, item_price in zip(self.items, self.prices):
                if item.lower() == item_name:
                    if not subtract_coins(ctx.author.id, item_price):
                        await ctx.message.add_reaction('🦈')
                        return await ctx.reply(f"Wups! You don't have enough {zenny}...", mention_author=False)
                    add_item(item, ctx.author.id, 1)
                    return await ctx.reply(f"You have successfully purchased a {item_name}!", mention_author=False)
            await ctx.message.add_reaction('🦈')
            return await ctx.reply("Wups! Invalid item...", mention_author=False)

    @commands.command(name='inventory', aliases=['inv'])
    async def inventory(self, ctx):
        if await in_wom_shenanigans(ctx):
            inventorySTR = "You have...\n\n"
            async with ctx.typing():
                for item in self.items:
                    inventorySTR += f'{int(lists[item].get(str(ctx.author.id), 0))} {item}s\n'
            return await ctx.reply(inventorySTR, mention_author=False)

    @commands.command(name='use')
    async def use(self, ctx, item:str):
        if await in_wom_shenanigans(ctx):
            item = item.lower()
            if item not in self.items:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! Invalid item...", mention_author=False)

            if item == 'delivery':
                if subtract_item(item, ctx.author.id, 1):
                    blues = 232041680017031168
                    moddery = discord.utils.get(ctx.guild.channels, name='moddery')
                    await moddery.send(f"<@{blues}>, {ctx.author.name} has purchased a delivery. You are now obligated to personally deliver your plushie of me to them! Don't back out of it now...")
                    return await ctx.reply("Blues has been notified, you gambling-addicted bastard...", mention_author=False)
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! You don't have a {item}...", mention_author=False)

            elif item == 'bomb':
                if subtract_item(item, ctx.author.id, 1):
                    bombed = random.choice([member for member in ctx.guild.members if not member == ctx.author and not member.bot and not member.guild_permissions.administrator])
                    await ctx.message.delete()
                    return await bombed.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(minutes=30))
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! You don't have a {item}...", mention_author=False)

            elif item == 'blueshell':
                async with ctx.typing():
                    df = pd.read_csv("coins.csv")
                    df_sorted = df.sort_values("coins", ascending=False)
                    df_sorted.to_csv("coins.csv", index=False)
                    create_list('coins')
                    richest_person_list = [(k, lists['coins'][k]) for k in list(lists['coins'])[:1]]
                    richest_person_id = int(richest_person_list[0][0])
                    richest_person = discord.utils.get(ctx.guild.members, id=richest_person_id)
                    if ctx.author == richest_person:
                        await ctx.message.add_reaction('🦈')
                        return await ctx.reply(f"Wups! You can't {item} yourself! You're the richest person...", mention_author=False)
                    if subtract_item(item, ctx.author.id, 1):
                        balance = int(lists['coins'][str(richest_person_id)])
                        remainder = balance % 2
                        if remainder == 1:
                            add_coins(richest_person_id, 1)
                            balance = int(lists['coins'][str(richest_person_id)])
                        if subtract_coins(richest_person_id, balance // 2):
                            add_coins(ctx.author.id, balance // 2)
                            return await ctx.reply(f"{richest_person.name} got hit by a {item}! You received {balance // 2} {zenny} from them!", mention_author=False)
                    await ctx.message.add_reaction('🦈')
                    return await ctx.reply(f"Wups! You don't have a {item}...", mention_author=False)

            elif item == 'ticket':
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                if subtract_item(item, ctx.author.id, 1):
                    await ctx.reply("You have 60 seconds to name your new custom role! This can be done by simply sending the name of that role in this channel. Be aware, however, that the next message you send will be the role name...", mention_author=False)
                    try:
                        msg = await self.bot.wait_for('message', check=check, timeout=60)
                    except asyncio.TimeoutError:
                        add_item(item, ctx.author.id, 1)
                        return await ctx.reply("Time's up! You didn't provide me with a role name, so I've given you your ticket back. Try again later...", mention_author=False)
                    name = msg.content
                    role = await ctx.guild.create_role(name=name)
                    await ctx.author.add_roles(role)
                    return await msg.reply("Congrats on your new role!", mention_author=False)
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! You don't have a {item}...", mention_author=False)

async def setup(bot):
    await bot.add_cog(Economy(bot))
