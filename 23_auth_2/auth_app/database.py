from auth_app.models import UserInDB

users_db: dict[str, dict] = {
    'Dima': {
        'username': 'Dima',                     
        'email': 'dima@mail.ru',
        'is_active': True,
        'hashed_password': 'hashedpassworddima'
    },
    'Maxim': {
        'username': 'Maxim',
        'email': 'maxim@mail.ru',
        'is_active': False,
        'hashed_password': 'hashedpasswordmaxim'
    }
}

def get_user(db: dict[str, dict], username: str) -> UserInDB | None:
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)