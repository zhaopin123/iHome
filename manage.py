import redis
from flask import Flask
from flask_script import Manager
from flask_session import Session

from app.models import db
from app.views import blue

app = Flask(__name__)

app.register_blueprint(blueprint=blue, url_prefix='/app')

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@119.23.76.19:3306/ihome'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
# login_manage.init_app(app)

app.secret_key = 'weardtfh85wesrfv645efsdvgfd'
manage = Manager(app)

if __name__ == '__main__':
    manage.run()