from auth_app.models import UserInDB

users_db: dict[str, dict] = {
    'Dima': {
        'username': 'Dima',                     
        'email': 'dima@mail.ru',
        'is_active': True,
        'hashed_password': '$argon2id$v=19$m=65536,t=3,p=4$QicTqUD0DIUMxDBcAk6VnQ$b1zYgXTo9fQjFSdIHRQRgLkLdzngmiP1FaK9yq/7l3A'
    },
    'Maxim': {
        'username': 'Maxim',
        'email': 'maxim@mail.ru',
        'is_active': False,
        'hashed_password': '$argon2id$v=19$m=65536,t=3,p=4$3zamDmubR+y8JVnO8S8a6A$gDpxNTbBXRMzN5prFhjaZn1HEximzl/mRus1qD0H1NE'
    }
}

def get_user(db: dict[str, dict], username: str) -> UserInDB | None:
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)