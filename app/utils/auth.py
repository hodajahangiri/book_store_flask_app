from datetime import datetime, timedelta, timezone
from jose import jwt
from functools import wraps
from flask import request,jsonify
import jose


SECRET_KEY = 'SUPER SECRET secret key'

def encode_token(id):
    payload = {
        'iat' : datetime.now(timezone.utc), #issued 
        'exp' : datetime.now(timezone.utc) + timedelta(days=0, hours=1), #expiration data
        'sub' : str(id),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
        if not token:
            return jsonify({"error": "token missing from authorization headers"}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user_id = data['sub']
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message':'token is expired'}), 403
        except jose.exceptions.JWTError:
            return jsonify({'message':'invalid token'}), 401
        return f(*args, **kwargs)
    return decorator