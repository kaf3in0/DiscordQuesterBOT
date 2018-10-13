import discord
from discord import user
from discord.ext import commands
from db import session, User, Quest, QuestActive, Ideea

# Start scheduler to check if the active quests are over and start new quests every 1day
#note that there are many other schedulers available
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler()

bot = commands.Bot(command_prefix='!', description='Un bot special conceput pentru Sectantii CCSDG.')


@bot.event
async def on_ready():
    #initQuests()
    print('Logat ca')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    updateUsers()   
    QuestActive.updateActive()
    initSchedulers()

def initSchedulers():
    # seconds can be replaced with minutes, hours, or days
    # Check for user updates every 1 hour
    sched.add_job(updateUsers, 'interval', minutes=15)
    sched.add_job(QuestActive.updateActive, 'interval', minutes=15)
    #sched.add_job(startRandomQuest, 'interval', seconds=15)
    # TODO: Check for active quests updates every 1 hour
    sched.start()
    

# TODO: Finish this
def startRandomQuest():
    s = session()
    quest = Quest.startRandom(s)
    string_quest = ("\nQuest ID: %s" % (quest.id) +
            "\nZiua terminarii: %s/%s" % (quest.active.time_stop.month, quest.active.time_stop.day) +
            "\nDurata timp: %s zile" % (quest.interval_days) +
            "\nTIP: %s" % (quest.type) +
            "\nRaritate: %s"% (quest.rarity) +
            "\nNume: %s" % (quest.name) +
            "\nObiectiv: %s" % (quest.task) +
            "\n----RECOMPENSE-----"
            "\nXP: %s" % (quest.xp) + 
            "\nSect coins: %s" % (quest.sect_coins)
        )
    string_ranks = '\nRankuri: '
    for rank in quest.ranks:
        string_ranks = string_ranks + rank.rank + ', '
    # Just print the string
    # Don't print the last ','
    string = string_quest + string_ranks[:string_ranks.__len__() -2]
    s.close()



# NOTE: This functions shoul stay in here even if it;s not a bot comand because it's heavyli dependent on discord.py   
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
        
        user = User.getByDiscordID(s, member.id)
        #user = s.query(User).filter(User.discord_id == member.id).first()
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
    s.close()


#<Role id=495959309608419343 name='QuesterADMIN'>


@bot.command()
async def premiaza(ctx, quest_id: int, force= ''):
    s = session()
    # Get the author of the message and check if he is an admin in the database
    msgUser = User.getByDiscordID(s, ctx.author.id)
    if msgUser.is_admin == False:
        await ctx.send("Misto incercare bosule, dar nu esti tu bossul %s" %(ctx.author.name))
        return

    # Is it forced reward?    
    if force != '-f':
            force = False
    elif force == '-f':
            force = True

    # Reward all the mentioned users with the quest
    mentions = ctx.message.mentions
    for mention in mentions:
        user = User.getByDiscordID(s, mention.id)
        # Execute the give reward function and also check if it met all the conditions
        check = user.giveReward(s, quest_id, force)
        if check == False:
            await ctx.send("NU poti oferii premiul de la questul %s deoarece acesta nu este activ" % (quest_id))
            return


        # Let users know that they were rewarded
        quest = Quest.getByID(s, quest_id)
        
        string = ('Pentru completarea cu succes a questului \'%s\' <@%s> a fost premiat cu:' % (quest.name, user.discord_id)
         +'\nxp: %s' % (quest.xp)
         +'\nsect coins: %s'% (quest.sect_coins)
        )
        stringStartRanks = '' 
        stringEndRanks = ''            
        
        if quest.ranks.__len__() < 1:
            stringStartRanks = '\nrankul: '
        else:
            stringStartRanks = '\nrankurile: '

        for rank in quest.ranks:
            stringEndRanks = stringEndRanks + rank.name + ', ' 
        string = string + stringStartRanks + stringEndRanks[:stringEndRanks.__len__() - 2]
        print(string)
        await ctx.send(string)

@bot.command()
async def info(ctx):
    s = session()
    #await ctx.send('CURios mic ce esti, ia cu paine:')
    mentions = ctx.message.mentions
    for mention in mentions:
        user = User.getByDiscordID(s,mention.id)
        string = ('\nxp: %s' % (user.xp)
                + '\nsect coins: %s' % (user.sect_coins)
        )
        stringRanks = ''
        stringStartRanks = '\nrankuri: '
        for rank in user.ranks:
            stringRanks = stringRanks + rank.quest_rank.name + ', ' 
        string = string + stringStartRanks + stringRanks[:stringRanks.__len__() - 2]
        await ctx.send(string)



