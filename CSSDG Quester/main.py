import discord
from discord import user
from discord.ext import commands
from db import session, User, Quest, QuestActive, Ideea
from discord import Embed
import asyncio
import time
# Start scheduler to check if the active quests are over and start new quests every 1day
#note that there are many other schedulers available
#from apscheduler.schedulers.background import BackgroundScheduler

#sched = BackgroundScheduler()

bot = commands.Bot(command_prefix='!', description='Un bot special conceput pentru Sectantii CCSDG.')



@bot.event
async def on_ready():
    #initQuests()
    print('Logat ca')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    updateUsers()


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
        count = 0
        for role in member.roles:
            # TODO: GET THE ADMIN ROLE NAME FROM THE DATABASE INSTEAD, fro better scalability
            if role.name == 'QuesterADMIN' and user.is_admin == False:
                print("Updated user %s to admin role" %(user.discord_name))
                user.is_admin = True
                s.commit()
            if role.name == 'QuesterADMIN' and user.is_admin == True:
                print(f'{user.discord_name} is already admin')
                count += 1
        #if count == 0 and user.is_admin == True:
            #print('{user.discord_name} is not admin anymore'):
            # TODO: How to make this work with multiple servers ?
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
async def embed(ctx):
    embed = discord.Embed(title="title ~~(did you know you can have markdown here too?)~~", colour=discord.Colour(0x7c941e), url="https://discordapp.com", description="this supports [named links](https://discordapp.com) on top of the previously shown subset of markdown. ```\nyes, even code blocks```")

    embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
    embed.set_thumbnail(url="https://cdn.discordapp.com/embed/avatars/0.png")
    embed.set_author(name="author name", url="https://discordapp.com", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
    embed.set_footer(text="footer text", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")

    embed.add_field(name="🤔", value="some of these properties have certain limits...")
    embed.add_field(name="😱", value="try exceeding some of them!")
    embed.add_field(name="🙄", value="an informative error should show up, and this view will remain as-is until all issues are fixed")
    embed.add_field(name="<:thonkang:219069250692841473>", value="these last two", inline=True)
    embed.add_field(name="<:thonkang:219069250692841473>", value="are inline fields", inline=True)

    await ctx.send(content="this `supports` __a__ **subset** *of* ~~markdown~~ 😃 ```js\nfunction foo(bar) {\n  console.log(bar);\n}\n\nfoo(1);```", embed=embed)



def getQuestStringByID(quest_id, active = True):
    s = session()
    quest = Quest.getByID(s, quest_id)
    

    stringQuest = ("```css" # This starts the discord formating with 'css' styling
        + "\n Quest #%s [%s] [%s]" % (quest.id, quest.type, quest.rarity)
        # TODO: ADD datetime year
    )
    if active == True:
        active = QuestActive.getById(s,quest_id)
        stringQuest+= "\n{Terminat:    %s/%s/2018}" % (active.time_stop.day, active.time_stop.month)

    # CHECK for plurals: 1 day or 2 days; 
    if(quest.interval_days > 1):
        stringQuest = stringQuest + "\n{Timp:        %s zile}" % (quest.interval_days)
    else:
        stringQuest = stringQuest + "\n{Timp:        %s zi}" % (quest.interval_days)

    stringQuest = stringQuest + (
        "\n{Nume: %s}" % (quest.name)
        + "\n{Obiectiv: %s}" % (quest.task)
        + "\n----RECOMPENSE-----"
    )

    # Don't print the row if it doesn't have any rewards/ranks
    if quest.xp > 0:
        stringQuest = stringQuest + "\nXP: %s" % (quest.xp)
    if quest.sect_coins > 0:
        stringQuest = stringQuest + "\nSect coins: %s" % (quest.sect_coins)
        
    # This is how you check if the ORM object is empty :|
    if quest.ranks != []:
        stringQuest = stringQuest + "\nRankuri: "
        for rank in quest.ranks:
            stringQuest = stringQuest + rank.name + ', '
        stringQuest  = stringQuest[:len(stringQuest) - 2]
    
    # This line closes the discord formating, it's very important
    stringQuest = stringQuest + "\n```"
    s.close()
    return stringQuest

@bot.command()
async def incepe_rand(ctx):
    s = session()
    questStartedId = Quest.startRandom(s)
    print(questStartedId)
    await ctx.send("Questul urmator a fost inceput, mult noroc coita :sunglasses:")

    questString = getQuestStringByID(questStartedId)
    await ctx.send(questString)
    s.close()

# Vry big bug with threads here
@bot.command()
async def quest(ctx):
    s = session()
    activeIds = QuestActive.get(s)
    s.close()
    string = getQuestStringByID(activeIds[0])
    embed = discord.Embed(colour=discord.Colour(0xf925f9))
    embed.add_field(name='Quest %s/%s' % (1, len(activeIds)), value=string)
    msg = await ctx.send(embed=embed)

    # Add the reactions
    await msg.add_reaction('◀')
    await msg.add_reaction('✅')
    await msg.add_reaction('▶')

    # Do the magic
    # Wait for reactions
    index = 0
    def check(reaction, user):
        return user == ctx.author and (str(reaction.emoji) == '◀' or str(reaction.emoji) == '▶' or str(reaction.emoji) == '✅')
    
    
    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=5.0, check=check)
        except:
            print('wewe')
        else:
            if reaction.emoji == '▶' and index < len(activeIds) - 1:
                index+=1 
                string = getQuestStringByID(activeIds[index])
                embed = discord.Embed(colour= discord.Colour(0xf925f9))
                embed.add_field(name='Quest %s/%s' % (index + 1, len(activeIds)), value=string)
                await msg.edit(embed=embed)
            elif reaction.emoji == '◀' and index > 0:
                index-=1 
                string = getQuestStringByID(activeIds[index])
                embed = discord.Embed(colour= discord.Colour(0xf925f9))
                embed.add_field(name='Quest %s/%s' % (index + 1, len(activeIds)), value=string)
                await msg.edit(embed=embed)
            elif reaction.emoji == '✅':
                s = session()
                quest = Quest.getByID(s, activeIds[index])
                await ctx.send(f'{user.mention}, cererea ta pentru completarea _questului_  **{quest.id}** a fost trimisa cu succes maretului lider intr-un mesaj privat')
                owner = bot.get_user(256853098914381835)
                await owner.send(f'***{user.name}*** a cerut aprobare pentru questul **{quest.id}**')
                s.close()
        # Remove
        try:
            reaction, user = await bot.wait_for('reaction_remove', timeout=5.0, check=check)
        except:
            print('muie?')
        else:
            if reaction.emoji == '▶' and index < len(activeIds) - 1:
                index+=1 
                string = getQuestStringByID(activeIds[index])
                embed = discord.Embed(colour=discord.Colour(0xf925f9))
                embed.add_field(name='Quest %s/%s' % (index + 1, len(activeIds)), value=string)
                await msg.edit(embed=embed)
            elif reaction.emoji == '◀' and index > 0:
                index-=1 
                string = getQuestStringByID(activeIds[index])
                embed = discord.Embed(colour=discord.Colour(0xf925f9))
                embed.add_field(name='Quest %s/%s' % (index + 1, len(activeIds)), value=string)
                await msg.edit(embed=embed)
            elif reaction.emoji == '✅':
                s = session()
                quest = Quest.getByID(s, activeIds[index])
                await ctx.send(f'{user.mention}, cererea ta a fost anulata 👌')
                owner = bot.get_user(256853098914381835)
                await owner.send(f'***{user.name}*** si-a dat seama ca nu este vrednic pentru completarea questului **{quest.id}**')    
                s.close()

        
@bot.command()
async def idee(ctx, text: str):
    s = session()
    user = User.getByDiscordID(s, ctx.author.id)
    ideea = Ideea(name = ctx.message.clean_content[6:], user = user)
    s.add(ideea)
    s.commit()
    print(text)
    await ctx.send("Ideea ta: \'%s\' \na fost inregistrata cu succes :D" % (ideea.name))
    #TODO: hmmmmm, maybe change to admins
    owner = bot.get_user(256853098914381835)
    await owner.send(f"**{ctx.author.name}** a avut urmatoarea idee: \n*{ideea.name}*")
    


async def updateActiveQuests():
    await bot.wait_until_ready()
    # Send the message to defined channels
    
    while not bot.is_closed():
        channels = bot.get_all_channels()
        print('Cheking for quest updates')
        ses = session()
        deletedQuests = QuestActive.updateActive(ses)
        ses.close()
        if len(deletedQuests) == 0:
            print('No finished quests')
            await asyncio.sleep(15*60) # task should run every 15minuteshours
            continue
        
        for channel in channels:
            if channel.name == 'quest':
                for deletedQuest in deletedQuests:
                    print('Quests stop message has ben sent to servers')
                    questString = getQuestStringByID(deletedQuest, active=False)
                    await channel.send('Urmatorul quest a fost oprit:')
                    await channel.send(questString)
                    #TODO: Feliciteaza userii care au reusit sa completeze questul in perioada lui :)
        await asyncio.sleep(15*60) # task should run every 15minuteshours



async def startRandomQuest():
    await bot.wait_until_ready()
    isFirstLoop = True
    while not bot.is_closed():
        if isFirstLoop == True:
            await asyncio.sleep(4*60*60) # task should run every 4 HOURS NOW
            isFirstLoop == False
            continue
        channels = bot.get_all_channels()
        print('Starting a random quest')
        ses = session()
        startedId = Quest.startRandom(ses)
        ses.close()
        questString = getQuestStringByID(startedId)
        for channel in channels:
            if channel.name == 'quest':
                await channel.send('Urmatorul quest a fost inceput, succes sectantii mei 😎:')
                await channel.send(questString)

        await asyncio.sleep(2*24*60*60) # task should run every 2 days

@bot.command()
async def reactie(ctx):

    # Pastreaza doar rolurile care nu exista deja
    rolesEmoji = {'Evreu' : '✡',
        'Negru' : '💩',
        'Betiv' : '🥃',
        'Poponar' : '🍆'
    }
    rolesToAdd = rolesEmoji.copy()
    for roles in ctx.guild.roles:
        for key in list(rolesToAdd.keys()):
            if roles.name == key:
                rolesToAdd.pop(key)

    print(rolesToAdd)

    # adaug rolurile care nu exista inca
    for key in rolesToAdd:
        await ctx.send('Am detectat roluri care nu exista initiali...')
        await ctx.guild.create_role(name=key)


    # Aici bagi emgedul..
    mesaj = await ctx.send('Dorel')
    print(rolesEmoji)
    # Adauga toate emojiurile ca reactii la mesaj
    for key, value in rolesEmoji.items():
        await mesaj.add_reaction(value)


    def check(reaction, user):
        if user == ctx.author:
            for key, value in rolesEmoji.items():
                if str(reaction.emoji) == value:
                    return True
    try:
        reaction,member = await bot.wait_for('reaction_add', timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("❌Nu s-a reactionat la mesaj. Inchid rolurile...❌")
        time.sleep(4)
        await ctx.send('⛔Roluri inchise⛔')
    else:
        for key, value in rolesEmoji.items():
            if reaction.emoji == value:
                await ctx.send(f'Ai primit rolul {key} : {value}')
                for role in ctx.guild.roles:
                    if role.name == key:
                        await member.add_roles(role)


@bot.command()
async def react(ctx):
    isOld = False
    msg = await ctx.send('Test')
    await msg.add_reaction('◀')
    await msg.add_reaction('▶')
    def check(reaction, user):
        return user == ctx.author and (str(reaction.emoji) == '◀' or str(reaction.emoji) == '▶')
    
    @bot.event
    async def on_message(message):
        if message.content == '!react':
            isOld = True
            await msg.delete()
    if isOld == True:
        return

    @bot.event
    async def on_reaction_add(reaction, member):
        if reaction.emoji == '▶':
            print('yes1')
        elif reaction.emoji == '◀':
            print('yes2')
    """ 
    while True: # How do I make this stop when this function is called again ?
        try:
            reaction, member = await bot.wait_for('reaction_add', check=check)
        except:
            pass
        else:
            if reaction.emoji == '▶':
                # Do stuff
                print('yes1')
            elif reaction.emoji == '◀':
                # Do other stuff
                print('yes2')
    """
    """
        def isOld(message):
            return message == '!react'
        try:
            newMsg = await bot.wait_for('on_message',timeout=10, check= isOld)
        except:
            pass
        else:
            await msg.edit(content='hey')
    """

import secret
bot.loop.create_task(updateActiveQuests())
bot.loop.create_task(startRandomQuest())
bot.run(secret.TOKEN)   