from PySide6.QtCore import QSettings


class AppSettings:
    def __init__(self):
        self.settings = QSettings("CompanyKit", "CompanyKitApp")

    def setUsername(self, username):
        self.settings.setValue("username", username)

    def getUsername(self):
        return self.settings.value("username", "")

    def setOpenAIKey(self, key):
        self.settings.setValue("openai/api_key", key)

    def getOpenAIKey(self):
        return self.settings.value("openai/api_key", "")

    def setOpenAIModel(self, model):
        self.settings.setValue("openai/model", model)

    def getOpenAIModel(self):
        return self.settings.value("openai/model", "gpt-4o-mini")

    def getConnectionUrl(self):
        if (
            not self.settings.value("database/host", "")
            or not self.settings.value("database/user", "")
            or not self.settings.value("database/password", "")
            or not self.settings.value("database/port", "")
            or not self.settings.value("database/name", "")
        ):
            return None
        return (
            "postgresql://"
            + self.settings.value("database/user", "")
            + ":"
            + self.settings.value("database/password", "")
            + "@"
            + self.settings.value("database/host", "")
            + ":"
            + self.settings.value("database/port", "")
            + "/"
            + self.settings.value("database/name", "")
        )
