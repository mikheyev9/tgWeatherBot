from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, User, WeatherReport

from settings.config import url

engine = create_engine(url, echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def add_user(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id).first()
    if user is None:
        new_user = User(tg_id=tg_id)
        session.add(new_user)
        session.commit()

def set_user_city(tg_id, city):
    session = Session()
    user = session.query(User).filter(User.tg_id == tg_id).first()
    if user:
        user.city = city
        session.add(user)
        session.commit()
    else:
        new_user = User(tg_id=tg_id)
        new_user.city = city
        session.add(new_user)
        session.commit()

def create_report(tg_id, temp, feels_like, wind_speed, pressure_mm, city):
    session = Session()
    user = session.query(User).filter(User.tg_id == tg_id).first()
    new_report = WeatherReport(temp=temp, feels_like=feels_like, wind_speed=wind_speed,
                               pressure_mm=pressure_mm, city=city, owner=user.id)
    session.add(new_report)
    session.commit()

def get_user_city(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == tg_id).first()
    return user.city

def get_reports(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == tg_id).first()
    reports = user.reports
    return reports


