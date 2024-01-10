from __future__ import annotations

import logging
import os
import subprocess
from typing import TYPE_CHECKING

from gi.repository import Gtk

from skytemple.core.ui_utils import open_dir
from skytemple_plugin_backups.widget.settings_manager import SettingsManager

logger = logging.getLogger(__name__)

class BackupSettingsDialog(Gtk.Dialog):
    def __init__(self, parent, settings_manager: SettingsManager, backups_dir: str):
        super().__init__("Backup Settings", parent, 0,
                         (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                          Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.backups_dir = backups_dir

        self.set_default_size(300, 200)
        self.set_modal(True)

        box = self.get_content_area()
        box.set_spacing(5)  # Adds some space between elements
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)

        # Auto-save interval
        auto_save_interval_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        auto_save_interval_label = Gtk.Label(label="Auto-save Interval (minutes, 0=disabled):", xalign=0)
        self.auto_save_interval_entry = Gtk.SpinButton()
        self.auto_save_interval_entry.set_range(0, 60)
        self.auto_save_interval_entry.set_increments(1, 10)  # Single steps or 10s steps
        auto_save_interval_box.pack_start(auto_save_interval_label, True, True, 0)
        auto_save_interval_box.pack_start(self.auto_save_interval_entry, False, True, 0)
        box.add(auto_save_interval_box)

        # Backup on save toggle
        backup_on_save_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        backup_on_save_label = Gtk.Label(label="Backup on Save:", xalign=0)
        self.backup_on_save_switch = Gtk.Switch()
        backup_on_save_box.pack_start(backup_on_save_label, True, True, 0)
        backup_on_save_box.pack_start(self.backup_on_save_switch, False, True, 0)
        box.add(backup_on_save_box)

        # Number of backups to keep
        num_backups_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        num_backups_label = Gtk.Label(label="Number of Backups to Keep:", xalign=0)
        self.num_backups_entry = Gtk.SpinButton()
        self.num_backups_entry.set_range(1, 100)  # Allows between 1 and 100 backups
        self.num_backups_entry.set_increments(1, 5)  # Single steps or 5s steps
        num_backups_box.pack_start(num_backups_label, True, True, 0)
        num_backups_box.pack_start(self.num_backups_entry, False, True, 0)
        box.add(num_backups_box)

        self.settings_manager = settings_manager

        # Set initial values based on settings
        self.backup_on_save_switch.set_active(self.settings_manager.backup_on_save)
        self.auto_save_interval_entry.set_value(self.settings_manager.auto_save_interval)
        self.num_backups_entry.set_value(self.settings_manager.num_backups)

        # Open Backup Folder Button
        open_backup_folder_button = Gtk.Button(label="Open Backup Folder")
        open_backup_folder_button.connect("clicked", self.on_open_backup_folder_clicked)
        box.pack_start(open_backup_folder_button, False, False, 0)

        self.show_all()

    def on_open_backup_folder_clicked(self, button: Gtk.Button):
        os.makedirs(self.backups_dir, exist_ok=True)
        open_dir(self.backups_dir)

    def run_dialog(self):
        response = self.run()
        if response == Gtk.ResponseType.OK:
            # Update settings
            self.settings_manager.backup_on_save = self.backup_on_save_switch.get_active()
            self.settings_manager.auto_save_interval = self.auto_save_interval_entry.get_value_as_int()
            self.settings_manager.num_backups = self.num_backups_entry.get_value_as_int()
            self.settings_manager.save_settings()

        self.destroy()