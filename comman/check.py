import jwt

def protected(token):
    try:
        decoded = jwt.decode(token, key='secret', algorithms=['HS256'])
        return {'decoded': decoded, 'message': 'Verified'}
    except jwt.ExpiredSignatureError:
        return {'decoded': None, 'message': 'Expired'}
    except jwt.InvalidTokenError:
        return {'decoded': None, 'message': 'Invalid'}