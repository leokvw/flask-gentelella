from flask import render_template, session
from flask_login import login_required

from app.base.models import Resident, Access, Capture
from app.home import blueprint


@blueprint.route('/index')
@login_required
def index():
    # 总住户数量
    total_resident = Resident.query.count()
    # 总解锁次数
    total_access = Access.query.count()
    # 总检测次数，包括人脸不匹配
    total_capture = Capture.query.count()
    return render_template('index.html',
                           total_resident=total_resident,
                           total_access=total_access,
                           total_capture=total_capture)


@blueprint.route('/monitor')
@login_required
def monitor():
    return render_template('monitor.html')


@blueprint.route('/warn')
@login_required
def warn():
    return render_template('warn.html')
