import json
import os
import logging

from skytemple_files.common.project_file_manager import ProjectFileManager

logger = logging.getLogger(__name__)

class SettingsManager:
    def __init__(self):
        config_dir = ProjectFileManager.shared_config_dir()
        self.settings_file = os.path.join(config_dir, "backup_settings.json")
        self.settings = self.load_settings()

    def load_settings(self):
        try:
            with open(self.settings_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return default settings if the file does not exist or is invalid
            return {"backup_on_save": False, "auto_save_interval": 0, "num_backups": 5}

    def save_settings(self):
        logger.info("Saving settings")
        with open(self.settings_file, "w") as file:
            json.dump(self.settings, file)

    @property
    def backup_on_save(self):
        return self.settings.get("backup_on_save", False)

    @backup_on_save.setter
    def backup_on_save(self, value):
        self.settings["backup_on_save"] = value

    @property
    def auto_save_interval(self):
        return self.settings.get("auto_save_interval", 0)

    @auto_save_interval.setter
    def auto_save_interval(self, value):
        self.settings["auto_save_interval"] = value

    @property
    def num_backups(self):
        return self.settings.get("num_backups", 10)

    @num_backups.setter
    def num_backups(self, value):
        self.settings["num_backups"] = value

