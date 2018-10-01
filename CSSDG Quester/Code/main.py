import discord
from discord.ext import commands
from discord import user
import quests as q
from threading import Timer
from sqlalchemy import select, insert, delete, func, update
# 3rd party
from database import connection, quests, active_quests, users, quest_ranks, user_ranks, completed_quests
bot = commands.Bot(command_prefix='!', description='Un bot special conceput pentru Sectantii CCSDG.')
# How to add subcomands
"""
@bot.group(pass_context=True)
async def git(ctx):
    if ctx.invoked_subcommand is None:
        await bot.say('Invalid git command passed...')

@git.command()
async def push(remote: str, branch: str):
    await bot.say('Pushing to {} {}'.format(remote, branch))
"""
client = discord.Client()



@bot.event
async def on_ready():
    #initQuests()
    print('Logat ca')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    setServerUsers()

    # Start timers to check if the active quests are over and start new quests every 1day



def setServerUsers():
    #self.get_all_members()
    #me = discord.utils.get(self.bot.get_all_members()
    members = bot.get_all_members()
    

    for member in members:
        #print (member.name, member.id)
        data = connection.execute(select([users]).where(users.c.discord_id == member.id))
        row = data.fetchone()
        # If the user doesn't exist we add it to the database
        if row == None:
            query = users.insert().values(discord_id = member.id, name = member.name)
            connection.execute(query)
        # Chekc if the user changed his name, update it if so
        elif row[users.c.name] != member.name:
            connection.execute(users.update().values(name = member.name).where(users.c.discord_id == member.id))


#<Role id=495959309608419343 name='QuesterADMIN'>
def isUserAdmin(ctx):
    role_id = 495959309608419343
    for row in ctx.author.roles:
        if row.id == role_id:
            return True
    return False



@bot.command()
async def premiaza(ctx, quest_id: int, user: str, force= ''):
    #print (ctx.author.id)

    if isUserAdmin(ctx) == False:
        await ctx.send("Misto incercare bosule, dar nu esti tu bossul %s" %(ctx.author.name))
        return

    # Is it forced reward?    
    if force != '-f':
            force = False
    elif force == '-f':
            force = True


    mentions = ctx.message.mentions
    for row in mentions:
        data = connection.execute(select([users]).where(users.c.discord_id == row.id))
        data = data.fetchone()
        await ctx.send(q.giveReward(quest_id, data[users.c.id], force))


@bot.command()
async def m_info(ctx):
    await ctx.send('CURios mic ce esti, ia cu paine:')
    mentions = ctx.message.mentions
    for row in mentions:
        #print(row.id)

        data_users = connection.execute(select([users]).where(users.c.discord_id == row.id))
        data_users = data_users.fetchone()
        print(data_users[users.c.id])
        await ctx.send("<@%s>\nXP: %s\nSect Coins:%s\n" % (row.id,data_users[users.c.xp], data_users[users.c.sect_coins]))
        
        #######
        query = select([user_ranks, quest_ranks]).\
            select_from(user_ranks.join(quest_ranks, user_ranks.c.rank_id == quest_ranks.c.id)).\
            where(user_ranks.c.user_id == data_users[users.c.id])
        data = connection.execute(query)
        await ctx.send("-----RANKS-----")
        for row in data:
            await ctx.send(row[quest_ranks.c.rank])



@bot.command()
async def salut(ctx):
    await ctx.send(":smiley: :wave: Hai salut, coaie!")
    await ctx.send(":smiley:Tot virgin, tot virgin?:smiley:")

@bot.command()
async def curve(ctx):
    # TODO: Scrape publi24 for bitches
    # TODO: Use the scraped info to give user perview of the hoe - Image, Description, Age, Location
    # TODO: Make it so the user can filter by certain criteria (hair:blonde, age:18-25, marime-sani:D?location-radius:5km?)
    await ctx.send("Ah, vrei sa futi si tu ceva no?:ok_hand::point_left:")
    await ctx.send("Ia d-aici sectantul meu, prietenii la nevoie se cunosc :heart:")
    await ctx.send("https://www.publi24.ro/anunturi/matrimoniale/")
    

@bot.command()
async def sect_rank(ctx):
    
    pass
@bot.command()
async def sect_stats(ctx):
    pass

@bot.command()
async def m_rate(ctx):
    await ctx.send("Rate: \n\nComun: %s\nEpic: %s\nLegendar: %s\nImposibil %s" % (
        q.Rarities.COMUN, q.Rarities.EPIC, q.Rarities.LEGENDAR, q.Rarities.IMPOSIBIL)
    )
@bot.command()
async def incepe(ctx):
    if isUserAdmin(ctx) == False:
        await ctx.send("Misto incercare bosule, dar nu esti tu bossul %s" %(ctx.author.name))
        return
    await ctx.send(q.startRandomQuest())



@bot.command()
async def misiune(ctx):
    data = q.getActiveQuests()
    check = data.fetchone()
    if check == None:
        await ctx.send("Nu exista questuri active momentan")
        return
    for row in data:
        await ctx.send('QUEST\nID: %s\nName: %s\nTask: %s\nType: %s\nRarity: %s\nXp: %s\nSect coins: %s' % (
            row[quests.c.id], row[quests.c.name], row[quests.c.task], row[quests.c.type], 
            row[quests.c.rarity], row[quests.c.xp], row[quests.c.sect_coins]))


bot.run('<token>)