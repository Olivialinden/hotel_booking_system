from passlib.context import CryptContext
# bcrypt makes stolen passwords hard to crack

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def generate_password_hash(raw_password: str) -> str:
    # .hash(): call this object's method to hash plain password
    return password_context.hash(raw_password)


def check_password(raw_password: str, stored_hash: str) -> bool:
    return password_context.verify(raw_password, stored_hash)
