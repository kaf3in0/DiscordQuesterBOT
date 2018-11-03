import datetime
import random

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer,
                        Interval, String, create_engine, func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

engine = create_engine('sqlite:///DB/data.db')
 
# Construct a sessionmaker object, use this object to make sessions across the aplication by importing it
session = sessionmaker(bind = engine)

# TODO: Constants shouldn't be in a class
# TODO: Make it so you can change and store those in the DataBase for user customization
class Types:
    BETIV = 'BETIV'
    NORMAL = 'NORMAL'
    DUBIOS = 'DUBIOS'
    PARIOR = 'PARIOR'

class Rarities:
    # % CONSTATNS
    # TODO: Make it so you can change and store those in the DataBase for user customization
    COMUN = 100
    EPIC = 60
    LEGENDAR = 25
    IMPOSIBIL = 5

    # WTF should this be ?
    def getRandomRarity():
        """
        Returns a string with a random rarity based on the drop rate (%) 
        """
        r = random.randint(1,100)
        if r <= Rarities.IMPOSIBIL:
            return "IMPOSIBIL"
        elif r <= Rarities.LEGENDAR:
            return "LEGENDAR"
        elif r <= Rarities.EPIC:
            return "EPIC"
        else:
            return "COMUN"

# TEACH: The parameter in a class means User class inherits everything from Base class which is from sqlalchemy
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    discord_id = Column(Integer, nullable = False)
    discord_name = Column(String, nullable = True)
    discord_server_name = Column(String, nullable = True)
    # Use database to check if a user is admin instead of discord roles for better scalapbility with whatsapp
    # If a user is the admin with discord role then add him in here
    # TODO: Regulary check for role changes
    is_admin = Column(Boolean, default = False)
    lv = Column(Integer, default = 0)
    xp = Column(Integer, default = 0)
    sect_coins = Column(Integer, default = 0)
    
    #BACKREFS
    phone_numbers = relationship('UserPhoneNumber', backref = 'user')
    quests = relationship('UserQuest', backref = 'user')
    ranks = relationship('UserRank', backref = 'user')
    ideea = relationship('Ideea', backref= 'user')

    def getCompletedQuests(self, session):
        """
        Returns a list with id's of all the completed quests by the user or None if there aren't any
        """
        userQuests = session.query(UserQuest).filter(UserQuest.user_id==self.id)
        # Return None if there are no completed quests by the user
        if userQuests.first() == None:
            return None
        
        # Save only the ids of the completed quests
        questids = []
        for userQuest in userQuests:
            questids.append(userQuest.quest_id)
        return questids

    def giveReward(self, session, quest_id, force = False):
        """
        Quest gets rewarded to the user. The quest must 
        be active or force to be true for that to be possible.
        Returns true if the user was rewarded or false if conditions
        were not met.
        """
        quest = Quest.getByID(session, quest_id)
        if force == False:
            # This means if the quest is not active,
            # because the ORM returns an empty list
            if quest.active == []:
                print("COULD NOT GIVE REWARD FOR QUEST ID: %s, QUEST IS NOT ACTIVE" % (quest_id))
                return False

        
        self.xp = self.xp + quest.xp
        self.sect_coins = self.sect_coins + quest.sect_coins

        # Give user the ranks
        for questRank in quest.ranks:
            userRank = UserRank(rank_id = questRank.id, user_id = self.id)
            session.add(userRank)

        # Add the quest to quest_user database
        userQuest = UserQuest(quest_id = quest.id, user_id = self.id)
        session.add(userQuest)
        session.commit()
        return True
        

    @staticmethod
    def getByID(session, id):
        """
        Returnns an ORM (object) where the User.id is matched
        """
        return session.query(User).filter(User.id == id).first()
    
    @staticmethod
    def getByDiscordID(session, discord_id):
        """
        Returnns an ORM (object) where the User.discord_id is matched
        """
        return session.query(User).filter(User.discord_id == discord_id).first()

class Ideea(Base):
    __tablename__ = 'ideea'
    id = Column(Integer, primary_key = True)
    user_id = Column(None, ForeignKey(User.id))
    name = Column(String, nullable = False)

# Used for whatsapp (No implementation yet)
class UserPhoneNumber(Base):
    __tablename__ = 'user_phone_number'
    id = Column(Integer, primary_key=True)
    user_id = Column(None, ForeignKey(User.id))
    # Save the phone number as a string because we might need to add country prefixes
    number = Column(String, nullable = False)
    country_prefix = Column(String, default = '+40')

    


