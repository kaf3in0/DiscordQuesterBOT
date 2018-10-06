import time
from threading import Timer
from db import session
from db import Quest, QuestActive
import pprint as pp
import datetime


# COMAND
def getActiveQuests():
    """
    quest1 = Quest(name = 'Diablo',
     task ='Joaca pana mori',
     type = 'GAMER',
     rarity = 'LEGENDAR',
     interval=datetime.timedelta(weeks=1)
    )
    """
    #active1 = QuestActive(quest_id = 1, time_stop = datetime.datetime.now())
    s = session()
    #s.add(quest1)
    #s.add(active1)
    s.commit()
    activeQuests = QuestActive.get(s)
    for aq in activeQuests:
        string_quest = ("\nquest_id: %s" %(aq.quest_id) +
            "\ntime_stop: %s/%s" % (aq.time_stop.month, aq.time_stop.day) +
            "\ninterval: %s days" % (aq.quest.interval.days) +
            "\ntype: %s" % (aq.quest.type) +
            "\nrarity: %s"% (aq.quest.rarity) +
            "\nname: %s" % (aq.quest.name) +
            "\ntask: %s" % (aq.quest.task) +
            "\nxp: %s" % (aq.quest.xp) + 
            "\nsect_coins: %s" % (aq.quest.sect_coins)
        )
    
        string_ranks = '\nranks: '
        for rank in aq.quest.ranks:
            string_ranks = string_ranks + rank.rank + ', '
        # Just print the string
        # Don't print the last ','
        string  = string_quest + string_ranks
        print(string)
    
    s.close()


#note that there are many other schedulers available
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler()

# seconds can be replaced with minutes, hours, or days
sched.add_job(getActiveQuests, 'interval', seconds=3)
sched.start()

time.sleep(1000000)