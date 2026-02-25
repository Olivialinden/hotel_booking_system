from passlib.context import CryptContext



# 创建一个密码加密工具
# 使用 bcrypt 算法（常见、安全） 这是在 创建一个对象（object） 
# 把这个对象存进变量 password_context
password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def generate_password_hash(raw_password: str) -> str:

    #.hash()：调用这个对象的方法，对明文密码进行加密
    return password_context.hash(raw_password)


def check_password(raw_password: str, stored_hash: str) -> bool:

    return password_context.verify(raw_password, stored_hash)
