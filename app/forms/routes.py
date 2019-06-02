import os

import face_recognition
from flask import render_template, redirect, url_for
from flask_login import login_required
from werkzeug.utils import secure_filename

from app.base.models import *
from app.base.forms import *
from app.forms import blueprint


@blueprint.route('/form_building', methods=['GET', 'POST'])
@login_required
def create_building_form():
    form = BuildingForm()
    if form.validate_on_submit():
        building = Building(number=form.number.data, name=form.name.data)
        db.session.add(building)
        db.session.commit()
        return redirect(url_for('tables_blueprint.render_building'))
    return render_template('form_building.html', form=form)


@blueprint.route('/form_resident', methods=['GET', 'POST'])
@login_required
def create_resident_form():
    form = ResidentForm()
    if form.validate_on_submit():
        # 获取用户上传的包含人脸的图像
        # TODO 检查是否包含人脸且提示用户
        f = form.portrait.data
        image = face_recognition.load_image_file(f)
        face_encoding = face_recognition.face_encodings(image)[0]
        filename = secure_filename(f.filename)
        resident = Resident(name=form.name.data,
                            mobile=form.mobile.data,
                            password=form.password.data,
                            building=form.building.data,
                            face_encoding=face_encoding)
        db.session.add(resident)
        db.session.commit()
        f.save(os.path.join(os.getcwd() + '/resident', str(resident.id)) + os.path.splitext(filename)[1])

        return redirect(url_for('tables_blueprint.render_residents'))
    return render_template('form_resident.html', form=form)


@blueprint.route('/form_visitor', methods=['GET', 'POST'])
@login_required
def create_visitor_form():
    form = VisitorForm()
    if form.validate_on_submit():
        visitor = Visitor(name=form.name.data, is_expire=False, building=form.building.data)
        db.session.add(visitor)
        db.session.commit()
        return redirect(url_for('tables_blueprint.render_visitors'))
    return render_template('form_visitor.html', form=form)
