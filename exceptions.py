class UndefinedError(Exception):
    def __str__(self) -> str:
        return "Неопознанная ошибка."

class ServiceUnavailableError(Exception):
    def __str__(self) -> str:
        return "Сервис временно не доступен. Повторите запрос позднее."

class FieldFormatError(Exception):
    def __str__(self) -> str:
        return "Ошибка формата полей."

class InnNotFoundError(Exception):
    def __str__(self) -> str:
        return "Информация об ИНН не найдена."

class DataVerificationError(Exception):
    def __str__(self) -> str:
        return "Данные не прошли однозначной проверки."

class ServiceCaptchaError(Exception):
    def __str__(self) -> str:
        return "Превышен лимит запросов. Повторите запрос позднее."
