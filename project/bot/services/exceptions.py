class ServiceError(Exception):
    pass


class AccessDeniedError(ServiceError):
    pass


class ProviderError(ServiceError):
    pass
