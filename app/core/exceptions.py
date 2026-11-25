# app/core/exceptions.py
class ServiceError(Exception):
    """Базовая ошибка сервиса."""

    def __init__(self, message: str, *, code: str = "service_error", status: int = 500):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status


class LLMUnavailableError(ServiceError):
    def __init__(self, message: str = "LLM temporarily unavailable"):
        super().__init__(message, code="llm_unavailable", status=503)


class LLMContentFilteredError(ServiceError):
    def __init__(self, message: str = "Content filtered by moderation"):
        super().__init__(message, code="content_filtered", status=422)


class TextTooLongError(ServiceError):
    def __init__(self, limit: int, got: int):
        super().__init__(
            f"Text too long: {got} > {limit}", code="text_too_long", status=413
        )
