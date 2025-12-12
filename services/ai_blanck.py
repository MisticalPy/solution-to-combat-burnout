import logging
from services.PythonScripts.database import Database
from services.PythonScripts.excel_reader import ExcelReader
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_employee_data(name, famili):
    EXCEL_FILE = 'services/PythonScripts/employees.xlsx'

    db = Database()
    if not db.connect():
        logger.error(
            "Не удалось подключиться к БД. Проверьте настройки в .env")
        return "Ошибка подключения к базе данных"

    db.create_tables()

    reader = ExcelReader(EXCEL_FILE)
    if not reader.read_file():
        logger.error("Не удалось прочитать файл Excel")
        return "Ошибка чтения файла Excel"

    employees_data = reader.get_employees_data()
    if not employees_data:
        logger.error("Не удалось получить данные сотрудников")
        return "Данные сотрудников не найдены"

    success = db.insert_employees_bulk(employees_data)

    if success:
        employees = db.get_all_employees()
        logger.info(f"✓ Всего записей в БД: {len(employees)}")

    employee = db.search_employee_by_name(name, famili)

    if employee:
        result = []
        for i, emp in enumerate(employee, 1):
            result.append(f"\n{'=' * 60}")
            result.append(f"СОТРУДНИК {i}: {emp.fio}")
            result.append(f"{'=' * 60}")

            data = [
                ("ID", emp.id), ("ФИО", emp.fio),
                ("Производительность (июнь)", emp.june_performance),
                ("Производительность (июль)", emp.july_performance),
                ("Производительность (август)", emp.august_performance),
                ("Производительность (сентябрь)", emp.september_performance),
                ("Производительность (октябрь)", emp.october_performance),
                ("Аттестация", emp.certification),
                ("Последний отпуск", emp.last_vacation),
                ("Больничный в 2025", "Да" if emp.sick_leave_2025 else "Нет"),
                ("Выговор", "Да" if emp.reprimand else "Нет"),
                ("Участие в активностях",
                 "Да" if emp.corporate_activities else "Нет")
            ]

            for field_name, value in data:
                display_value = value if value is not None else "Не указано"
                result.append(f" {field_name:<30} {display_value}")
            break

        result.append(f"{'=' * 60}")
        return "\n".join(result)
    else:
        return "Сотрудник не найден"


def read_text_file(file_path):
    """Чтение текстового файла"""
    try:
        with open(file_path, 'r', encoding='UTF-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Файл {file_path} не найден")
        return None


def main(name: str = "Анна", famili: str = "Борисовна"):
    system_prompt = read_text_file(
        '/home/misticalpy/Desktop/mts_hacaton/services/PythonScripts/system_promt.txt'
    )
    messages = [
        {
            "role":
            "system",
            "content":
            f"Ты помощник для тестирования и борьбы с выгоранием сотрудников, используй эти данные: {system_prompt}"
        },
        {
            "role":
            "user",
            "content":
            f"Проанализируй данные о сотруднике {get_employee_data(name, famili)}, как думаешь, есть ли у него выгорание, ответ должен быть не более 5 предложений, выведи все структурированно, под полями Тренд,Рекомендации (Пиши с контекстом: советую порекомедовать...),Прогноз. "
        },
    ]

    client = OpenAI(
        api_key=
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjE2NzQ4MGQxLTg2M2UtNDgwNS04M2I5LTM2NmNhYjc4YmUxZSIsImlzRGV2ZWxvcGVyIjp0cnVlLCJpYXQiOjE3NjAxMDAwOTYsImV4cCI6MjA3NTY3NjA5Nn0.J3gXymMHdDASEjqrsJ9xywVRQmkLkbjJB0O3Sye-IvA',
        base_url='https://bothub.chat/api/v2/openai/v1')

    chat_completion = client.chat.completions.create(
        messages=messages,
        temperature=0.1,
        model='gpt-5-nano',
    )

    # print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content


def genQues():
    questions = read_text_file(
        '/home/misticalpy/Desktop/mts_hacaton/services/PythonScripts/questions.txt'
    )
    messages = [
        {
            "role":
            "system",
            "content":
            f"Ты помощник для тестирования и борьбы с выгоранием сотрудников, используй эти данные для генерации вопросов, 1 вопрос на каждый симптом, в сумме по каждому признаку должно быть 4 вопроса, ещё 3 вопроса для проверки правдаподобности ответов, бобщее количество вопросов - 15): Вопросы: {questions}, на все вопросы можно ответить: да/нет (не писать об этом в вопросе)"
        },
        {
            "role":
            "user",
            "content":
            f"Выбери вопросы и переформулируй их, выведи списком (формат [] для python)вопросы, сначала по порядку вопросы по признакам: напряжение, резистенция, истощение, затем вопросы для правдоподности"
        },
    ]

    client = OpenAI(
        api_key=
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjE2NzQ4MGQxLTg2M2UtNDgwNS04M2I5LTM2NmNhYjc4YmUxZSIsImlzRGV2ZWxvcGVyIjp0cnVlLCJpYXQiOjE3NjAxMDAwOTYsImV4cCI6MjA3NTY3NjA5Nn0.J3gXymMHdDASEjqrsJ9xywVRQmkLkbjJB0O3Sye-IvA',
        base_url='https://bothub.chat/api/v2/openai/v1')

    chat_completion = client.chat.completions.create(
        messages=messages,
        temperature=0.1,
        model='gpt-5-nano',
    )

    print(chat_completion.choices[0].message.content)
