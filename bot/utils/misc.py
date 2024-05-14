import base64


class URLSafe:
    @staticmethod
    def addpad(data: str) -> None:
        return data + '=' * (-len(data) % 4)

    @staticmethod
    def delpad(data: str) -> None:
        return data.rstrip('=')

    def encode(self, data: int) -> str:
        encoded = base64.urlsafe_b64encode(
            data.encode('utf-8'),
        )
        return self.delpad(encoded.decode('utf-8'))

    def decode(self, data: str) -> int:
        padded = self.addpad(data)
        decoded = base64.urlsafe_b64decode(padded)
        return decoded.decode('utf-8')


URLSafe = URLSafe()


class Commands:
    cmds: list[str] = []

    def __init__(self):
        self.start = 'start'
        self.batch = 'batch'
        self.broadcast = 'bc'
        self.configs = 'set'
        self.log = 'log'
        self.evaluate = 'e'
        self.restart = 'r'
        for attr, value in vars(self).items():
            self.cmds.append(value)


Commands = Commands()
