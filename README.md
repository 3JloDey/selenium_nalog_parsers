# Selenium Nalog Parsers

Этот репозиторий содержит парсеры на Python для автоматизации проверки данных на сайтах [nalog.ru](https://www.nalog.gov.ru/) и [kad.arbitr.ru](https://kad.arbitr.ru/). \
Каждый парсер наследует базовый класс BaseParser, обеспечивающий работу с Selenium и упрощенное взаимодействие с веб-элементами.


### Установка и настройка
- Клонируйте репозиторий:\
`git clone https://github.com/3JloDey/selenium_nalog_parsers.git` \
`cd selenium_nalog_parsers`

- Установите зависимости:
`pip install -r requirements.txt`
- Настройте **WebDriver**: 
Загрузите драйвер для браузера, укажите путь к драйверу в BaseParser.DRIVER_PATH.

В репозитории имеется yandexdriver для корпоративной версии Яндекс Браузера.\
Вы можете использовать **любой драйвер и браузер**.


## Основные классы
### BaseParser
Базовый класс, реализующий:
* Инициализацию WebDriver с поддержкой headless-режима.
* Методы ожидания кликабельности и видимости элементов.
* Управление жизненным циклом драйвера и поддержку менеджера контекста.

### ArbitrParser
Описание: Парсер для проверки наличия судебных производств на сайте [kad.arbitr.ru](https://kad.arbitr.ru/).

Пример использования:
```python
from parser_arbitr import ArbitrParser

with ArbitrParser(timeout=30, headless=False) as arbitr_parser:
    if arbitr_parser.parse(inn="1234567890"):
        print("Данные найдены")
    else:
        print("Данные не найдены")
```

### InnParser
Описание: Парсер для получения информации об ИНН по личным данным.

Пример использования:
```python
from parser_inn import InnParser

with InnParser(timeout=30, headless=False) as inn_parser:
    inn = inn_parser.parse(
        surname="Иванов", name="Иван", lastname="Иванович",
        birthdate="01.01.1900", passport="12 34 567890"
    )
    print(f"ИНН: {inn}")
```

### NpdParser
Описание: Парсер для получения сведений о статусе профессионального дохода (самозанятости).

Пример использования:

```python
from parser_npd import NpdParser

with NpdParser(timeout=30, headless=False) as npd_parser: 
    if npd_parser.parse(inn="123123123123"):
        print("Является самозанятым")
    else:
        print("Не является самозанятым")
```

### RomParser
Описание: Парсер для проверки субъекта в реестре обеспечительных мер.

Пример использования:
```python
from parser_rom import RomParser

with RomParser(timeout=30, headless=False) as rom_parser:
    if rom_parser.parse(inn="1234567890"):
        print("Данные найдены") 
    else:
        print("Данные не найдены")
```
