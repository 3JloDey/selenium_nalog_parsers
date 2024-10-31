from abc import ABC, abstractmethod
from typing import Any, Optional

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BaseParser(ABC):
    """
    Базовый класс парсера для работы с Selenium WebDriver, включающий основные методы ожидания
    и настройки драйвера.
    """

    DRIVER_PATH = "yandexdriver.exe"

    def __init__(self, url: str, timeout: int | float, headless: bool) -> None:
        """
        Инициализация базового парсера.

        Args:
            url (str): URL страницы, которую необходимо открыть в браузере.
            timeout (int | float): Таймаут для ожидания элементов на странице (в секундах).
            headless (bool): Если True, запускает браузер в фоновом режиме без GUI.
        """
        self.timeout = timeout
        self.ua = UserAgent(browsers='chrome', os="windows", platforms="pc")
        self.driver = self._initialize_driver(headless)
        self.driver.get(url)

    def _initialize_driver(self, headless: bool) -> WebDriver:
        """Создает и настраивает драйвер Selenium с учетом заданных параметров."""
        options = webdriver.ChromeOptions()

        # Запуск в headless-режиме, если задано
        if headless:
            options.add_argument("--headless=new")

        # Скрытие признаков автоматизации
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Деактивация всплывающих окон и уведомлений
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-translate")
        options.add_argument("--disable-extensions")

        # Маскировка и оптимизация производительности
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")

        # Навигационные и media-параметры
        options.add_argument("--mute-audio")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")

        # Пользовательский агент и прочие параметры
        options.add_argument(f"user-agent={self.ua.random}")
        options.add_argument("start-maximized")
        options.add_argument("--ignore-certificate-errors")

        # Дополнительные параметры для повышения незаметности
        options.add_argument("--incognito")
        options.add_argument("--disable-sync")

        service = Service(executable_path=self.DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(self.timeout)

        return driver

    def wait_for_element_visibility(self, by: By, value: str, timeout: Optional[int | float] = None) -> WebElement:
        """Ожидает появления элемента на странице."""
        timeout = timeout or self.timeout
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((by, value)))

    def wait_for_element_clickable(self, by: By, value: str, timeout: Optional[int | float] = None) -> WebElement:
        """Ожидает, пока элемент станет кликабельным."""
        timeout = timeout or self.timeout
        return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((by, value)))

    @abstractmethod
    def parse(self, *args, **kwargs) -> Any:
        """Абстрактный метод для реализации логики парсинга, который должен быть определён в дочернем классе."""
        pass

    def close(self) -> None:
        """Закрытие браузера и освобождение ресурсов."""
        if self.driver:
            self.driver.quit()

    def __enter__(self) -> 'BaseParser':
        """Поддержка менеджера контекста для безопасного закрытия браузера."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Закрытие браузера при выходе из контекста."""
        self.close()
