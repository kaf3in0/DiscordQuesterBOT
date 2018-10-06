import discord
from discord import user
from discord.ext import commands
from db import session, User, Quest

# Start scheduler to check if the active quests are over and start new quests every 1day
#note that there are many other schedulers available
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler()





client = discord.Client()
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




@bot.event
async def on_ready():
    #initQuests()
    print('Logat ca')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    updateUsers()
    initSchedulers()
    
   

def initSchedulers():
    # seconds can be replaced with minutes, hours, or days
    # Check for user updates every 1 hour
    sched.add_job(updateUsers, 'interval', seconds=15)
    # TODO: Check for active quests updates every 1 hour

    sched.start()
def updateUsers():
    """
    Update the discord server for new users, new nicknames, new names and new admins
    """
    print("Checking Discord Users for updates")
    s = session()
    members = bot.get_all_members()

    for member in members:
        # Ignore bots
        if member.bot == True:
            continue
        
        user = s.query(User).filter(User.discord_id == member.id).first()
        # If the user doesn't exist we add it to the database
        if user == None:
            print("Added discord user %s to the database" % (member.name))
            user = User(discord_id = member.id, discord_name = member.name, discord_server_name = member.nick)
            s.add(user)
            s.commit()
        # Chekc if the user changed his name, update it if so
        if user.discord_name != member.name:
            print("Updated user's name %s to %s" %(user.discord_name, member.name))
            user.discord_id = member.name
            s.commit()
        # Check if the nickname on the server changed, update it if so
        if user.discord_server_name != member.nick:
            print("Updated user's nick %s to %s" % (user.discord_server_name, member.nick))
            user.discord_server_name = member.nick
            s.commit()
        # Check if the user has the admin role, update it if so
        for role in member.roles:
            # TODO: GET THE ADMIN ROLE NAME FROM THE DATABASE INSTEAD, fro better scalability
            if role.name == 'QuesterADMIN' and user.is_admin != True:
                print("Updated user %s to admin role" %(user.discord_name))
                user.is_admin = True
                s.commit()



#<Role id=495959309608419343 name='QuesterADMIN'>
def isUserAdmin(ctx):
    for role in ctx.author.roles:
        if role.name == 'QuesterADMIN':
            return True
    return False


def giveReward(quest_id, user_id, force):
    s = session()
    quest = s.query(Quest).filter(Quest.id == quest_id).first()
    if force == False:
        # This means if the quest is not active,
        # because the ORM returns an empty list
        if quest.quest_acitve == []:
            return "COULD NOT GIVE REWARD FOR QUEST ID: %s, QUEST IS NOT ACTIVE" % (quest_id)

@bot.command()
async def premiaza(ctx, quest_id: int, user: str, force= ''):
    #print (ctx.author.id)
    s = session()
    if isUserAdmin(ctx) == False:
        await ctx.send("Misto incercare bosule, dar nu esti tu bossul %s" %(ctx.author.name))
        return

    # Is it forced reward?    
    if force != '-f':
            force = False
    elif force == '-f':
            force = True


    mentions = ctx.message.mentions
    for mention in mentions:
        user = s.query(User).filter(User.discord_id == mention.id).first()
        # TODO: Make givereward function
        await ctx.send(giveReward(quest_id, user.id, force))


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


bot.run('NDg2ODAyNzQ5NTE0NzExMDUx.DnEbZA.ny7LqqXnkjR6qq1E1j3qsuxi_7k')