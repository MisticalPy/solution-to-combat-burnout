import pandas as pd
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExcelReader:
    """Класс для чтения данных из Excel"""

    COLUMN_MAPPING = {
        'ФИО': 'fio',
        'юр.лицо': 'legal_entity',
        'пол': 'gender',
        'Город': 'city',
        'Должность': 'position',
        'Стаж': 'experience',
        'возраст': 'age',
        'В подчиненнии сотрудники': 'subordinates',
        'июнь': 'june_performance',
        'июль': 'july_performance',
        'август': 'august_performance',
        'сентябрь': 'september_performance',
        'октябрь': 'october_performance',
        'Прохождение аттестации (прошел/не прошел/нет аттестации)':
        'certification',
        'Обучение': 'training',
        'Отпуск (когда ходил в последний раз)': 'last_vacation',
        'Больничный (брал или нет в 2025 году)': 'sick_leave_2025',
        'Выговор (да/нет)': 'reprimand',
        'Участие в активностях корпоративных': 'corporate_activities',
    }

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None

    def read_file(self) -> bool:
        """Чтение Excel файла"""
        try:
            # Читаем Excel, используя первую строку как заголовок
            self.df = pd.read_excel(self.file_path,
                                    engine='openpyxl',
                                    header=0)

            # Если первая строка содержит "ФИО", значит это заголовки
            if self.df.columns[0] == 'Unnamed: 0':
                # Используем первую строку данных как заголовки
                logger.info("  Обнаружены заголовки в первой строке данных")
                new_header = self.df.iloc[0]
                self.df = self.df[1:]
                self.df.columns = new_header
                self.df = self.df.reset_index(drop=True)

            # Удаляем пустые строки
            self.df = self.df.dropna(how='all')

            logger.info(f"✓ Файл {self.file_path} успешно прочитан")
            logger.info(f"  Найдено строк: {len(self.df)}")
            logger.info(f"  Найдено столбцов: {len(self.df.columns)}")

            return True
        except Exception as e:
            logger.error(f"✗ Ошибка чтения файла: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def _clean_string(self, value):
        """Очистка строки"""
        if not isinstance(value, str):
            value = str(value) if value is not None else ''

        value = value.encode('utf-8', errors='ignore').decode('utf-8',
                                                              errors='ignore')
        value = ''.join(char for char in value
                        if char.isprintable() or char.isspace())
        value = ' '.join(value.split())

        return value.strip()

    def _convert_boolean(self, value) -> bool:
        """Конвертация в boolean"""
        if pd.isna(value):
            return False

        value_str = self._clean_string(str(value)).lower()
        return value_str in ['да', 'yes', 'true', '1', '+']

    def _clean_value(self, value):
        """Очистка значения"""
        if pd.isna(value):
            return None

        if isinstance(value, str):
            value = self._clean_string(value)
            return value if value else None

        return value

    def _parse_row(self, row: pd.Series) -> Dict:
        """Парсинг строки"""
        employee_data = {}

        for excel_col, db_field in self.COLUMN_MAPPING.items():
            if excel_col in row.index:
                value = row[excel_col]

                if db_field in [
                        'sick_leave_2025', 'reprimand', 'corporate_activities'
                ]:
                    employee_data[db_field] = self._convert_boolean(value)
                elif db_field == 'age':
                    try:
                        employee_data[db_field] = int(
                            value) if not pd.isna(value) else None
                    except (ValueError, TypeError):
                        employee_data[db_field] = None
                else:
                    employee_data[db_field] = self._clean_value(value)

        # Собираем заметки
        notes_parts = []
        for col in row.index:
            if col not in self.COLUMN_MAPPING:
                value = self._clean_value(row[col])
                if value:
                    notes_parts.append(f"{col}: {value}")

        if notes_parts:
            employee_data['notes'] = '; '.join(notes_parts)

        return employee_data

    def get_employees_data(self) -> List[Dict]:
        """Получить данные сотрудников"""
        if self.df is None:
            return []

        employees_data = []

        for index, row in self.df.iterrows():
            try:
                employee_data = self._parse_row(row)

                if employee_data.get('fio'):
                    fio = self._clean_string(str(employee_data['fio'])).lower()
                    if fio not in ['фио', 'nan', 'none', '']:
                        employees_data.append(employee_data)
            except Exception as e:
                logger.error(f"✗ Ошибка строки {index + 2}: {e}")
                continue

        logger.info(f"✓ Обработано {len(employees_data)} записей")
        return employees_data

    def print_preview(self, n_rows: int = 5):
        """Превью данных"""
        if self.df is None:
            return

        print("\n" + "=" * 80)
        print("ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР ДАННЫХ")
        print("=" * 80)
        print(self.df.head(n_rows))
        print("=" * 80 + "\n")


if __name__ == "__main__":
    print('Запуск программы должен быть из функции main')
