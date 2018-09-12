from datetime import datetime
import time


def do_format_date(value, cover_time=False):
    if cover_time:
        result = time.strftime('%Y-%m-%d %H:%H:%S', datetime.timetuple(value))
    else:
        result = time.strftime('%Y-%m-%d', datetime.timetuple(value))
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