class Quest(Base):


    __tablename__ = 'quest'
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, default = False)
    type = Column(String, nullable = False)
    rarity = Column(String, nullable = False)
    name = Column(String, nullable = False)
    task = Column(String, nullable = False)
    interval_days = Column(Integer,nullable = False)
    xp = Column(Integer, default = 0)
    sect_coins = Column(Integer, default = 0)


    # BACKREFS
    active = relationship('QuestActive', backref = 'quest')
    ranks = relationship('QuestRank', backref = 'quest')

    # FUNCTIONS
    @staticmethod
    def getByID(session, quest_id):
        """
        Returns an ORM where the Quest.id is matched
        """
        return session.query(Quest).filter(Quest.id == quest_id).first()


    @staticmethod
    def startRandom(session):
        """
        Returns the id of the started quest
        """
        rarity = Rarities.getRandomRarity()
        # Select a random quest from the database based on the random % rarity
        quest = None
        while True:
            # Rpeat this process until you get a not already active/valid/enabled quest
            quest = session.query(Quest).filter(Quest.rarity == rarity).order_by(func.random()).first()
            #TODO: isQuestActive()
            
            if quest.is_active == True and quest.isActive(session) == False:
                break

        activequest = QuestActive(time_stop = datetime.datetime.now() + datetime.timedelta(days = quest.interval_days),
         quest = quest
        )
        print("Started random quest %s" % (quest.id))
        session.add(activequest)
        session.commit()
        return quest.id
    
    def isActive(self, session):
        if self.active == []:
            return False
        else:
            return True


class QuestActive(Base):
    __tablename__ = 'quest_active'
    id = Column(Integer, primary_key=True)
    quest_id = Column(None, ForeignKey(Quest.id))
    # This isn't very good, but its better than nothing
    # TODO: Does storing the time_start even make sense 
    # func.now() is -3hours from my timezone
    time_start = Column(DateTime, default = func.now()) 
    #time = datetime.datetime.now() + datetime.timedelta(days = 1)
    time_stop = Column(DateTime, nullable = False)

    @staticmethod
    def updateActive(session):
        """
        Returns a list with id's of the deleted quests
        """
        # THIS IS VALID -> session.query(QuestActive).filter(datetime.datetime.now() >= QuestActive.time_stop).delete()
        # BUT I can't tell if it deleted anything or not, so for better debugging I will do it like this:
        i = 0
        deletedQuestIds = []
        activeQuests = session.query(QuestActive)
        for activeQuest in activeQuests:
            if datetime.datetime.now() >= activeQuest.time_stop:
                i += 1
                deletedQuestIds.append(activeQuest.quest_id)
                session.delete(activeQuest)
                print("Removed from active list quest %s, added on %s/%s" %(activeQuest.quest_id,
                activeQuest.time_start.day, activeQuest.time_start.month))
                session.commit()

        return deletedQuestIds


    @staticmethod
    def get(session):
        """
        Returns a list with id's of all the active quests
        """
        # Get all the active quests
        activeQuests = session.query(QuestActive)
        session.commit()
        ids = []
        # Save only the quest ids
        for activeQuest in activeQuests:
            ids.append(activeQuest.quest_id)
        return ids

    @staticmethod
    def getById(session, quest_id):
        """
        Returns the ORM of quest_active
        """
        return session.query(QuestActive).filter(QuestActive.quest_id == quest_id).first()


class UserQuest(Base):
    __tablename__ = 'user_quest'
    id = Column(Integer, primary_key=True)
    quest_id = Column(None, ForeignKey(Quest.id))
    user_id = Column(None, ForeignKey(User.id))
    date = Column(DateTime, default = func.now())




class QuestRank(Base):
    __tablename__ = 'quest_rank'
    id = Column(Integer, primary_key=True)
    quest_id = Column(None, ForeignKey(Quest.id))
    name = Column(String, nullable = False)

class UserRank(Base):
    __tablename__ = 'user_rank'
    id = Column(Integer, primary_key=True)
    user_id = Column(None, ForeignKey(User.id))
    rank_id = Column(None, ForeignKey(QuestRank.id))
    quest_rank = relationship('QuestRank', backref = 'user_rank')

 
# Create all the tables in the database
Base.metadata.create_all(engine)


if __name__ == '__main__':
    s = session()
    user = User.getByID(s,35)
    cmpquests = user.getCompletedQuests(s)
    print(cmpquests)