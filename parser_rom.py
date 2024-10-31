from contextlib import suppress

from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from base import BaseParser
from exceptions import UndefinedError, ServiceUnavailableError, FieldFormatError


class RomParser(BaseParser):
    """
    Парсер для получения данных из реестра обеспечительных мер.
    """
    URL = r"https://service.nalog.ru/rom/"

    def __init__(self, timeout: int | float, headless: bool = True) -> None:
        """
        Инициализация парсера реестра обеспечительных мер.

        Args:
            timeout (int | float): Таймаут для ожидания элементов на странице (в секундах).
            headless (bool): Если True, запускает браузер в фоновом режиме без GUI (по-умолчанию True).
        """
        super().__init__(self.URL, timeout, headless)

    def parse(self, inn: str) -> bool:
        """
        Выполняет поиск в реестре обеспечительных мер по ИНН.

        Args:
            inn (str): ИНН физического лица.
        Returns:
            bool: True — данные найдены, False — данные не найдены.
        Raises:
            ServiceUnavailableError: Сервис недоступен.
            FieldFormatError: Ошибка формата заполняемых данных.
            UndefinedError: Неопределенная ошибка.
        """
        try:
            self._input_inn(inn)
            self._submit_search()
            self._check_entry_validation()
            result = self._check_result()
            return result
        except NoSuchElementException:
            raise UndefinedError
        except TimeoutException:
            raise ServiceUnavailableError

    def _input_inn(self, inn: str) -> None:
        """Вводит ИНН в поле поиска."""
        inn_field = self.wait_for_element_visibility(By.XPATH, '//*[@id="query"]')
        self.driver.execute_script("arguments[0].value = arguments[1]", inn_field, inn)

    def _submit_search(self) -> None:
        """Кликает по кнопке для отправки запроса поиска."""
        submit_button = self.wait_for_element_clickable(By.XPATH, '//*[@id="pnlSearch"]/div[4]/div[2]/button')
        self.driver.execute_script("arguments[0].click()", submit_button)

    def _check_entry_validation(self) -> None:
        """Проверяет наличие ошибок в формате полей ввода."""
        with suppress(TimeoutException):
            if self.wait_for_element_visibility(By.CLASS_NAME, 'field-errors', timeout=2):
                raise FieldFormatError

    def _check_result(self) -> bool:
        """Проверяет результат поиска и возвращает статус."""
        self._wait_for_result_display()

        if self._is_element_displayed(By.ID, 'pnlNoData'):
            return False
        elif self._is_element_displayed(By.ID, 'pnlData'):
            return True
        else:
            raise UndefinedError

    def _wait_for_result_display(self) -> None:
        """Ожидает завершения поиска и отображения результатов."""
        WebDriverWait(self.driver, self.timeout).until(
            EC.any_of(
                EC.visibility_of_element_located((By.ID, "pnlData")),
                EC.visibility_of_element_located((By.ID, "pnlNoData")),
            )
        )

    def _is_element_displayed(self, by: By, value: str) -> bool:
        """Проверяет отображение элемента на странице."""
        with suppress(NoSuchElementException):
            element = self.driver.find_element(by, value)
            return element.is_displayed()
        return False


# Пример использования
def main():
    with RomParser(timeout=30, headless=False) as rom_parser:
        try:
            data = rom_parser.parse(inn="1234567890")
            print("Данные найдены" if data else "Данные не найдены")
        except (FieldFormatError, ServiceUnavailableError, UndefinedError) as ex:
            print(ex)


if __name__ == '__main__':
    main()
