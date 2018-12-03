from datetime import datetime, date
import time


def do_format_date(value, cover_time=False):
    if cover_time:
        result = time.strftime('%Y-%m-%d %H:%H:%S', datetime.timetuple(value))
    else:
        result = time.strftime('%Y-%m-%d', datetime.timetuple(value))
    return result


def do_slicer(value, slices=None):
    if slices:
        if slices.count(':') == 1:
            start, end = slices.split(':')
            try:
                if start:
                    start = int(start)
                else:
                    start = None
                if end:
                    end = int(end)
                else:
                    end = None
            except ValueError as e:
                return value
            if start and end and start > end:
                raise ValueError('Input parameter first must less than two')
            result = value[start:end]
        else:
            raise ValueError('Input parameter error:example slicer("1:2")')
    else:
        result = value
    return result


def diff_time_year(value):
    """
        date类相减，获取差天数，计算年龄
    """
    result = ''
    if value and isinstance(value, date):
        today = date.today()
        sub_result = today - value
        result = sub_result.days // 365
    return result

# 可以给过滤器器一个名字，如果没有，默认就是函数的名字
# app.add_template_filter(list_reverse,'li_reverse')


if __name__ == '__main__':
    # 时间戳类型
    print(time.time())
    # time tuple是time.struct_time对象类型
    print(time.localtime(time.time()))
    # 时间戳类型 转化为datetime 类型
    print(datetime.fromtimestamp(time.time()))
    # datetime 对象类型
    print(datetime.now())
    # ----------------------------
    # datetime tuple是time.struct_time对象类型
    print(datetime.timetuple(datetime.now()))
    # 转化格式化字符串
    print(time.strftime('%Y-%m-%d %H:%M:%S', datetime.timetuple(datetime.now())))
