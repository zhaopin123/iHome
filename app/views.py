import datetime
import os
import random
import re

from flask import Blueprint, request, render_template, url_for, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import User, db, Area, House, Facility, Order, HouseImage
from utils.function import is_login

blue = Blueprint('first',__name__)


@blue.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
       return render_template('register.html')
    if request.method == 'POST':
        user = User()
        phone = request.form.get('mobile')
        imagecode = request.form.get('imagecode')
        pwd = request.form.get('password')
        password2 = request.form.get('password2')
        if phone and pwd and password2 and imagecode:
            if not re.match('^1[3456789]\d{9}$',phone):
                return jsonify({'code':1001,'msg':'手机号不正确'})
            if session['code'] != imagecode:
                return jsonify({'code': 1002, 'msg': '验证码不正确'})
            if User.query.filter(User.phone==phone).first():
                return jsonify({'code': 1003, 'msg': '用户名已存在'})
            if password2 != pwd:
                return jsonify({'code': 1004, 'msg': '密码不一致'})
            user.phone = phone
            user.name = phone
            user.pwd_hash = generate_password_hash(pwd)
            db.session.add(user)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '请求成功'})


@blue.route('/code/')
def get_code():
    #     获取验证码
    #    后端生成随机参数,返回给页面
    s='123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
    code = ''
    for i in range(4):
        code += random.choice(s)
    session['code'] = code
    return jsonify({'code':200, 'msg':'请求成功', 'data':code})


@blue.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        phone = request.form.get('mobile')
        password = request.form.get('password')
        user = User.query.filter_by(phone=phone).first()
        if user:
            if user.check_pwd(password):
                session['id'] = user.id
                return jsonify({'code': 200, 'msg': '请求成功'})
            return jsonify({'code': 1004, 'msg': '密码错误'})
        return jsonify({'code': 1001, 'msg': '用户不存在'})


@blue.route('/logout/')
@is_login
def logout():
    session.clear()
    return redirect(url_for('first.index'))


