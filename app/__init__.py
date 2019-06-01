import os
import time
from importlib import import_module
from logging import basicConfig, DEBUG, getLogger, StreamHandler

import face_recognition
from flask import Flask, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

known_image = face_recognition.load_image_file("./upload/me.jpg")
my_face_encoding = face_recognition.face_encodings(known_image)[0]


# 毫秒级时间戳，基于lambda
def now_time():
    return int(round(time.time() * 1000))


db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)


def register_blueprints(app):
    for module_name in ('base', 'forms', 'ui', 'home', 'tables', 'data', 'additional', 'base'):
        module = import_module('app.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):
    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def configure_logs(app):
    basicConfig(filename='error.log', level=DEBUG)
    logger = getLogger()
    logger.addHandler(StreamHandler())


def apply_themes(app):
    """
    Add support for themes.

    If DEFAULT_THEME is set then all calls to
      url_for('static', filename='')
      will modfify the url to include the theme name

    The theme parameter can be set directly in url_for as well:
      ex. url_for('static', filename='', theme='')

    If the file cannot be found in the /static/<theme>/ lcation then
      the url will not be modified and the file is expected to be
      in the default /static/ location
    """

    @app.context_processor
    def override_url_for():
        return dict(url_for=_generate_url_for_theme)

    def _generate_url_for_theme(endpoint, **values):
        if endpoint.endswith('static'):
            themename = values.get('theme', None) or \
                        app.config.get('DEFAULT_THEME', None)
            if themename:
                theme_file = "{}/{}".format(themename, values.get('filename', ''))
                if os.path.isfile(os.path.join(app.static_folder, theme_file)):
                    values['filename'] = theme_file
        return url_for(endpoint, **values)


def create_app(config, selenium=False):
    app = Flask(__name__, static_folder='base/static')
    app.config.from_object(config)
    if selenium:
        app.config['LOGIN_DISABLED'] = True
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    configure_logs(app)
    apply_themes(app)

    # 上传文件 API
    @app.route('/api/upload', methods=['POST'], strict_slashes=False)
    def api_upload():
        f = request.files['file']
        if f and f.filename.rsplit('.', 1)[1] == 'jpg':  # 判断是否是允许上传的文件类型
            image = face_recognition.load_image_file(f)
            print('{}:loaded image'.format(now_time()))

            unknown_face_encoding = face_recognition.face_encodings(image)[0]
            print('{}:encoded face'.format(now_time()))

            results = face_recognition.compare_faces([my_face_encoding], unknown_face_encoding)
            print('{}:compared faces'.format(now_time()))

            if results[0]:
                print("匹配！")
                return jsonify({"errno": 0, "errmsg": "识别成功", "resident": "侯先生"})
            else:
                print("不匹配")
                return jsonify({"errno": 1001, "errmsg": "识别失败，该人脸未注册"})

    return app
