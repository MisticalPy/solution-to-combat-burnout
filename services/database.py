from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from services.PythonScripts.models import Base, Employee
from services.PythonScripts.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с базой данных"""

    def __init__(self):
        self.engine = None
        self.Session = None

    def connect(self):
        """Подключение к базе данных"""
        try:
            database_url = Config.get_database_url()

            # Создаём движок без проблемных параметров
            self.engine = create_engine(database_url, echo=False)

            # Проверка подключения
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()
                logger.info(f"✓ PostgreSQL подключен")

            self.Session = sessionmaker(bind=self.engine)
            logger.info("✓ Подключение к базе данных установлено")
            return True

        except Exception as e:
            logger.error(f"✗ Ошибка подключения к БД: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def create_tables(self):
        """Создание таблиц в базе данных"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("✓ Таблицы успешно созданы")
            return True
        except Exception as e:
            logger.error(f"✗ Ошибка создания таблиц: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def drop_tables(self):
        """Удаление всех таблиц"""
        try:
            Base.metadata.drop_all(self.engine)
            logger.info("✓ Таблицы успешно удалены")
            return True
        except Exception as e:
            logger.error(f"✗ Ошибка удаления таблиц: {e}")
            return False

    def table_exists(self, table_name):
        """Проверка существования таблицы"""
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()

    def get_session(self):
        """Получить сессию для работы с БД"""
        if self.Session:
            return self.Session()
        return None

    def insert_employee(self, employee_data):
        """Вставка данных сотрудника"""
        session = self.get_session()
        try:
            cleaned_data = self._clean_data(employee_data)
            employee = Employee(**cleaned_data)
            session.add(employee)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(
                f"✗ Ошибка вставки: {employee_data.get('fio', 'Unknown')}: {e}"
            )
            return False
        finally:
            session.close()

    def insert_employees_bulk(self, employees_list):
        """Массовая вставка сотрудников"""
        success_count = 0
        error_count = 0

        for i, emp_data in enumerate(employees_list, 1):
            if self.insert_employee(emp_data):
                success_count += 1
            else:
                error_count += 1

            if i % 10 == 0:
                logger.info(f"  Обработано: {i}/{len(employees_list)}")

        logger.info(
            f"✓ Успешно добавлено: {success_count}/{len(employees_list)}")

        if error_count > 0:
            logger.warning(f"⚠ Ошибок: {error_count}")

        return success_count > 0

    def _clean_data(self, data):
        """Очистка данных"""
        cleaned = {}
        for key, value in data.items():
            if isinstance(value, str):
                try:
                    value = value.encode('utf-8',
                                         errors='ignore').decode('utf-8')
                    value = ''.join(c for c in value
                                    if c.isprintable() or c in ' \n\r\t')
                    value = ' '.join(value.split())
                    cleaned[key] = value if value else None
                except:
                    cleaned[key] = None
            else:
                cleaned[key] = value
        return cleaned

    def get_all_employees(self):
        """Получить всех сотрудников"""
        session = self.get_session()
        try:
            employees = session.query(Employee).all()
            return employees
        except Exception as e:
            logger.error(f"✗ Ошибка получения данных: {e}")
            return []
        finally:
            session.close()

    def search_employee_by_name(self, first_name: str, last_name: str = None):
        """
        Поиск сотрудника по имени и фамилии

        Args:
            first_name: Имя сотрудника
            last_name: Фамилия сотрудника (опционально)

        Returns:
            List[Employee]: Список найденных сотрудников
        """
        session = self.get_session()
        try:
            # Если передана только фамилия в первом параметре
            if last_name is None:
                # Пытаемся разделить по пробелу
                name_parts = first_name.strip().split()
                if len(name_parts) >= 2:
                    last_name = name_parts[0]
                    first_name = ' '.join(name_parts[1:])
                else:
                    # Если только одно слово, ищем по частичному совпадению
                    query = session.query(Employee).filter(
                        Employee.fio.ilike(f"%{first_name}%"))
                    return query.all()

            # Поиск по имени и фамилии
            query = session.query(Employee).filter(
                Employee.fio.ilike(f"%{first_name}%"),
                Employee.fio.ilike(f"%{last_name}%"),
            )

            return query.all()

        except Exception as e:
            logger.error(
                f"✗ Ошибка поиска сотрудника {first_name} {last_name}: {e}")
            return []
        finally:
            session.close()

    def print_employee_details(self, employee):
        """
        Вывод всех данных сотрудника в читаемом формате
        """
        if not employee:
            print("Сотрудник не найден")
            return

        print("\n" + "=" * 70)
        print("ПОЛНЫЕ ДАННЫЕ СОТРУДНИКА")
        print("=" * 70)

        # Основная информация
        print("📋 ОСНОВНАЯ ИНФОРМАЦИЯ:")
        print(f"   ID: {employee.id}")
        print(f"   ФИО: {employee.fio}")
        print(f"   Юридическое лицо: {employee.legal_entity or 'Не указано'}")
        print(f"   Пол: {employee.gender or 'Не указан'}")
        print(f"   Город: {employee.city or 'Не указан'}")
        print(f"   Должность: {employee.position or 'Не указана'}")
        print(f"   Стаж: {employee.experience or 'Не указан'}")
        print(f"   Возраст: {employee.age or 'Не указан'}")
        print(f"   Подчиненные: {employee.subordinates or 'Не указаны'}")

        # Производительность
        print("\n📊 ПРОИЗВОДИТЕЛЬНОСТЬ:")
        print(f"   Июнь: {employee.june_performance or 'Нет данных'}")
        print(f"   Июль: {employee.july_performance or 'Нет данных'}")
        print(f"   Август: {employee.august_performance or 'Нет данных'}")
        print(f"   Сентябрь: {employee.september_performance or 'Нет данных'}")
        print(f"   Октябрь: {employee.october_performance or 'Нет данных'}")

        # Аттестация и обучение
        print("\n🎓 АТТЕСТАЦИЯ И ОБУЧЕНИЕ:")
        print(f"   Аттестация: {employee.certification or 'Не указана'}")
        print(f"   Обучение: {employee.training or 'Не указано'}")
        print(f"   Последний отпуск: {employee.last_vacation or 'Не указан'}")

        # Статус
        print("\n📝 СТАТУС:")
        print(
            f"   Больничный в 2025: {'✅ Да' if employee.sick_leave_2025 else '❌ Нет'}"
        )
        print(f"   Выговор: {'⚠️ Да' if employee.reprimand else '✅ Нет'}")
        print(
            f"   Участие в активностях: {'✅ Да' if employee.corporate_activities else '❌ Нет'}"
        )

        # Заметки
        if employee.notes:
            print(f"\n📌 ЗАМЕТКИ: {employee.notes}")

        # Служебная информация
        print(f"\n🕐 СЛУЖЕБНАЯ ИНФОРМАЦИЯ:")
        print(f"   Создан: {employee.created_at}")
        print(f"   Обновлен: {employee.updated_at}")
        print("=" * 70)


if __name__ == "__main__":
    print('Запуск программы должен быть из функции main')
