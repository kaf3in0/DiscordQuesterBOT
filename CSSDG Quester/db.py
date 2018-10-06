from sqlalchemy import Column, DateTime, String, Boolean, Integer, Interval, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship

import datetime
import random
Base = declarative_base()

engine = create_engine('sqlite:///DB/data.db')
 
# Construct a sessionmaker object, use this object to make sessions across the aplication
session = sessionmaker(bind = engine)
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
    user_phone_numbers = relationship('UserPhoneNumber', backref = 'user')
    user_quests = relationship('UserQuest', backref = 'user')
    user_ranks = relationship('UserRank', backref = 'user')


# Used for whatsapp (No implementation yet)
class UserPhoneNumber(Base):
    __tablename__ = 'user_phone_number'
    id = Column(Integer, primary_key=True)
    user_id = Column(None, ForeignKey(User.id))
    # Save the phone number as a string because we might need to add country prefixes
    number = Column(Integer, nullable = False)
    country_prefix = Column(String, default = '+40')


class Quest(Base):
    class Types:
        BETIV = 'BETIV'
        NORMAL = 'NORMAL'
        DUBIOS = 'DUBIOS'
        PARIOR = 'PARIOR'
    
    class Rarities:
        # % CONSTATNS
        COMUN = 100
        EPIC = 60
        LEGENDAR = 25
        IMPOSIBIL = 5

        
        def getRandomRarity():
            """
                Returns a string with a random rarity based on the drop rate (%) 
            """
            r = random.randint(1,100)
            if r <= IMPOSIBIL:
                return "IMPOSIBIL"
            elif r <= LEGENDAR:
                return "LEGENDAR"
            elif r <= EPIC:
                return "EPIC"
            else:
                return "COMUN"

    __tablename__ = 'Quest'
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, default = False)
    type = Column(String, nullable = False)
    rarity = Column(String, nullable = False)
    name = Column(String, nullable = False)
    task = Column(String, nullable = False)
    interval = Column(Interval, nullable = False)
    xp = Column(Integer, default = 0)
    sect_coins = Column(Integer, default = 0)


    # BACKREFS
    quest_active = relationship('QuestActive', backref = 'quest')
    quest_ranks = relationship('QuestRank', backref = 'quest')


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


    def get(session):
        """
         Returns an ORM (object) with all the active quests, 
         acces to the quest itself is made by using backrefs:
         active.quest.name/id/type/rarity
         similarly, acces to quest_ranks is done like:
         active.quest.quest_ranks[0].rank
        """
        activeQuests = session.query(QuestActive)
        return activeQuests


class UserQuest(Base):
    __tablename__ = 'user_quest'
    id = Column(Integer, primary_key=True)
    quest_id = Column(None, ForeignKey(Quest.id))
    user_id = Column(None, ForeignKey(User.id))
    date = Column(DateTime, default = func.now())
    # TODO: Add the time it took to complete the quest, from the start to the time the user made it

class QuestRank(Base):
    __tablename__ = 'quest_rank'
    id = Column(Integer, primary_key=True)
    quest_id = Column(None, ForeignKey(Quest.id))
    rank = Column(String, nullable = False)

class UserRank(Base):
    __tablename__ = 'user_rank'
    id = Column(Integer, primary_key=True)
    user_id = Column(None, ForeignKey(User.id))
    rank_id = Column(None, ForeignKey(QuestRank.id))



 
# Create all the tables in the database
Base.metadata.create_all(engine)


