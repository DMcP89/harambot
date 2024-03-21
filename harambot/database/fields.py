from cryptography.fernet import Fernet
from peewee import Field


class EncryptedField(Field):
    def __init__(self, key, *args, **kwargs):
        super(EncryptedField, self).__init__(*args, **kwargs)
        self.key = key

    def db_value(self, value):
        f = Fernet(self.key)
        return f.encrypt(value.encode()).decode()

    def python_value(self, value):
        f = Fernet(self.key)
        return f.decrypt(value.encode()).decode()
