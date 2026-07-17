from PySide6.QtCore import QSettings

class AppSettings:
    def __init__(self):
        self.settings = QSettings("UtilFusion", "UtilFusionApp")

    def setUsername(self, username):
        self.settings.setValue("username", username)

    def getUsername(self):
        return self.settings.value("username", "")
    def getConnectionUrl(self):
        return "postgresql://" + self.settings.value("database/user", "") + ":" + self.settings.value("database/password", "") + "@" + self.settings.value("database/host", "") + ":" + self.settings.value("database/port", "") + "/" + self.settings.value("database/name", "")