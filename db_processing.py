# Вычисление медианы и моды я провожу на клиентской стороное и без применения каких либо
# алгоритмов. Я понимаю, что часть расчетов при больших объемах данных разумнее проводить
# на стороне базы данных. Например, при поиске моды, подсчитать количество вхождений каждого
# значения можно было реализовав SELECT tail_length, COUNT(*) as count
#                                FROM cats
#                                GROUP BY tail_length
#                                ORDER BY count DESC;
#


import sqlalchemy as sqla
from collections import Counter
from db_models import Cat, Color, Statistics, create_session


def compute_colors(color_list):
    """
    Подсчитывает количество котов каждого цвета
    Создает строку с цветом или обновляет значение, если оно было
    :param color_list: список цветов
    """
    session = create_session()
    for color in color_list:
        count = session.query(Cat.color).filter(Cat.color == color).count()
        color_query = session.query(Color).filter(Color.color == color).scalar()
        if color_query is None:
            session.add(Color(color=color, count=count))
        else:
            session.query(Color).filter(Color.color == color).update({Color.count: count})
        session.commit()


def get_cats(number_of_lines=None, width=20):
    """
    Выводит на экран содержимое таблыцы cats
    :param number_of_lines: количество строк, выводимых на экран
                            если не указано, выводятся все строки
    :param width: ширина колонки в символах, по умолчанию 20
    """
    session = create_session()
    print(*[x.ljust(width, ' ') for x in Cat.__table__.columns.keys()])
    if number_of_lines is None:
        query = session.query(Cat)
        for i in query:
            print(*[str(x).ljust(width, ' ') for x in (i.name,
                                                       i.color,
                                                       i.tail_length,
                                                       i.whiskers_length)])
    else:
        query = session.query(Cat).limit(number_of_lines)
        for i in query:
            print(*[str(x).ljust(width, ' ') for x in (i.name,
                                                       i.color,
                                                       i.tail_length,
                                                       i.whiskers_length)])


def get_cats_to_web(attr, limit, offset, direction):
    """
    Возвращает список словарей с результатом запроса к таблице cats с параметрами
    :param attr: столбец сортировки, по  умолчанию сортировка не производится
    :param limit: количество выводимых строк, по умолчанию - все
    :param offset: номер строки, с которой начинается отсчет
    :param direction: направление сортировки, по умолчанию - по возврастанию
    :return: [{'name': ..., 'color': ..., 'tail_length': ..., 'whiskers_length': ...}]
    """
    session = create_session()
    if direction == 'desc':
        query = session.query(Cat).order_by(getattr(Cat, attr).desc() if attr else None)\
            .offset(offset)\
            .limit(limit)
    else:
        query = session.query(Cat).order_by(getattr(Cat, attr) if attr else None)\
            .offset(offset)\
            .limit(limit)
    cats = []
    for i in query:
        cats.append({'name': i.name,
                     'color': i.color,
                     'tail_length': i.tail_length,
                     'whiskers_length': i.whiskers_length
                     })
    return cats


def get_colors(width=20):
    """
    Выводит на экран содержимое таблицы cat_colors_info с сортировкой по убыванию
    :param width: ширина колонки в символах, по умолчанию 20
    """
    session = create_session()
    query = session.query(Color).order_by(Color.count.desc())
    print(*[x.ljust(width, ' ') for x in Color.__table__.columns.keys()])
    for i in query:
        print(*[str(x).ljust(width, ' ') for x in (i.color,
                                                   i.count)])


def get_stat(width=22):
    """
    Выводит на экран содержимое таблицы cats_stat
    :param width: ширина колонки в символах, по умолчанию 22
    """
    session = create_session()
    query = session.query(Statistics)
    print(*[x.ljust(width, ' ') for x in Statistics.__table__.columns.keys()])
    for i in query:
        print(*[str(x).ljust(width, ' ') for x in (i.tail_length_mean,
                                                   i.tail_length_median,
                                                   i.tail_length_mode,
                                                   i.whiskers_length_mean,
                                                   i.whiskers_length_median,
                                                   i.whiskers_length_mode)])


