from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, fullname, username, password, rol_id,created_at) -> None:
        self.id = id
        self.username = username
        self.password = password
        self.fullname = fullname
        self.rol_id = rol_id
        self.created_at = created_at

    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)