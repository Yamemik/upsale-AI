import bcrypt


def get_password_hash(password: str) -> str:
    # bcrypt ограничивает пароль 72 байтами
    raw = password.encode("utf-8")[:72]
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("ascii")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    raw = plain_password.encode("utf-8")[:72]
    try:
        return bcrypt.checkpw(raw, hashed_password.encode("ascii"))
    except ValueError:
        return False
