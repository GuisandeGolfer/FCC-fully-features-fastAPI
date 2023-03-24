from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from .. import database, models, utils, oauth2, schemas

router = APIRouter(tags=['Authentication'])


@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(database.get_db)):

    is_user_in_db = models.User.email == user_credentials.username

    user_query = db.query(models.User).filter(is_user_in_db).first()

    if not user_query:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Invalid Credentials')

    if not utils.verify(user_credentials.password, user_query.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Invalid Credentials')

    access_token = oauth2.create_access_token(data={'user_id': user_query.id})

    return {'access_token': access_token, 'token_type': 'bearer'}
