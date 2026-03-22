class ServiceError(Exception):
    pass


class AccessDeniedError(ServiceError):
    def __init__(self, code: str = "error.access_denied", **context: object) -> None:
        self.code = code
        self.context = context
        super().__init__(code)


class ProviderError(ServiceError):
    pass