@blue.route('/index/',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        area_id = request.form.get('area_id')
        begin_date = request.form.get('begin_date')
        end_date = request.form.get('end_date')
        session['area_id'] = area_id
        session['begin_date'] = str(begin_date)
        session['end_date'] = str(end_date)
        return jsonify({'code':200, 'msg':'请求成功'})


@blue.route('/index_info/')
def index_info():
    if request.method == 'GET':
        house_list = []
        houses = House.query.order_by('-id').all()[:5]
        for house in houses:
            house_list.append(house.to_dict())
        if session.get('id'):
            data = {'user': True, 'houses': house_list}
        else:
            data = {'user': False, 'houses': house_list}
        return jsonify({'code': 200, 'msg': '请求成功', 'data': data})

@blue.route('/areas/',methods=['GET'])
def areas():
    if request.method == 'GET':
        area_list = []
        areas = Area.query.all()
        for area in areas:
            area_list.append({'id':area.id,'name':area.name})
        return jsonify({'code':200, 'msg':'请求成功', 'areas':area_list})


@blue.route('/detail/<int:id>/', methods=['GET','POST'])
@is_login
def detail(id):
    if request.method == 'GET':
        session['house_id'] = id
        return render_template('detail.html')
    if request.method == 'POST':
        return redirect(url_for('first.detail'))


@blue.route('/house_detail/')
@is_login
def house_detail():
    if request.method == 'GET':
        house_id = session.get('house_id')
        house = House.query.filter_by(id=house_id).first()
        if house:
            house_detail = house.to_full_dict()
            return jsonify({'code': 200, 'msg': '请求成功', 'house': house_detail})
        return jsonify({'code': 403, 'msg': '请求失败'})


@blue.route('/auth/',methods=['GET','POST'])
@is_login
def auth():
    if request.method == 'GET':
        return render_template('auth.html')
    if request.method == 'POST':
        str = '^[1-9][0-7]\d{4}((19\d{2}(0[13-9]|1[012])(0[1-9]|[12]\d|30))|(19\d{2}(0[13578]|1[02])31)|(19\d{2}02(0[1-9]|1\d|2[0-8]))|(19([13579][26]|[2468][048]|0[48])0229))\d{3}(\d|X|x)?$'
        name = request.form.get('real_name')
        idcard = request.form.get('id_card')
        if not all([name,idcard]):
            return jsonify({'code':1001,'msg':'字段不能为空'})
        if not re.match('^[\u4e00-\u9fa5]{2:10}$',name):
            return jsonify({'code': 1004, 'msg': '请填写真实姓名'})
        if not re.match(str,idcard):
            return jsonify({'code':1002,'msg':'身份证格式错误'})
        if User.query.filter_by(id_card=idcard).first():
            return jsonify({'code':1003,'msg':'身份证号有误'})
        id = session.get('id')
        user = User.query.filter_by(id=id).first()

        user.id_name = name
        user.id_card = idcard
        db.session.add(user)
        db.session.commit()
        return jsonify({'code':200,'msg':'请求成功'})


@blue.route('/my_auth/')
def my_auth():
    user_id = session.get('id')
    user = User.query.filter_by(id=user_id).first()
    if user.id_card:
        id_name = '**'+user.id_name[-1]
        id_card = user.id_card[:5] + '*********' + user.id_card[-3:]
        user_auth = {'id_name':id_name, 'id_card':id_card}
        return jsonify({'code':200, 'msg':'请求成功', 'data':user_auth})
    return jsonify({'code':1001, 'msg':'未通过认证'})

@blue.route('/is_auth/')
def is_auth():
    if request.method == 'GET':
        user_id = session.get('id')
        user = User.query.filter_by(id=user_id).first()
        if not user.id_card:
            return jsonify({'code': 400, 'msg': '您还没有实名认证,现在前往认证'})
        return jsonify({'code': 200, 'msg': '已通过认证'})


@blue.route('/myhouse_detail/')
def myhouse_detail():
    if request.method == 'GET':
        user_id = session.get('id')
        houses = House.query.filter_by(user_id=user_id).all()
        house_detail = []
        if houses:
            for house in houses:
                house_detail.append(house.to_dict())
            return jsonify({'code': 200, 'msg': '请求成功', 'houses': house_detail})
        return jsonify({'code': 403, 'msg': '您还没有发布任何房源'})


@blue.route('/booking/',methods=['GET','POST'])
@is_login
def booking():
    if request.method == 'GET':
        return render_template('booking.html')
    if request.method == 'POST':
        begin_date = request.form.get('begin_date')
        end_date = request.form.get('end_date')
        data = request.form.get('data')
        nums = re.findall(r'\d+',data)
        amount = int(nums[0])
        days = int(nums[2])
        session['begin_date'] = begin_date
        session['end_date'] = end_date
        list = random.sample('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890',10)
        order_id = ''
        for x in list:
            order_id += x
        house_id = session.get('house_id')
        house = House.query.filter_by(id=house_id).first()
        user_id = session.get('id')
        myorders = Order.query.filter_by(user_id=user_id).all()
        if house.user_id == user_id:
            return jsonify({'code':404,'msg':'您无法预定自己的房屋'})
        for myorder in myorders:
            if myorder.house_id == house_id:
                return jsonify({'code':404,'msg':'该房屋您已预定'})
        order = Order()
        order.user_id = user_id
        order.house_user_id = house.user_id
        order.house_id = house_id
        order.order_id = order_id
        order.begin_date = begin_date
        order.end_date = end_date
        order.days = days
        order.house_price = house.price
        order.amount = amount
        order.status = "WAIT_ACCEPT"
        db.session.add(order)
        db.session.commit()
        return jsonify({'code':200, 'msg':'请求成功'})


@blue.route('/order_status/',methods=['POST'])
def order_status():
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        reason = request.form.get('reason')
        comment = request.form.get('comment')
        order = Order.query.filter_by(id=order_id).first()
        if reason:
            order.comment = reason
            order.status = "REJECTED"
        elif comment:
            order.comment = comment
            order.status = "COMPLETE"
        else:
            order.comment = ''
            order.house.order_count += 1
            order.status = "WAIT_COMMENT"
        db.session.add(order)
        db.session.commit()
        return jsonify({'code':200, 'msg':'请求成功'})


@blue.route('/my_booking/')
def my_booking():
    if request.method == 'GET':
        house_id = session.get('house_id')
        house = House.query.filter_by(id=house_id).first()
        begin_date = session.get('begin_date')
        end_date = session.get('end_date')
        house_detail = house.to_dict()
        return jsonify({'code': 200, 'msg': '请求成功', 'data':{'house': house_detail,'end_date':end_date,'begin_date':begin_date}})


@blue.route('/lorders/',methods=['GET','POST'])
@is_login
def lorders():
    if request.method == 'GET':
        return render_template('lorders.html')


@blue.route('/my_orders/')
def my_orders():
    if request.method == 'GET':
        user_id = session.get('id')
        orders = Order.query.filter_by(user_id=user_id).order_by('-id').all()
        data = []
        for order in orders:
            data.append(order.to_dict())
        return jsonify({'code':200,'msg':'请求成功','data':data})


@blue.route('/my_lorders/')
def my_lorders():
    if request.method == 'GET':
        user_id = session.get('id')
        orders = Order.query.filter_by(house_user_id=user_id).order_by('-id').all()
        data = []
        for order in orders:
            data.append(order.to_dict())
        return jsonify({'code': 200, 'msg': '请求成功', 'data': data})


@blue.route('/my/')
@is_login
def my():
    if request.method == 'GET':
        return render_template('my.html')


@blue.route('/myinfo/')
def myinfo():
    if request.method == 'GET':
        user_id = session.get('id')
        user = User.query.filter_by(id=user_id).first()
        data = user.to_basic_dict()
        return jsonify({'code':200, 'msg':'请求成功', 'data':data})


@blue.route('/myhouse/',)
@is_login
def myhouse():
    if request.method == 'GET':
        return render_template('myhouse.html')


@blue.route('/newhouse/',methods=['GET','POST'])
@is_login
def newhouse():
    if request.method == 'GET':
        return render_template('newhouse.html')
    if request.method == 'POST':
        user_id = session.get('id')
        user = User.query.filter_by(id=user_id).first()
        if not user.id_card:
            return redirect(url_for('first.auth'))
        house = House()
        house.user_id = user_id
        house.title = request.form.get('title')
        house.price = request.form.get('price')
        house.area_id = request.form.get('area_id')
        house.address = request.form.get('address')
        house.room_count = request.form.get('room_count')
        house.acreage = request.form.get('acreage')
        house.unit = request.form.get('unit')
        house.capacity = request.form.get('capacity')
        house.beds = request.form.get('beds')
        house.min_days = request.form.get('min_days')
        house.max_days = request.form.get('max_days')
        facilities = request.form.getlist('facility')
        for fa_id in facilities:
            facility = Facility.query.filter_by(id=fa_id).first()
            house.facilities.append(facility)
        db.session.add(house)
        db.session.commit()
        session['house_id'] = house.id
        return jsonify({'code': 200, 'msg': '请求成功'})


@blue.route('/house_image/',methods=['POST'])
def house_image():
    house_id = session.get('house_id')
    house = House.query.filter_by(id=house_id).first()
    dict_file = request.files
    if 'house_image' in dict_file:
        f1 = request.files['house_image']
        if not re.match('image/.*', f1.mimetype):
            return jsonify({'code': 1001, 'msg': '文件类型错误'})
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        STATIC_DIR = os.path.join(BASE_DIR, 'static')
        MEDIA_DIR = os.path.join(STATIC_DIR, 'media')
        url = os.path.join(MEDIA_DIR, f1.filename)
        f1.save(url)
        if not house.index_image_url:
            house.index_image_url = f1.filename
            db.session.add(house)
        house_image = HouseImage()
        house_image.url = f1.filename
        house_image.house_id = house_id
        db.session.add(house_image)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '请求成功'})


