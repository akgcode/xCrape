from __future__ import annotations


class DomainError(Exception):
    pass


class InvalidTweetDataError(DomainError):
    pass


class PersistenceError(DomainError):
    pass


class APIClientError(DomainError):
    pass


class TelegramDeliveryError(DomainError):
    pass
