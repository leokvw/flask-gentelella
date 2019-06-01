from flask import render_template, redirect, url_for
from flask_login import login_required

from app.base.models import *
from app.base.forms import *
from app.forms import blueprint


@blueprint.route('/form_building', methods=['GET', 'POST'])
@login_required
def create_building_form():
    form = BuildingForm()
    if form.validate_on_submit():
        building = Building(number=form.id.data)
        db.session.add(building)
        db.session.commit()
        return redirect(url_for('tables_blueprint.render_building'))
    return render_template('form_building.html', form=form)


@blueprint.route('/form_resident', methods=['GET', 'POST'])
@login_required
def create_resident_form():
    form = ResidentForm()
    if form.validate_on_submit():
        resident = Resident()
        db.session.add(resident)
        db.session.commit()
        return redirect(url_for('table_blueprint.render_resident'))
    return render_template('form_resident.html', form=form)


@blueprint.route('/form_visitor', methods=['GET', 'POST'])
@login_required
def create_visitor_form():
    form = VisitorForm()
    if form.validate_on_submit():
        return redirect(url_for('table_blueprint.render_visitor'))
    return render_template('form_visitor.html', form=form)
