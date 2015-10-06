from sqlalchemy import (
    Column,
    Integer,
    String,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    
    uid = Column(String, primary_key=True)
    email = Column(String)
    data_used = Column(Integer)


class Link(Base):
    __tablename__ = 'link'
    
    uid = Column(Integer, primary_key=True)
    key = Column(String)