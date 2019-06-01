from app.tables import blueprint
from app.base.models import *
from flask import render_template
from flask_login import login_required


@blueprint.route('/person')
@login_required
def render_person():
    result = User.query.all()
    return render_template('person.html', result=result)


@blueprint.route('/building', methods=['GET', 'POST'])
@login_required
def render_building():
    result = Building.query.all()
    # TODO 添加每栋楼住户数量
    return render_template('building.html', result=result)


@blueprint.route('/residents')
@login_required
def render_residents():
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
