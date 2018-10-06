from sqlalchemy import Column, DateTime, String, Boolean, Integer, Interval, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship

import datetime
import random



Base = declarative_base()

engine = create_engine('sqlite:///DB/data.db')
 


class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    pets = relationship("Pet", backref = 'person')
    foods = relationship("Food", backref = 'person')

class Pet(Base):
    __tablename__ = 'pet'
    id = Column(Integer, primary_key=True)
    person_id = Column(None, ForeignKey(Person.id))
    name = Column(String)

class Food(Base):
    __tablename__ = 'food'
    id = Column(Integer, primary_key=True)
    person_id = Column(None, ForeignKey(Person.id))
    name = Column(String)