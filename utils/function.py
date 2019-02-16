
# 定义登陆装饰器
# 外层函数嵌套内层函数
# 2.外层函数返回内层函数
# 3.内层函数调用外层函数的参数
from functools import wraps

from flask import session, url_for, redirect


def is_login(func):
    @wraps(func)
    def check_status(*args, **kwargs):
        try:
            session['id']
            return func(*args, **kwargs)
        except Exception as e:
            return redirect(url_for('first.login'))
    return check_status