# Dysmantle Save File Editor (WIP)

**Note**: This is a work-in-progress (WIP) project and is subject to change. Features, functionality, and compatibility may be updated or modified in future versions.

## Overview

The Dysmantle Save File Editor is a Python-based tool designed to edit `.save` files for the game *Dysmantle*. It allows you to modify player state data, such as inventory items and hotbar items, through a simple graphical interface. This project is WIP, and some features or compatibility with certain save files may change.

## Prerequisites

Before using the editor, ensure you have the following:

- **Python 3.8 or higher**: Install from [python.org](https://www.python.org/downloads/).
- **Required Libraries**: Install the necessary Python libraries by running:
  ```bash
  pip install tkinter
  ```
  *Note*: The `tkinter` library is typically included with Python, but ensure it’s available on your system. The editor also uses standard libraries (`zlib`, `os`, `shutil`, `logging`, `xml.etree.ElementTree`, `re`, `struct`), which require no additional installation.
- A valid *Dysmantle* `.save` file (usually found in the game’s save directory).
- **Backup your save files**: The editor creates backups automatically, but manually back up your `.save` files before editing.

## Installation

1. **Download the Editor**:
   - Clone or download the repository containing the `save_file_editor.py` script.
   - *Note*: The repository structure and download process may change as this is a WIP project.

2. **Verify Dependencies**:
   - Ensure Python is installed and run the `pip install` command above if needed.
   - No additional setup is required, as the editor uses standard Python libraries.

3. **Place the Script**:
   - Save `save_file_editor.py` in a directory of your choice.
   - *Note*: Future releases may include additional files or a packaged executable, as this is WIP.

## Usage

1. **Run the Program**:
   - Open a terminal or command prompt, navigate to the directory containing `save_file_editor.py`, and run:
     ```bash
     python save_file_editor.py
     ```
   - A graphical window will open with the Dysmantle Save File Editor interface.
   - *Note*: The interface and functionality are WIP and may change in future updates. I may release an standalone exe eventually.

2. **Import a Save File**:
   - Click the **Import .save File** button.
   - Select a `.save` file from your *Dysmantle* game directory (e.g., `profile.save`).
   - The editor will load the file and display editable player state data (e.g., inventory slots, respawn location).
   - A backup of the original file is automatically saved in the `backups` folder with a timestamp (e.g., `profile_20250629_153000.save`).
   - *Note*: Save file compatibility and parsing are WIP and may change. Always verify backups.

3. **Edit Player State**:
   - The editor displays fields for:
     - **Inventory Slots**: Modify the `amount` and `material` for each slot using dropdowns and text fields.
     - **Respawn Node**: Adjust `location` (x, y, z coordinates), `stage`, and `enabled` status.
     - **Other Nodes**: Edit attributes like `statistics` or `discovered_tower_areas` using text fields or checkboxes.
   - Enter numeric values for coordinates or amounts, and use dropdowns for materials.
   - *Note*: The editable fields and their behavior are WIP and may change based on game updates or editor enhancements eg. discovered_tower_areas now only allows toggleing already discovered areas, undiscovered areas will be added as well similar to how it currently works for material selection for hotbar items.

4. **Save Changes**:
   - Click **Save Changes** to save your edits.
   - Choose:
     - **Yes**: Overwrite the original file (backups are in backups folder).
     - **No**: Save as a new file with `_edited` appended (e.g., `profile_edited.save`).
     - **Cancel**: Discard changes.
   - The editor updates the file’s header to match the new compressed data length, ensuring compatibility.
   - *Note*: Save file structure handling is WIP and may require adjustments in future versions.

5. **Cancel Editing**:
   - Click **Cancel** to discard changes and return to the import screen.
   - *Note*: The cancel functionality is WIP and may be refined in future updates.

## Important Notes

- **Work-in-Progress**: This editor is in active development. Features, UI, and compatibility with *Dysmantle* save files are subject to change. Test with non-critical save files first.
- **Backup Your Files**: Although the editor creates backups, always keep manual backups of your `.save` files to avoid data loss.
- **Compression**: The editor uses zlib compression (level 9) and updates the file header to match the new compressed length. This works for most cases, but compatibility may vary as the project is WIP.
- **Game Compatibility**: The editor is designed for *Dysmantle* save files as of June 2025. Game updates may alter save file formats, requiring editor updates. Check for new releases if issues occur.
- **Error Handling**: If you encounter errors (e.g., "Invalid XML" or "Decompressed data length mismatch"), verify your `.save` file is valid and  with error details. Error handling is WIP and may improve.

## Troubleshooting

- **"No valid XML found" Error**: Ensure the `.save` file is a valid *Dysmantle* save file. Try a different file or check for game updates, as the editor is WIP.
- **Game Rejects Edited File**: Verify the backup file works in-game. If issues persist, the save file format may have changed. Revert to a backup and check for editor updates.
- **UI Issues**: If the interface is unresponsive or fields don’t display, ensure Python and `tkinter` are correctly installed. The UI is WIP and may be refined.
- **Contact**: For bugs or questions, make an issue provide as much info as possible.

## Contributing

This project is open to contributions. To contribute:
- Submit pull requests with bug fixes or features.

## License

This project is licensed under the MIT License.

**Disclaimer**: Use this editor at your own risk. The developer is not responsible for lost save data or game issues. Always back up your files.
