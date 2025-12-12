class TestPrivateMethod:
    def __init__(self):
        self.__private_value = 42

    def _private_method(self):
        return self.__private_value

    def public_method(self):
        return self.__private_value