@blue.route('/orders/')
@is_login
def orders():
    if request.method == 'GET':
        return render_template('orders.html')


@blue.route('/profile/', methods=['GET','POST'])
@is_login
def profile():
    if request.method == 'GET':
        return render_template('profile.html')
    if request.method == 'POST':
        user_id = session.get('id')
        user = User.query.filter_by(id=user_id).first()
        name = request.form.get('name')
        dict_file = request.files
        if 'avatar' in dict_file:
            f1 = request.files['avatar']
            if not re.match('image/.*', f1.mimetype):
                return jsonify({'code':1001,'msg':'文件类型错误'})
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # 媒体文件路径
            STATIC_DIR = os.path.join(BASE_DIR, 'static')
            MEDIA_DIR = os.path.join(STATIC_DIR, 'media')
            url = os.path.join(MEDIA_DIR, f1.filename)
            f1.save(url)
            user.avatar = f1.filename
        elif name:
            user.name = name
        db.session.add(user)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '请求成功','url':user.avatar})


@blue.route('/search/',methods=['GET','POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html')


@blue.route('/to_search/')
def to_search():
    if request.method =='GET':
        if request.args.get('area_id'):
            session['area_id'] = request.args.get('area_id')
        if request.args.get('begin_date') and request.args.get('begin_date'):
            session['begin_date'] = request.args.get('begin_date')
            session['end_date'] = request.args.get('end_date')
        area_id = session.get('area_id')
        begin_date = session.get('begin_date')
        end_date = session.get('end_date')
        key = request.args.get('key')
        housess = []
        if area_id:
            if key == 'booking':
                houses = House.query.filter_by(area_id=area_id).order_by('-order_count').all()
            elif key == 'price-inc':
                houses = House.query.filter_by(area_id=area_id).order_by('price').all()
            elif key == 'price-des':
                houses = House.query.filter_by(area_id=area_id).order_by('-price').all()
            else:
                houses = House.query.filter_by(area_id=area_id).order_by('-id').all()
        else:
            if key == 'booking':
                houses = House.query.order_by('-order_count').all()
            elif key == 'price-inc':
                houses = House.query.order_by('price').all()
            elif key == 'price-des':
                houses = House.query.order_by('-price').all()
            else:
                houses = House.query.order_by('-id').all()
        if begin_date and end_date:
            for house in houses:
                if house.orders:
                    for order in house.orders:
                        if order.status == "REJECTED" or order.status == "CANCELED":
                            continue
                        if datetime.datetime.strptime(order.end_date, "%Y-%m-%d") > datetime.datetime.strptime(begin_date, "%Y-%m-%d")>datetime.datetime.strptime(order.begin_date, "%Y-%m-%d")\
                                or datetime.datetime.strptime(order.end_date, "%Y-%m-%d") > datetime.datetime.strptime(end_date, "%Y-%m-%d")>datetime.datetime.strptime(order.begin_date, "%Y-%m-%d")\
                                or datetime.datetime.strptime(end_date, "%Y-%m-%d") > datetime.datetime.strptime(order.end_date, "%Y-%m-%d")>datetime.datetime.strptime(begin_date, "%Y-%m-%d"):
                            break
                    else:
                        housess.append(house)
                else:
                    housess.append(house)
        house_list = [house.to_full_dict() for house in housess]
        return jsonify({'code':200, 'msg':'请求成功', 'data':house_list})

@blue.route('/search_info/')
def search_info():
    area_id = session.get('area_id')
    area = Area.query.filter_by(id=area_id).first()
    begin_date = session.get('begin_date')
    end_date = session.get('end_date')
    if area_id:
        data = {'area_id': area_id, 'area_name': area.name, 'begin_date': begin_date, 'end_date': end_date}
        return jsonify({'code':200, 'msg':'请求成功', 'data':data})
    return jsonify({'code':1001, 'msg':'请求成功'})