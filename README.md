# SkyTemple Backup Plugin
A plugin that adds automatic backups and an auto-save feature to SkyTemple.

## How to use
Load a ROM in SkyTemple, click the button on the top right of the window, then click "Backup settings...".
This will open a menu with the following options:
- **Auto-save interval**: The interval at which the ROM will be automatically saved in minutes. Set to 0 to disable.
Auto-saves work like regular saves and will overwrite your current ROM. Enable "Backup on Save" to automatically create a backup of your ROM before it is overwritten.
- **Backup on Save**: If enabled, a backup of the ROM will be created before it is overwritten by a manual or auto-save.
- **Number of Backups to Keep**: The number of backups to keep. If the number of backups exceeds this number, the oldest backup will be deleted. Note that each backup takes about 100MB of disk space (or more if you have many custom assets).

Click the "Open Backup Folder" button to open the folder where backups are stored.

## Installation
1. Download the latest release from the [releases page](https://github.com/tech-ticks/skytemple-plugin-backups/releases)
2. Refer to this [Wiki page](https://wiki.skytemple.org/index.php/Plugin) for installation instructions.