@bot.command()
async def curve(ctx):
    # TODO: Scrape publi24 for bitches
    # TODO: Use the scraped info to give user perview of the hoe - Image, Description, Age, Location
    # TODO: Make it so the user can filter by certain criteria (hair:blonde, age:18-25, marime-sani:D?location-radius:5km?)
    await ctx.send("Ah, vrei sa futi si tu ceva no?:ok_hand::point_left:")
    await ctx.send("Ia d-aici sectantul meu, prietenii la nevoie se cunosc :heart:")
    await ctx.send("https://www.publi24.ro/anunturi/matrimoniale/")
    


@bot.command()
async def quest(ctx):
    s = session()
    activeQuests = QuestActive.get(s)
    if activeQuests.first() == None:
        await ctx.send('Momentan nu exista questuri active')
        return
    for aq in activeQuests:
        questString = getQuestString(ctx,
            aq.quest.ranks,
            aq.quest_id,
            aq.time_stop.month,
            aq.time_stop.day,
            aq.quest.interval_days,
            aq.quest.type,
            aq.quest.rarity,
            aq.quest.name,
            aq.quest.task,
            aq.quest.xp,
            aq.quest.sect_coins
            )
        await ctx.send(questString)
    s.close()


@bot.command()
async def incepe_rand(ctx):
    s = session()
    active = Quest.startRandom(s)
    # Print
    stringQuest = getQuestString(ctx,
        active.quest.ranks,
        active.quest.id,
        active.time_stop.month,
        active.time_stop.day,
        active.quest.interval_days,
        active.quest.type,
        active.quest.rarity,
        active.quest.name,
        active.quest.task,
        active.quest.xp,
        active.quest.sect_coins    
    )
    await ctx.send("Questul umrator a fost inceput, mult noroc coita :sunglasses:")
    await ctx.send(stringQuest)

def getQuestString(ctx, ranks, questId, stopMonth, stopDay, interval, type, rarity, name, task, xp, coins):
    stringQuest = ("```css" # This starts the discord formating with 'css' styling
        + "\n Quest #%s [%s] [%s]" % (questId, type, rarity)
        # TODO: ADD datetime year
        + "\n{Terminat:    %s/%s/2018}" % (stopDay, stopMonth)
    )

    # CHECK for plurals: 1 day or 2 days; 
    if(interval > 1):
        stringQuest = stringQuest + "\n{Timp:        %s zile}" % (interval)
    else:
        stringQuest = stringQuest + "\n{Timp:        %s zi}" % (interval)

    stringQuest = stringQuest + (
        "\n{Nume: %s}" % (name)
        + "\n{Obiectiv: %s}" % (task)
        + "\n----RECOMPENSE-----"
    )

    # Don't print the row if it doesn't have any rewards/ranks
    if xp > 0:
        stringQuest = stringQuest + "\nXP: %s" % (xp)
    if coins > 0:
        stringQuest = stringQuest + "\nSect coins: %s" % (coins)
        
    # This is how you check if the ORM object is empty :|
    if ranks != []:
        stringQuest = stringQuest + "\nRankuri: "
        for rank in ranks:
            stringQuest = stringQuest + rank.name + ', '

    # This line closes the discord formating, it's very important
    stringQuest  = stringQuest[:len(stringQuest) - 2] + "\n```"
    return stringQuest





@bot.command()
async def idee(ctx, text: str):
    print(ctx.message.clean_content[6:])
    s = session()
    user = User.getByDiscordID(s, ctx.author.id)
    ideea = Ideea(name = ctx.message.clean_content[6:], user = user)
    s.add(ideea)
    s.commit()
    print(text)
    await ctx.send("Ideea ta: \'%s\' \na fost inregistrata cu succes :D" % (ideea.name))
    #TODO: hmmmmm, maybe change to admins
    owner = bot.get_user(256853098914381835)
    #'Utilizatorul: %s a adaugat o idee: \n\'%s\'' % (user.discord_server_name, idee.name)
    #await client.send_message(owner, 'o sugi')
    #await ctx.send_message(owner, 'o wtf')  
    #await bot.send_message(owner, 'Hello')
    #client.send_message()

    
import secret
bot.run(secret.TOKEN)
