import re
from contextlib import suppress
from datetime import date
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from base import BaseParser
from exceptions import UndefinedError, ServiceUnavailableError, FieldFormatError


class NpdParser(BaseParser):
    """
    Парсер для получения сведений о статусе профессионального дохода (самозанятости).
    """

    URL = r"https://npd.nalog.ru/check-status/"

    def __init__(self, timeout: int | float, headless: bool = True) -> None:
        """
        Инициализация парсера самозанятости.

        Args:
            timeout (int | float): Таймаут ожидания элементов на странице (в секундах).
            headless (bool): Если True, запускает браузер в фоновом режиме без GUI (по-умолчанию True).
        """
        super().__init__(url=self.URL, timeout=timeout, headless=headless)

    def parse(self, inn: str) -> bool:
        """
        Проверяет регистрацию человека как плательщика налога на профессиональный доход (самозанятости).

        Args:
            inn (str): ИНН физического лица.
        Returns:
            bool: True — является самозанятым, False — не является самозанятым.
        Raises:
            ServiceUnavailableError: Сервис недоступен.
            FieldFormatError: Ошибка формата заполняемых данных.
            UndefinedError: Неопределенная ошибка.
        """
        try:
            self._fill_inn_field(inn)
            self._fill_date_field()
            self._submit_form()
            self._check_entry_validation()
            result_text = self._get_result_text()
            return self._analyze_result(result_text)

        except NoSuchElementException:
            raise UndefinedError

        except TimeoutException:
            raise ServiceUnavailableError

    def _fill_inn_field(self, inn: str) -> None:
        """Заполняет поле ИНН."""
        inn_field = self.wait_for_element_visibility(By.XPATH, '//*[@id="ctl00_ctl00_tbINN"]')
        self.driver.execute_script("arguments[0].value = arguments[1]", inn_field, inn)

    def _fill_date_field(self) -> None:
        """Заполняет поле даты текущей датой."""
        current_date = date.today().strftime("%d-%m-%Y")
        date_field = self.wait_for_element_visibility(By.XPATH, '//*[@id="ctl00_ctl00_tbDate"]')
        self.driver.execute_script("arguments[0].value = arguments[1]", date_field, current_date)

    def _submit_form(self) -> None:
        """Нажимает кнопку отправки формы."""
        submit_button = self.wait_for_element_clickable(By.XPATH, '//*[@id="ctl00_ctl00_btSend"]')
        self.driver.execute_script("arguments[0].click()", submit_button)

    def _check_entry_validation(self) -> None:
        """Проверяет наличие ошибок в заполнении формы."""
        with suppress(TimeoutException):
            WebDriverWait(self.driver, 2).until(
                EC.any_of(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="ctl00_ctl00_RequiredFieldValidator1"]')),
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="ctl00_ctl00_cv_Inn"]')),
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="ctl00_ctl00_RequiredFieldValidator2"]')),
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="ctl00_ctl00_CustomValidator1"]'))
                )
            )
            raise FieldFormatError("Ошибка в формате введенных данных.")

    def _get_result_text(self) -> str:
        """Получает текст результата проверки статуса самозанятости."""
        result_element = WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="content"]/div/div/div[1]/div[5]'))
        )
        return result_element.text.strip()

    @staticmethod
    def _analyze_result(text: str) -> bool:
        """
        Анализирует результат поиска по тексту.

        Args:
            text (str): Текст результата.
        Returns:
            bool: True если является самозанятым, False — если не является.
        Raises:
            ServiceUnavailableError: Ошибка, если статус не удалось определить.
        """
        pattern = r"\bне является\b|\bявляется\b"
        match = re.search(pattern, text)
        if not match:
            raise ServiceUnavailableError
        return match.group() == "является"


# Пример использования
def main():
    with NpdParser(timeout=30, headless=False) as npd_parser:
        try:
            is_self_employed = npd_parser.parse(inn="123123123123")
            print("Является самозанятым" if is_self_employed else "Не является самозанятым")
        except (FieldFormatError, ServiceUnavailableError, UndefinedError) as ex:
            print(ex)


if __name__ == '__main__':
    main()
