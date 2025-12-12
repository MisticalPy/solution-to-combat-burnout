from services.PythonScripts.ai_blanck import get_employee_data, main
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

main('Анна', 'Борисовна')
