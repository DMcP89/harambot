from enum import Enum

class DatabaseType(Enum):
    SQLITE = 'sqlite'
    MYSQL = 'mysql'
    POSTGRES = 'postgres'