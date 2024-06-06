import mysql.connector


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = cls._create_connection()
        return cls._instance

    @staticmethod
    def _create_connection():
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="rikshawride"
        )    
    
    def get_connection(self):
        return self.connection
