# color_list - список возможных цветов котов я захардкодил, т.к. он известен заранее
#              хотя можно было достать его запросом SELECT DISTINCT color FROM cats;


import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ENUM
import inspect


DB_PATH = 'postgresql://wg_forge:a42@localhost:5432/wg_forge_db'

color_list = [
    'black',
    'white',
    'black & white',
    'red',
    'red & white',
    'red & black & white']

Base = declarative_base()


class Cat(Base):
    __tablename__ = 'cats'

    name = sqla.Column(sqla.TEXT,
                       primary_key=True)
    color = sqla.Column(ENUM(*color_list, name='cat_color'))
    tail_length = sqla.Column(sqla.INTEGER)
    whiskers_length = sqla.Column(sqla.INTEGER)


class Color(Base):
    __tablename__ = 'cat_colors_info'

    color = sqla.Column(ENUM(*color_list, name='cat_color'),
                        unique=True,
                        primary_key=True)
    count = sqla.Column(sqla.INTEGER)


class Statistics(Base):
    __tablename__ = 'cats_stat'

    tail_length_mean = sqla.Column(sqla.NUMERIC, primary_key=True, default=0)
    tail_length_median = sqla.Column(sqla.NUMERIC)
    tail_length_mode = sqla.Column(sqla.Integer)
    whiskers_length_mean = sqla.Column(sqla.NUMERIC)
    whiskers_length_median = sqla.Column(sqla.NUMERIC)
    whiskers_length_mode = sqla.Column(sqla.Integer)


def create_session():
    """
    Создаёт объект сессии для взаимодействия с БД
    :return: Объект сессии
    """
    print('обращение за сессией')
    engine = sqla.create_engine(DB_PATH)
    Session = scoped_session(sessionmaker(engine))
    a = Session()
    print('Session:', a)
    print('****', inspect.stack()[1][3])
    return a
