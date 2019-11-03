from bottle import route, run, response, request, error, abort
import json
from db_processing import get_cats_to_web, add_cat, get_names_list, get_number_of_lines
from db_models import color_list


@route('/ping')
def ping():
    return 'Cats Service. Version 0.1'


@route('/cats')
def show_cats():
    response.set_header('Content-Type', 'application/json')
    params = dict(request.query)

    errors = set(params.keys()) - {'attribute', 'limit', 'offset', 'order'}
    if errors:
        abort(400, 'Check query params: ' + ', '.join(errors) + '\n'
                   'Available params: attribute, limit, offset, order')

    attribute = params.get('attribute', None)
    attr_list = ['name', 'color', 'tail_length', 'whiskers_length', None]
    if attribute not in attr_list:
        abort(400, f'The attribute must be: {", ".join(attr_list[0:-1])}')

    limit = params.get('limit', None)
    if limit is not None and number_not_valid(limit):
        abort(400, 'The limit must be non negative integer')

    offset = params.get('offset', None)
    if offset is not None:
        if number_not_valid(offset):
            abort(400, 'The offset must be non negative integer')
        number_of_lines = get_number_of_lines()
        if int(offset) >= number_of_lines:
            abort(400, f'There is nothing to show. '
                       f'The offset is greater than number of lines: {number_of_lines}')

    order = params.get('order', 'asc')
    if order not in ['asc', 'desc']:
        abort(400, 'The order must be "asc" or "desc"')

    return json.dumps(get_cats_to_web(attribute,
                                      limit,
                                      offset,
                                      order),
                      sort_keys=False)


@route('/cat', method='POST')
def new_cat():
    errors = set(request.json) - {'name', 'color', 'tail_length', 'whiskers_length'}
    if errors:
        abort(400, 'Check JSON keys: ' + ', '.join(errors) + '\n' + not_valid_json())

    name = request.json.get('name')
    color = request.json.get('color')
    tail_length = request.json.get('tail_length')
    whiskers_length = request.json.get('whiskers_length')
    if None in (name, color, tail_length, whiskers_length):
        abort(400, 'Not enough parameters.' + '\n' + not_valid_json())

    names_list = get_names_list()
    if name in names_list:
        abort(400, 'The name must be unique.\n'
                   'These names already exist:\n' + '\n'.join(names_list))

    if color not in color_list:
        abort(400, 'The color must be: ' + ', '.join(color_list))

    if number_not_valid(tail_length):
        abort(400, 'The tail_length must be non negative integer')

    if number_not_valid(whiskers_length):
        abort(400, 'The whiskers_length must be non negative integer')

    add_cat(name,
            color,
            int(tail_length),
            int(whiskers_length))
    return 'New cat added successfully'


@route('/help')
def help_info():
    msg = f"""
/cats [GET] ... to show cats

params to sort query:
\tattribute = ['name', 'color', 'tail_length', 'whiskers_length']
\tlimit = [int]
\toffset = [int]
\torder = ['asc', 'desc'] (asc - by default)

/cat [POST] ... to add new cat

params:
\tname = [str]
\tcolor = {color_list}
\ttail_length = [int]
\twhiskers_length = [int]
    """
    return msg


def number_not_valid(number):
    """
    Возвращает False если number - целое неотрицательное число (даже если оно передано строкой)
    Во всех остальных случаях возвращает True
    """
    if type(number) is str:
        try:
            if int(number) == float(number):
                if int(number) < 0:
                    return True
                else:
                    return False
        except ValueError:
            return True
    if number < 0 or type(number) == float:
        return True
    return False


def not_valid_json():
    """
    Возвращает шаблон запроса в случае невалидного JSON
    """
    response.status = 400
    template_json = json.dumps({'name': 'str',
                                'color': color_list,
                                'tail_length': 'int',
                                'whiskers_length': 'int'})
    return f'JSON template:\n{template_json}'


@error(400)
def error400(error):
    return 'RequestError. ' + error.body


@error(405)
def error_405(error):
    return 'Use POST method for /cat to add new cat\n' \
           'Use GET method for /cats to show cats\n' \
           'Use GET method for /help for more info'


@error(404)
def error_404(error):
    return 'Please check URL.\n' \
           '/cats [GET] to show cats\n' \
           '/cat [POST] to add new cat\n' \
           '/help [GET] for more info'


if __name__ == '__main__':
    run(host='localhost', port=8080)
