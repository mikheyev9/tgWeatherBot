from datetime import datetime

from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Users(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger)
    city = Column(String(30))
    connection_date = Column(DateTime, default=datetime.now)
    reports = relationship('WeatherReports', backref='report', lazy=True,
                           cascade='all, delete-orphan')
    def _repr__(self):
        return self.tg_id

class WeatherReports(Base):
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey('Users.id'))
    date = Column(DateTime, default=datetime.now)
    temp = Column(String(20))
    feels_like = Column(String(20))
    wind_speed = Column(String(20))
    pressure_mm = Column(String(20))
    city = Column(String(30))

    def __repr__(self):
        return self.city