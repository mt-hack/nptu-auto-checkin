class InvalidCredentialsError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class TooManyAttemptsError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class TesseractError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
