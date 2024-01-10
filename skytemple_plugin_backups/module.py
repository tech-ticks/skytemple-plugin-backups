from __future__ import annotations

import logging
import os
import shutil
from datetime import datetime

from skytemple.core.abstract_module import AbstractModule
from skytemple.core.item_tree import ItemTree
from skytemple.core.rom_project import RomProject
from skytemple.core.ui_utils import builder_get_assert
from skytemple.controller.main import MainController

from skytemple_plugin_backups.widget.dialog import BackupSettingsDialog
from skytemple_plugin_backups.widget.settings_manager import SettingsManager

from gi.repository import Gtk, GLib

logger = logging.getLogger(__name__)

class BackupPluginModule(AbstractModule):
    """
    This is the entry-point of your plugin.
    """

    settings_item_registered: bool = False
    instance: BackupPluginModule = None
    timer_id: int = None
    main_controller_save_original = None
    
    rom_project: RomProject
    settings_manager: SettingsManager

    @classmethod
    def load(cls):
        """
        This is called when SkyTemple starts up. It is your chance to do any one-time
        initialization that your plugin needs to do.
        """
        # Monkey-patch the save function to create a backup before saving
        cls.main_controller_save_original = MainController._save
        def save_hook(main_controller: MainController, force=False, after_save_action=None):
            if cls.instance and cls.instance.settings_manager.backup_on_save:
                cls.instance.create_rom_backup()
            cls.main_controller_save_original(main_controller, force, after_save_action)

        MainController._save = save_hook

    def __init__(self, rom_project: RomProject):
        """
        Your plugin gets passed in the RomProject when it is created.
        This is your primary way to interact with the game and other modules.

        Note that `__init__` is called to create an instance of your module whenever a ROM
        is loaded. If you want to perform one-time initialization when SkyTemple starts
        use the classmethod load.
        """
        self.rom_project = rom_project
        self.settings_manager = SettingsManager()
        BackupPluginModule.instance = self

        if not BackupPluginModule.settings_item_registered:
            self.register_settings_item()
            BackupPluginModule.settings_item_registered = True

        BackupPluginModule.start_periodic_save_timer()

    def backup_folder(self):
        """
        Returns the folder where backups will be stored.
        """

        # Construct the backup folder name (e.g. "MyRom.nds.backup")
        basename, extension = os.path.splitext(os.path.basename(self.rom_project.filename))
        backup_folder = os.path.join(os.path.dirname(self.rom_project.filename), f"{basename}{extension}.backup")

        return backup_folder
    
    def backup_filename(self):
        """
        Returns the filename of the backup that will be created.
        """

        # Construct the backup filename (e.g. "MyRom_20210901_123456.nds")
        basename, extension = os.path.splitext(os.path.basename(self.rom_project.filename))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = self.backup_folder()
        backup_filename = os.path.join(backup_folder, f"{basename}_{timestamp}{extension}")

        return backup_filename

    def create_rom_backup(self):
        rom_filename = self.rom_project.filename
        backup_folder = self.backup_folder()
        backup_filename = self.backup_filename()

        try:
            os.makedirs(backup_folder, exist_ok=True)
            shutil.copy(rom_filename, backup_filename)
            logger.info(f"Backup created: {backup_filename}")

            # Manage the number of backups
            self.manage_backups(backup_folder)
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
        pass

    def manage_backups(self, backup_folder):
        num_backups = self.settings_manager.num_backups

        backups = [os.path.join(backup_folder, f) for f in os.listdir(backup_folder) if os.path.isfile(os.path.join(backup_folder, f))]
        
        # Sort the files by modification time (oldest first)
        backups.sort(key=lambda x: os.path.getmtime(x))

        # If there are more backups than num_backups, remove the oldest ones
        while len(backups) > num_backups:
            backup = backups.pop(0)
            os.remove(backup)
            logger.info(f"Deleted old backup: {backup}")

    @classmethod
    def register_settings_item(cls):
        builder = MainController._instance.builder

        about: Gtk.PopoverMenu = builder_get_assert(
            builder, Gtk.PopoverMenu, "settings_menu"
        )
        box: Gtk.Box = about.get_children()[0]

        # HACK: I just can't figure out how to get the button to not be centered...
        button = Gtk.ModelButton(label="Backup settings...                      ")
        button.centered = False
        button.connect("clicked", cls.on_open_popup_button_clicked)
        box.pack_end(button, True, True, 0)
        box.show_all()

    @classmethod
    def on_open_popup_button_clicked(cls, button: Gtk.ModelButton):
        if cls.instance:
            modal = BackupSettingsDialog(MainController._instance.window(), cls.instance.settings_manager, cls.instance.backup_folder())
            modal.run_dialog()
            cls.start_periodic_save_timer()

    @classmethod
    def start_periodic_save_timer(cls):    
        logger.info(f"Starting periodic backup timer. Auto-save interval: {cls.instance.settings_manager.auto_save_interval}")
        if cls.timer_id:
            GLib.source_remove(cls.timer_id)
            cls.timer_id = None

        if cls.instance.settings_manager.auto_save_interval > 0:
            interval_seconds = cls.instance.settings_manager.auto_save_interval * 60
            cls.timer_id = GLib.timeout_add_seconds(interval_seconds, cls.do_periodic_save)

    @classmethod
    def do_periodic_save(cls):
        project = RomProject.get_current()
        if project is None or not project.has_modifications():
            logger.info("Skipping periodic save because there are no modifications")
            return True

        logger.info("Periodic save")
        MainController.save()

        return True

    @classmethod
    def depends_on(cls) -> list[str]:
        """
        This returns a list of modules that your plugin needs. This can be another plugin module
        or one of the built-in modules, which are listed in SkyTemple's setup.py
        (or in the future it's pyproject.toml).

        You can reference these other modules and rely on functionality in them.
        """
        return ["rom"]
    
    def load_tree_items(self, item_tree: ItemTree):
        pass

    def sort_order(self) -> int:
        return 0
