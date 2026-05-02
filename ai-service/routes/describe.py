from flask import Blueprint

describe_bp = Blueprint('describe', __name__)

@describe_bp.route('/describe', methods=['POST'])
def describe():
    return {"message": "Describe endpoint coming soon"}