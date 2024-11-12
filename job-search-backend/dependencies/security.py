from contextlib import contextmanager
from fastapi.security import OAuth2PasswordBearer 
from fastapi import HTTPException ,Request
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError,ExpiredSignatureError
from passlib.context import CryptContext


import _constants
import jwt
import bcrypt

# Function to hash password
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)




def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    vietnam_timezone = timezone(timedelta(hours=7))
    if expires_delta:
        expire = datetime.now(vietnam_timezone) + expires_delta
        print(expire)
    else:
        expire = datetime.now(vietnam_timezone) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, _constants.SECRET_KEY, algorithm=_constants.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    vietnam_timezone = timezone(timedelta(hours=7))
    if expires_delta:
        expire =  datetime.now(vietnam_timezone) + expires_delta
    else:
        expire = datetime.now(vietnam_timezone) + timedelta(days=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, _constants.JWT_REFRESH_KEY, algorithm=_constants.ALGORITHM)
    return encoded_jwt


def verified_user(auth_header: str):
    # validate the refresh jwt token
    if not auth_header:
        return {"status": 400, "message": "Authorization header missing"}
    
    if not auth_header.startswith("Bearer "):
       return {"status": 400, "message":"Authorization header must start with Bearer"}
    
    token = auth_header.split(" ")[1]
    try:
        # Giải mã JWT và xác thực
        payload = jwt.decode(token, _constants.SECRET_KEY, algorithms=[_constants.ALGORITHM])
        return payload
    except ExpiredSignatureError:
        # Xử lý khi token đã hết hạn
        return {"status": 401, "message": "Access token has expired"}
    except InvalidTokenError:
        # Xử lý khi token không hợp lệ
        return {"status": 405, "message": "Invalid token"}
    except Exception as e:
        # Xử lý các lỗi khác
        return {"status": 500, "message": f"An error occurred: {str(e)}"}


def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=500, detail="Authorization header missing")
    
    # Xác thực người dùng
    payload = verified_user(auth_header)
    if not payload:
        raise HTTPException(status_code=500, detail="Invalid token or unauthorized")
    
    return payload