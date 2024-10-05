from flask import Blueprint, render_template, session
import requests

test_bp = Blueprint('test', __name__)
@test_bp.route('/test')
def test():
    return render_template('test.html')