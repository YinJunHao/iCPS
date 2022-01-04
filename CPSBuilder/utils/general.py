from datetime import datetime


def intersect(a, b):
    '''
    Return the intersection of two lists a and b.
    :param a:
    :param b:
    :return:
    '''
    return list(set(a) & set(b))


def union(a, b):
    '''
    Return the union of two lists a and b.
    :param a:
    :param b:
    :return:
    '''
    # return list(set(a) | set(b))
    return a + b


def unique(a):
    '''
    Return the list with duplicate elements removed.
    :param a:
    :return:
    '''
    return list(set(a))


def define_datetime_format():
    '''
    Standardize the datetime format.
    :return:
    '''
    return "%Y-%m-%d %H:%M:%S"


def format_datetime(dt_str):
    my_format = define_datetime_format()
    dt_before = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")
    dt_str = dt_before.strftime(my_format)
    dt_dt = datetime.strptime(dt_str, my_format)
    return dt_dt


def get_datetime_string(dt_dt):
    my_format = define_datetime_format()
    dt_str = dt_dt.strftime(my_format)
    return dt_str


def get_oldest_datetime(dt_list):
    return min(dt_list)


def get_youngest_datetime(dt_list):
    return max(dt_list)

