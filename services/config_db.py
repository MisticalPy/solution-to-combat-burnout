import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Конфигурация приложения"""

    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'employees_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    @classmethod
    def get_database_url(cls):
        """Получить URL для подключения к БД"""
        if cls.DB_PASSWORD:
            return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        else:
            return f"postgresql://{cls.DB_USER}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"


if __name__ == "__main__":
    print('Запуск программы должен быть из функции main')
