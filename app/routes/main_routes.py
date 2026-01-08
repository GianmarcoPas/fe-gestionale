from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    # Qui in futuro passeremo i dati veri dal database (count lavori, etc)
    return render_template('main/dashboard.html')