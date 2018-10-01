from sqlalchemy import Table, Column, ForeignKey, Boolean, Integer, String, DateTime
from sqlalchemy import select, insert, func
from sqlalchemy import create_engine,MetaData
import datetime
import time
dbpath = '/DataBase/QuesterCSSDG.db'
engine = create_engine('sqlite://%s' % dbpath, echo = False)
metadata = MetaData(engine)


connection = engine.connect()



# Tables
quests = Table('Quests', metadata,
    Column('id', Integer, primary_key = True),
    Column('type', String(50), nullable = False),
    Column('rarity', String(90), nullable = False),
    Column('status', Boolean, default = True),
    Column('name', String(100), nullable = False),
    Column('task', String(100), nullable = False),
    Column('time_days', Integer, nullable = False),
    Column('xp', Integer, default = 0),
    Column('sect_coins', Integer, default = 0)
)

active_quests = Table('Active_quests', metadata,
    Column('id', Integer, primary_key = True),
    Column('quest_id', None, ForeignKey('Quests.id'), nullable = False ),
    Column('date_start', DateTime, nullable = False),
    Column('date_stop', DateTime, nullable = False)
)

users = Table('Users', metadata,
    Column('id', Integer, primary_key = True),
    Column('discord_id', Integer, nullable = True),
    Column('name', String(150), nullable = True),
    Column('whatsapp_phone', Integer, nullable = True),
    Column('lv', Integer, default = 0),
    Column('xp', Integer, default = 0),
    Column('sect_coins', Integer, default = 0)
)

quest_ranks = Table('Quest_ranks', metadata,
    Column('id', Integer, primary_key = True),
    Column('quest_id', ForeignKey('Quests.id'), nullable = False),
    Column('rank', String(100), nullable = False)
)

user_ranks = Table('User_ranks', metadata,
    Column('id', Integer, primary_key = True),
    Column('user_id', None, ForeignKey('Users.id'), nullable = False),
    Column('rank_id', None, ForeignKey('Quest_ranks.id'))
)

completed_quests = Table('Completed_quests', metadata,
    Column('id', Integer, primary_key = True),
    Column('quest_id', None, ForeignKey('Quests.id'), nullable = False),
    Column('user_id', None, ForeignKey('Users.id'), nullable = False),
    Column('date', DateTime)
)

metadata.create_all(engine)
