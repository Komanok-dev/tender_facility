from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from .database import get_db
from .models import Employee
from .schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

SECRET_KEY = "48f5e94e9773b64079cd71778b38bba6fb0d2f521ba8bf2632da3a070afb6160"
ALGORITHM = "HS256"

def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except JWTError:
        raise credentials_exception

    user = db.query(Employee).filter(Employee.id == token_data.id).first()
    if user is None:
        raise credentials_exception
    return user
