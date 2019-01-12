from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger)
    created_at = Column(DateTime)
    upload_rating = Column(Integer, default=0)
    view_rating = Column(Integer, default=0)
    chat_name = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    login = Column(String)
    language_code = Column(String)
    role = Column(String)


class Img(Base):
    __tablename__ = 'img'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    created_at = Column(DateTime)
    archived_at = Column(DateTime)
    sum_rating = Column(Integer)
    name = Column(Text)
    media_type = Column(Text)
    count_rating = Column(Integer)
    rank = Column(Integer)
    telegram_file_id = Column(Text)
    reports_count = Column(Integer)
    user = relationship(User)


class Show(Base):
    __tablename__ = 'show'
    id = Column(Integer, primary_key=True)
    img_id = Column(Integer, ForeignKey('img.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    rating = Column(Integer)
    created_at = Column(DateTime)
    rated_at = Column(DateTime)
    reported_at = Column(DateTime)
    img = relationship(Img)
    user = relationship(User)

class InlineQuery(Base):
    __tablename__ = 'InlineQuery'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger)
    query = Column(Text)
    created_at = Column(DateTime)

