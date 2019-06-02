from app.tables import blueprint
from app.base.models import *
from flask import render_template, request
from flask_login import login_required


@blueprint.route('/admin')
@login_required
def render_person():
    result = Admin.query.all()
    return render_template('admin.html', result=result)


@blueprint.route('/building', methods=['GET', 'POST'])
@login_required
def render_building():
    number = request.args.get('number')
    if number != '0':
        Building.query.filter_by(number=number).delete()
        db.session.commit()
    result = Building.query.all()
    # TODO 添加每栋楼住户数量
    return render_template('building.html', result=result)


@blueprint.route('/residents', methods=['GET', 'POST'])
@login_required
def render_residents():
    id = request.args.get('id')
    if id != '0':
        Resident.query.filter_by(id=id).delete()
        db.session.commit()
    result = Resident.query.all()

    return render_template('residents.html', result=result)


@blueprint.route('/visitors')
@login_required
def render_visitors():
    result = Visitor.query.all()
    return render_template('visitors.html', result=result)


@blueprint.route('/capture')
@login_required
def render_capture():
    result = Capture.query.all()
    return render_template('capture.html', result=result)


@blueprint.route('/access')
@login_required
def render_access():
    result = Access.query.all()
    return render_template('access.html', result=result)


@blueprint.route('/table')
@login_required
def render_table():
    return render_template('tables.html')


@blueprint.route('/table_dynamic')
@login_required
def render_dynamic_table():
    return render_template('tables_dynamic.html')
