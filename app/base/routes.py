import time

import face_recognition
from bcrypt import checkpw
from flask import render_template, redirect, url_for
from flask import request, jsonify
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from skimage.exposure import adjust_gamma
from app import retinex
from app import db, login_manager
from app.base import blueprint
from app.base.forms import LoginForm, CreateAccountForm
from app.base.models import Admin, Resident, Visitor
from app.base.models import Capture, Access

config = retinex.config


@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.login'))


@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')


@blueprint.route('/fixed_<template>')
@login_required
def route_fixed_template(template):
    return render_template('fixed/fixed_{}.html'.format(template))


@blueprint.route('/page_<error>')
def route_errors(error):
    return render_template('errors/page_{}.html'.format(error))


## Login & Registration


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'login' in request.form:
        admin_id = request.form['id']
        password = request.form['password']
        admin = Admin.query.filter_by(id=admin_id).first()
        if admin and checkpw(password.encode('utf8'), admin.password):
            login_user(admin)
            return redirect(url_for('base_blueprint.route_default'))
        return render_template('errors/page_403.html')
    if not current_user.is_authenticated:
        return render_template(
            'login/login.html',
            login_form=login_form,
            create_account_form=create_account_form
        )
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/create_user', methods=['POST'])
def create_user():
    user = Admin(**request.form)
    db.session.add(user)
    db.session.commit()
    return jsonify('success')


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))


@blueprint.route('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'


# 毫秒级时间戳，基于lambda
def now_time():
    return int(round(time.time() * 1000))


# 设置访客 API
@blueprint.route('/api/add_visitor', methods=['POST'], strict_slashes=False)
def api_add_visitor():
    name = request.values.get('name')
    building = request.values.get('building')
    host_id = request.values.get('host_id')
    visitor = Visitor(name=name, building=building, host=host_id)
    db.session.add(visitor)
    db.session.commit()
    return jsonify({'id': visitor.id})


# 手动开门 API
@blueprint.route('/api/manual_open', methods=['POST'], strict_slashes=False)
def api_manual_open():
    resident_id = request.values.get('id')
    resident = Resident.query.filter_by(id=resident_id).first()
    access = Access(name=resident.name, building=resident.building, type=2)
    db.session.add(access)
    db.session.commit()
    print('Someone inside!')
    return jsonify({'result': 'success'})


# QRCode API
@blueprint.route('/api/qrcode', methods=['POST'], strict_slashes=False)
def api_qrcode():
    visitor_id = request.values.get('visitor_id')
    building = request.values.get('building')
    print("{} {} 请求访问...".format(building, visitor_id))
    visitor = Visitor.query.filter_by(building=building, name=visitor_id).first()
    if visitor:
        name = visitor.name
        visitor.is_expire = True
        db.session.commit()
        print("{} {} 允许访问".format(building, name))
        return jsonify({"errno": 1, "visitor": name})
    return jsonify({"errno": 1001, "errmsg": "识别失败，该访客未注册！"})


# 上传文件 API
@blueprint.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    f = request.files['file']
    building = request.values.get("building")
    neighbor = Resident.query.filter_by(building=building).all()
    resident_name = [x.name for x in neighbor]
    known_face_encoding = [x.face_encoding for x in neighbor]
    if f and f.filename.rsplit('.', 1)[1] == 'jpg':  # 判断是否是允许上传的文件类型
        image = face_recognition.load_image_file(f)
        print('楼号: {} {} 载入图像...'.format(building, now_time()))
        # 伽马变换
        image = adjust_gamma(image, 0.1)
        # Retinex
        # image = retinex.multi_scale_retinex_with_color_restoration(
        #     image,
        #     config['sigma_list'],
        #     config['G'],
        #     config['b'],
        #     config['alpha'],
        #     config['beta'],
        #     config['low_clip'],
        #     config['high_clip']
        # )
        print('楼号: {} {} 增强图像...'.format(building, now_time()))
        unknown_face_encoding = face_recognition.face_encodings(image)
        print('楼号: {} {} 检测人脸...'.format(building, now_time()))
        if len(unknown_face_encoding) > 0:
            # top, right, bottom, left = landmarks
            print('楼号: {} {} 开始比对人脸...'.format(building, now_time()))

            results = face_recognition.compare_faces(known_face_encoding, unknown_face_encoding[0])
            print('楼号: {} {} 人脸比对完成'.format(building, now_time()))

            for name, result in zip(resident_name, results):
                if result:
                    print("楼号: {} 匹配！".format(building))
                    capture = Capture(on_record=True, building=building)
                    db.session.add(capture)
                    access = Access(name=name, building=building)
                    db.session.add(access)
                    db.session.commit()
                    return jsonify({"errno": 0, "errmsg": "识别成功", "resident": name})
                else:
                    print("楼号: {} 失败！".format(building))
                    capture = Capture(on_record=False, building=building)
                    db.session.add(capture)
                    db.session.commit()
                    return jsonify({"errno": 1001, "errmsg": "识别失败，该人脸未注册！"})
        else:
            print("楼号: {} 未检测到人脸！".format(building))
            return jsonify({"errno": 1, "errmsg": "未检测到人脸！"})
    return "It's for api use!"


# Errors


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('errors/page_403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden():
    return render_template('errors/page_403.html'), 403


@blueprint.errorhandler(404)
def not_found_error():
    return render_template('errors/page_404.html'), 404


@blueprint.errorhandler(500)
def internal_error():
    return render_template('errors/page_500.html'), 500
