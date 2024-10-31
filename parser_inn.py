from contextlib import suppress
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from base import BaseParser
from exceptions import (
    UndefinedError, ServiceUnavailableError, FieldFormatError,
    DataVerificationError, InnNotFoundError, ServiceCaptchaError
)


class InnParser(BaseParser):
    """
    Парсер для получения информации об ИНН по личным данным.
    """
    URL = r"https://service.nalog.ru/inn.do"

    def __init__(self, timeout: int | float, headless: bool = True) -> None:
        """
        Инициализация парсера ИНН.

        Args:
            timeout (int | float): Таймаут для ожидания элементов на странице (в секундах).
            headless (bool): Если True, запускает браузер в фоновом режиме без GUI (по-умолчанию True).
        """
        super().__init__(self.URL, timeout, headless)

    def parse(self, surname: str, name: str, lastname: str, birthdate: str, passport: str) -> str:
        """
        Выполняет проверку и получение ИНН на сайте https://service.nalog.ru/inn.do.

        Args:
            surname (str): Фамилия.
            name (str): Имя.
            lastname (str): Отчество.
            birthdate (str): Дата рождения в формате ДД.ММ.ГГГГ.
            passport (str): Паспорт в формате "xx xx xxxxxx".
        Returns:
            str: Найденный ИНН.
        Raises:
            InnNotFoundError: Если ИНН не найден.
            DataVerificationError: Ошибка верификации данных.
            FieldFormatError: Ошибка формата заполняемых данных.
            ServiceUnavailableError: Сервис недоступен.
            UndefinedError: Неопределенная ошибка.
        """
        try:
            self._bypass_personal_data_block()
            self._fill_personal_info(surname, name, lastname, birthdate, passport)
            self._submit_form()
            self._validate_input()
            return self._parse_result()
        except NoSuchElementException:
            raise UndefinedError
        except TimeoutException:
            raise ServiceUnavailableError

    def _bypass_personal_data_block(self) -> None:
        """Пропускает блок с подтверждением использования личных данных, если он присутствует."""
        personal_data = self._find_and_click(By.XPATH, '//*[@id="unichk_0"]')
        if personal_data:
            self._find_and_click(By.XPATH, '//*[@id="btnContinue"]')

    def _fill_personal_info(self, surname: str, name: str, lastname: str, birthdate: str, passport: str) -> None:
        """Заполняет поля формы личными данными."""
        self._fill_field(By.XPATH, '//*[@id="fam"]', surname)
        self._fill_field(By.XPATH, '//*[@id="nam"]', name)
        self._fill_field(By.XPATH, '//*[@id="otch"]', lastname)
        self._fill_field(By.XPATH, '//*[@id="bdate"]', birthdate)
        self._fill_field(By.XPATH, '//*[@id="docno"]', passport)

    def _fill_field(self, by: By, locator: str, value: str) -> None:
        """Заполняет одно поле значением."""
        field = self.wait_for_element_visibility(by, locator)
        self.driver.execute_script("arguments[0].value = arguments[1]", field, value)

    def _submit_form(self) -> None:
        """Отправляет форму на сервер."""
        self._find_and_click(By.XPATH, '//*[@id="btn_send"]')

    def _validate_input(self) -> None:
        """Проверяет валидность данных и отсутствие капчи."""
        try:
            self.driver.implicitly_wait(0)
            self._check_for_errors()
            self._check_for_captcha()
        finally:
            self.driver.implicitly_wait(self.timeout)

    def _check_for_errors(self) -> None:
        """Проверяет наличие ошибок в формате данных."""
        with suppress(TimeoutException):
            if self.wait_for_element_visibility(By.CLASS_NAME, 'field-errors', timeout=2):
                raise FieldFormatError

    def _check_for_captcha(self) -> None:
        """Проверяет наличие капчи и возбуждает исключение, если капча найдена."""
        with suppress(TimeoutException):
            if self.wait_for_element_visibility(By.XPATH, '//*[@id="uniDialogData"]', timeout=3):
                raise ServiceCaptchaError

    def _parse_result(self) -> str:
        """Обрабатывает и возвращает результат поиска ИНН."""
        self._wait_for_result_display()

        if self._is_element_displayed(By.ID, 'result_0'):
            raise InnNotFoundError
        elif self._is_element_displayed(By.ID, 'result_1'):
            return self.driver.find_element(By.XPATH, '//*[@id="resultInn"]').text
        elif self._is_element_displayed(By.ID, 'result_3'):
            raise DataVerificationError
        elif self._is_element_displayed(By.ID, 'result_err'):
            raise ServiceUnavailableError
        else:
            raise UndefinedError

    def _wait_for_result_display(self) -> None:
        """Ожидает отображения результата поиска."""
        WebDriverWait(self.driver, self.timeout).until(
            EC.any_of(
                EC.visibility_of_element_located((By.ID, "result_0")),
                EC.visibility_of_element_located((By.ID, "result_1")),
                EC.visibility_of_element_located((By.ID, "result_3")),
                EC.visibility_of_element_located((By.ID, "result_err")),
            )
        )

    def _is_element_displayed(self, by: By, value: str) -> bool:
        """Проверяет, отображен ли элемент на странице."""
        with suppress(NoSuchElementException):
            element = self.driver.find_element(by, value)
            return element.is_displayed()
        return False

    def _find_and_click(self, by: By, locator: str) -> bool:
        """Находит и кликает на элемент, если он существует."""
        with suppress(NoSuchElementException):
            element = self.driver.find_element(by, locator)
            self.driver.execute_script("arguments[0].click()", element)
            return True
        return False


# Пример использования
def main() -> None:
    with InnParser(timeout=30, headless=False) as inn_parser:
        try:
            data = inn_parser.parse(
                surname="Иванов", name="Иван", lastname="Иванович",
                birthdate="01.01.1900", passport="12 34 567890"
            )
            print(data)
        except (InnNotFoundError, DataVerificationError, FieldFormatError,
                ServiceUnavailableError, UndefinedError) as ex:
            print(ex)

if __name__ == '__main__':
    main()
