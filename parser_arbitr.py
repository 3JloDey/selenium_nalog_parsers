import time
from contextlib import suppress
from random import uniform

from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from base import BaseParser
from exceptions import UndefinedError, ServiceUnavailableError


class ArbitrParser(BaseParser):
    """
    Парсер для проверки наличия судебных производств на сайте kad.arbitr.
    """
    URL = r"https://kad.arbitr.ru/"

    def __init__(self, timeout: int | float, headless: bool = True) -> None:
        """
        Инициализация парсера судебных производств.

        Args:
            timeout (int | float): Таймаут для ожидания элементов на странице (в секундах).
            headless (bool): Если True, запускает браузер в фоновом режиме без GUI (по-умолчанию True).
        """
        super().__init__(self.URL, timeout, headless)

    def parse(self, inn: str) -> bool:
        """
        Выполняет поиск судебных производств по ИНН.

        Args:
            inn (str): ИНН физического лица.
        Returns:
            bool: True — данные найдены, False — данные не найдены.
        Raises:
            ServiceUnavailableError: Сервис недоступен.
            UndefinedError: Неопределенная ошибка.
        """
        try:
            self._close_notification()
            self._input_inn(inn)
            self._submit_search()
            result = self._check_result()
            return result
        except NoSuchElementException:
            raise UndefinedError
        except TimeoutException:
            raise ServiceUnavailableError

    def _close_notification(self) -> None:
        """Закрывает начальное уведомление, если оно есть"""
        with suppress(TimeoutException):
            close_btn = self.wait_for_element_clickable(By.XPATH, '//*[@id="js"]/div[13]/div[2]/div/div/div/div/a[1]', timeout=5)
            close_btn.click()
            time.sleep(uniform(1, 1.5))

    def _input_inn(self, inn: str) -> None:
        """Вводит ИНН в поле поиска."""
        inn_field = self.wait_for_element_visibility(By.XPATH, '//*[@id="sug-participants"]/div/textarea')
        inn_field.send_keys(inn)
        time.sleep(uniform(1, 1.5))

    def _submit_search(self) -> None:
        """Кликает по кнопке для отправки запроса поиска."""
        submit_button = self.wait_for_element_clickable(By.XPATH, '//*[@id="b-form-submit"]/div/button')
        submit_button.click()
        time.sleep(uniform(1, 1.5))

    def _check_result(self) -> bool:
        """Проверяет результат поиска и возвращает статус."""
        self._wait_for_result_display()

        if self._is_element_displayed(By.CLASS_NAME, 'b-noResults'):
            return False
        elif self._is_element_displayed(By.CLASS_NAME, 'b-results'):
            return True
        else:
            raise UndefinedError

    def _wait_for_result_display(self) -> None:
        """Ожидает завершения поиска и отображения результатов."""
        WebDriverWait(self.driver, self.timeout).until(
            EC.any_of(
                EC.visibility_of_element_located((By.CLASS_NAME, "b-noResults")),
                EC.visibility_of_element_located((By.CLASS_NAME, "b-results")),
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
    with ArbitrParser(timeout=30, headless=False) as arbitr_parser:
        try:
            data = arbitr_parser.parse(inn="1234567890")
            print("Данные найдены" if data else "Данные не найдены")
        except (ServiceUnavailableError, UndefinedError) as ex:
            print(ex)


if __name__ == '__main__':
    main()