def compute_tail_length_mean():
    """
    Добавляет или обновляет значение tail_length_mean в таблице cats_stat
    """
    session = create_session()
    avg = round(session.query(sqla.func.avg(Cat.tail_length)).scalar(), 1)
    update_statistics('tail_length_mean', avg)


def compute_whiskers_length_mean():
    """
    Добавляет или обновляет значение whiskers_length_mean в таблице cats_stat
    """
    session = create_session()
    avg = round(session.query(sqla.func.avg(Cat.whiskers_length)).scalar(), 1)
    update_statistics('whiskers_length_mean', avg)


def compute_tail_length_median():
    """
    Добавляет или обновляет значение медианы tail_length_median в таблице cats_stat
    """
    session = create_session()
    query = session.query(Cat.tail_length).order_by(Cat.tail_length)
    query_list = [x.tail_length for x in query]
    median = find_list_median(query_list)
    update_statistics('tail_length_median', median)


def compute_whiskers_length_median():
    """
    Добавляет или обновляет значение медианы whiskers_length_median в таблице cats_stat
    """
    session = create_session()
    query = session.query(Cat.whiskers_length).order_by(Cat.whiskers_length)
    query_list = [x.whiskers_length for x in query]
    median = find_list_median(query_list)
    update_statistics('whiskers_length_median', median)


def find_list_median(target_list: list):
    """
    Возвращает медиану списка
    """
    half_length = len(target_list) // 2
    if len(target_list) % 2 == 0:
        median = round((target_list[half_length] + target_list[half_length - 1]) / 2, 1)
    else:
        median = target_list[half_length]
    return median


def compute_tail_length_mode():
    """
    Добавляет или обновляет значение моды tail_length_mode в таблице cats_stat
    """
    session = create_session()
    query = session.query(Cat.tail_length)
    tail_length_list = [x.tail_length for x in query]
    mode = find_list_mode(tail_length_list)
    update_statistics('tail_length_mode', mode)


def compute_whiskers_length_mode():
    """
    Добавляет или обновляет значение моды whiskers_length_mode в таблице cats_stat
    """
    session = create_session()
    query = session.query(Cat.whiskers_length)
    whiskers_length_list = [x.whiskers_length for x in query]
    mode = find_list_mode(whiskers_length_list)
    update_statistics('whiskers_length_mode', mode)


def update_statistics(column_name, value):
    session = create_session()
    first_line = session.query(Statistics).first()
    new_data = Statistics()
    setattr(new_data, column_name, value)
    if first_line is None:
        session.add(new_data)
    else:
        session.query(Statistics).update({column_name: value})
    session.commit()


def find_list_mode(target_list: list) -> list:
    """
    Возвращает моду списка. В случае мультимодальности, возвращает список всех мод
    """
    counter = Counter()
    for i in target_list:
        counter[i] += 1
    most_common = counter.most_common(1)[0][1]
    filtered_list = filter(lambda x: target_list.count(x) == most_common, target_list)
    return list(set(filtered_list))


def get_all_statistics():
    """
    Подсчитывает всю статистику и выводит на экран таблицу со статистикой
    """
    compute_whiskers_length_mean()
    compute_tail_length_mean()
    compute_whiskers_length_median()
    compute_tail_length_median()
    compute_whiskers_length_mode()
    compute_tail_length_mode()
    get_stat()


def add_cat(name, color, tail_length, whiskers_length):
    """
    Добавляет кота в таблицу cats
    """
    session = create_session()
    session.add(Cat(name=name,
                    color=color,
                    tail_length=tail_length,
                    whiskers_length=whiskers_length))
    session.commit()


def get_names_list():
    """
    Возвращает список имен из таблицы cats
    """
    session = create_session()
    query = session.query(Cat.name)
    return [i.name for i in query]


def get_number_of_lines():
    """
    Возвращает количество строк в таблице cats
    """
    session = create_session()
    return session.query(Cat).count()


# Посчитать и показать статистику по цветам:
# compute_colors(color_list)
# get_colors()

# Посчитать и показать всю статистику по усам и хвостам:
# get_all_statistics()

# Показать всех котов:
# get_cats()

# Показать статистику по усам и хвостам:
# get_stat()

# Показать статистику по цветам:
# get_colors()
