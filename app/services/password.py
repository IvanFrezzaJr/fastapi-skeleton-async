from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    """Hash a plain text password using the configured password context."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a plain text password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)
