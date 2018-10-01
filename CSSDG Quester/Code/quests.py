import random
from sqlalchemy import select, insert, delete, func, update
import datetime


# 3rd party
from database import connection, quests, active_quests, users, quest_ranks, user_ranks, completed_quests

BETIV = 'BETIV'
NROMAL = 'NORMAL'
PARIOR = 'PARIOR'
DUBIOS = 'DUBIOS'

class Rarities:
    IMPOSIBIL = 15
    LEGENDAR = 35
    EPIC = 50
    COMUN = 100


# Returns a random rarity based on the drop rates (%)
def getRandomRarity():
    r = random.randint(1,100)

    if r <= Rarities.IMPOSIBIL:
        return "IMPOSIBIL"
    elif r <= Rarities.LEGENDAR:
        return "LEGENDAR"
    elif r <= Rarities.EPIC:
        return "EPIC"
    else:
        return "COMUN"

def getActiveQuests():
    return connection.execute(select([ quests,  active_quests]).select_from( quests.join( active_quests, quests.c.id ==  active_quests.c.quest_id)))

def stopFinishedQuests():
    # create a Session
    session = Session()

    session.query(active_quests).delete().where(datetime.datetime.now() >= active_quests.c.date_stop)
    #query = active_quests.delete().where(datetime.datetime.now() >= active_quests.c.date_stop)
    #connection.execute(query)
            

def startRandomQuest():
    rarity = getRandomRarity()
    query = select([quests]).order_by(func.random()).limit(1).where((quests.c.rarity == rarity) & (quests.c.status == True))
    data = connection.execute(query)
    # WTF ALSO TODO FIX THIS
    """
    for row in data:
        if row == None:
            return "NO ENABLED QUESTS FOUND"
    """
    quest_id = None
    date_stop = None
    date_start = datetime.datetime.now()
    for row in data:
        q_time = row[quests.c.time_days]
        date_stop = date_start + datetime.timedelta(days=q_time)
        quest_id = row[quests.c.id]
        
    
    query = active_quests.insert().values(quest_id = quest_id, date_start = date_start, date_stop = date_stop)
    connection.execute(query)

 
    return "\nSTARTED QUEST ID: %s" % (quest_id)

def isQuestActiveByID(id):
    query = select([active_quests]).where(active_quests.c.quest_id == id)
    data = connection.execute(query)
    i = 0
    for row in data:
        i += 1
       
    if i == 0:
        return False
    else:
        return True
# Gives the reward for the quest by quest_id to user by user_id
def giveReward(quest_id, user_id, force = False):
    
    # If the quest isnt active then you cant give a reward for it, unless you overrule it
    if force == False:
        if isQuestActiveByID(quest_id) == False:
            return "COULD NOT GIVE REWARD FOR QUEST ID: %s, QUEST IS NOT ACTIVE" % (quest_id)
    # Gets the quest rewarded ranks, if any
    query = select([quests, quest_ranks]).\
        select_from(quests.outerjoin(quest_ranks, quests.c.id == quest_ranks.c.quest_id)).\
        where(quests.c.id == quest_id)
    data = connection.execute(query)

    query3 = None
    quest_name = None
    
    for row in data:
        quest_name = row[quests.c.name]
        # Update xp and coins 
        query = users.update().\
            values(xp = users.c.xp + row[quests.c.xp], sect_coins = users.c.sect_coins + row[quests.c.sect_coins]).\
            where(users.c.id == user_id)
        # Insert the new ranks into the users info
        if row[quest_ranks.c.id] != None:
            query2 = user_ranks.insert().\
                values(user_id = user_id, rank_id = row[quest_ranks.c.id])
            connection.execute(query2)

        # Insert the completed quests by the user
        query3 = completed_quests.insert().\
            values(quest_id = row[quests.c.id], user_id = user_id, date = datetime.datetime.now())

        
    # !!!!!!!!!!THIS ONLY HAPENS ONCE!!!!!!!!!!!!!!
    connection.execute(query)
    connection.execute(query3)

    data = connection.execute(select([users]).where(users.c.id == user_id))
    user_name = None
    for row in data:
        user_name = row[users.c.name]
    return "Quest ID: %s, name: %s \nRewarded succesfully to %s\n" % (quest_id, quest_name, user_name)

