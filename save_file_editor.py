import logging
import os
import re
import shutil
import struct
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
import zlib

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SaveFileEditor:
    """Editor for Dysmantle .save files, allowing modification of PLAYER_STATE data."""
    def __init__(self, root):
        self.root = root
        self.root.title("Dysmantle Save File Editor")
        self.force_boolean_nodes = {"discovered_tower_areas"}
        self.backup_dir = "backups"
        os.makedirs(self.backup_dir, exist_ok=True)

        self.original_file_path = None
        self.original_binary_data = None
        self.original_decompressed_data = None
        self.original_compressed_data = None
        self.xml_root = None
        self.xml_start_index = None
        self.xml_end_index = None
        self.current_player_state_data = None
        self.player_state_widgets = {}

        self.all_materials = [
            "", "PLANTS", "SCRAP_FABRIC", "SCRAP_WOOD", "SCRAP_METAL", "PLASTICS",
            "STONE", "WOOD", "IRON", "SCRAP_ELECTRONICS", "CERAMICS", "FABRIC",
            "HIDE", "BRICKS", "RUBBER", "STEEL", "LUMBER", "ELECTRONICS",
            "MANA_BEAD", "TITANIUM", "MANA_CHUNK", "MANA_SHARD", "TOMB_ORB",
            "NIGHT_MANA", "CPU", "FUEL_CELL", "MUSHROOM_BROWN", "MUSHROOM_RED",
            "MUSHROOM_WHITE", "RICE", "BERRIES", "EGG", "CACTUS", "SPICES",
            "FISH_A", "FISH_B", "FISH_C", "FISH_E", "FISH_D", "MEAT", "BONE",
            "TOMATO", "CARROT", "CORN", "LETTUCE", "ONION", "POTATO", "WHEAT",
            "LOBSTER", "OCTOPUS", "BANANA", "TRUFFLE", "CLOUDBERRY", "TIGER_LILY",
            "AMBER_LILY", "FROST_LILY", "CHITIN", "GOLD_ORE", "GOLD_BAR",
            "BEAM_GUN_BATTERY"
        ]

        self.info_label = tk.Label(
            root,
            text="Dysmantle Save File Editor\nUpload your DYSMANTLE .save file to edit its data.\nBackups are saved in the 'backups' folder.",
            justify="center",
            wraplength=780,
            padx=10,
            pady=10
        )
        self.info_label.pack()

        self.upload_button = tk.Button(root, text="Import .save File", command=self.upload_file, padx=10, pady=5)
        self.upload_button.pack(pady=5)

        self.xml_text = scrolledtext.ScrolledText(root, width=90, height=25, font=("Courier", 10), wrap=tk.WORD)
        self.xml_text.pack_forget()

        self.action_frame = tk.Frame(root)
        self.cancel_button = tk.Button(self.action_frame, text="Cancel", command=self.cancel_edit, padx=10, pady=5)
        self.save_button = tk.Button(self.action_frame, text="Save Changes", command=self.save_changes, state="disabled", padx=10, pady=5)
        self.cancel_button.pack(side="left", padx=5)
        self.save_button.pack(side="right", padx=5)
        self.action_frame.pack_forget()

        self.player_state_frame = None

    def upload_file(self):
        """Load and parse a DYSMANTLE .save file, displaying its PLAYER_STATE data."""
        file_path = filedialog.askopenfilename(title="Select DYSMANTLE .save File", filetypes=[("Save Files", "*.save")])
        if not file_path:
            logger.info("No file selected")
            return

        self.original_file_path = file_path
        logger.info(f"Selected file: {file_path}")

        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            if len(raw_data) < 12:
                messagebox.showerror("Error", "File is too short for a valid .save file.")
                return

            header = raw_data[:12]
            compressed_data = raw_data[12:]
            decompressed_data = zlib.decompress(compressed_data)

            match = re.search(b"<\?xml[^>]*>.*?</root>", decompressed_data, re.DOTALL)
            if not match:
                logger.error("Could not find valid XML in decompressed data.")
                messagebox.showerror("Error", "No valid XML found in save file.")
                return

            xml_bytes = match.group(0)
            end_match = re.search(b"</root>", xml_bytes)
            if not end_match:
                logger.error("Could not find </root> in XML block.")
                messagebox.showerror("Error", "Invalid XML structure in save file.")
                return

            xml_bytes = xml_bytes[:end_match.end()]
            self.xml_start_index = match.start()
            self.xml_end_index = self.xml_start_index + len(xml_bytes)

            try:
                self.xml_root = ET.fromstring(xml_bytes)
                logger.debug(f"XML parsed successfully, length: {len(xml_bytes)}, parsed length: {len(ET.tostring(self.xml_root, encoding='iso-8859-1'))}")
            except ET.ParseError as e:
                logger.error(f"XML parsing failed: {e}")
                messagebox.showerror("Error", f"Invalid XML in save file: {e}")
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"{os.path.basename(file_path)}_{timestamp}.save")
            shutil.copyfile(file_path, backup_path)
            logger.info(f"Saved backup to {backup_path}")

            self.original_binary_data = raw_data
            self.original_decompressed_data = decompressed_data
            self.original_compressed_data = compressed_data

            player_state = next((arr for arr in self.xml_root.findall('array') if arr.attrib.get('id') == 'PLAYER_STATE'), None)
            if player_state is None:
                messagebox.showerror("Error", "PLAYER_STATE array not found in save file XML.")
                return

            self.current_player_state_data = player_state
            self.show_player_state_editor(player_state)

            self.upload_button.pack_forget()
            self.action_frame.pack(pady=10, anchor="e")
            self.save_button.config(state="normal")
            messagebox.showinfo("Success", f"Data loaded for editing. Backup saved to {backup_path}.")
        except Exception as e:
            logger.error(f"Error processing file: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to process save file: {e}")

    def show_player_state_editor(self, player_state_node):
        """Display an editor for PLAYER_STATE node attributes."""
        self.xml_text.pack_forget()
        if self.player_state_frame:
            self.player_state_frame.destroy()

        self.player_state_frame = tk.Frame(self.root)
        self.player_state_frame.pack(padx=10, pady=10, fill="both", expand=True)

        canvas = tk.Canvas(self.player_state_frame, width=700, height=600)
        scrollbar = tk.Scrollbar(self.player_state_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        scrollable_frame = tk.Frame(canvas, bd=2, relief="ridge")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def resize_scrollable_frame(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", resize_scrollable_frame)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.player_state_widgets.clear()
        skip_ids = {
            "active_stage", "last_death_position", "last_death_position_in_open_world",
            "last_death_time_in_seconds_since_day1", "last_death_materials", "last_death_stage_id",
            "last_location", "materials", "current_tower_area_id", "material_storage_alltime",
            "tracked_recipes", "fast_travel", "states", "travel"
        }

        def is_leave_position_node(n):
            node_id = n.attrib.get("id", "")
            return node_id.startswith("stages/") and "leave_position" in n.attrib

        inventory_slots = []
        tk.Frame(scrollable_frame, height=2).pack(fill="x")

        for node in player_state_node.findall('node'):
            node_id = node.attrib.get('id', '')
            if not node_id or is_leave_position_node(node) or node_id in skip_ids or len(node.attrib) == 1:
                continue
            if node_id.startswith("slot_"):
                inventory_slots.append(node)
                continue
            if node_id == "respawn":
                self._render_respawn_node(scrollable_frame, node)
            elif node_id == "statistics":
                self._render_generic_node(scrollable_frame, node, vertical_layout=False)
            elif node_id == "discovered_tower_areas":
                self._render_generic_node(scrollable_frame, node, vertical_layout=True)
            elif node_id == "material_storage":
                self._render_material_storage_node(scrollable_frame, node)
            else:
                self._render_generic_node(scrollable_frame, node)

        if inventory_slots:
            self._render_inventory_slots(scrollable_frame, inventory_slots)

    def _render_material_storage_node(self, parent, node):
        """Render the material_storage node with quantity entries, remove buttons, and an add material section."""
        node_id = node.attrib.get('id', 'material_storage')
        frame = tk.LabelFrame(parent, text=node_id, padx=10, pady=5)
        frame.pack(fill="x", padx=5, pady=5)

        # Container for material entries
        entries_container = tk.Frame(frame)
        entries_container.pack(fill="x", anchor="w")

        # Track material entries and their widgets
        material_entries = []

        # Validation for quantity inputs
        def validate_numeric_input(action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
            if value_if_allowed == "":
                return True
            try:
                int(value_if_allowed)  # Quantities are integers
                return True
            except ValueError:
                return False

        vcmd = (self.root.register(validate_numeric_input), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # Render existing materials
        for attr_name, attr_value in node.attrib.items():
            if attr_name == "id" or attr_name not in self.all_materials:
                continue

            def create_remove_handler(attr, entry_frame):
                def remove_material():
                    # Remove from player_state_widgets
                    self.player_state_widgets.pop((node_id, attr), None)
                    # Remove from node attributes
                    if attr in node.attrib:
                        del node.attrib[attr]
                    # Destroy the entry frame
                    entry_frame.destroy()
                    # Update add material dropdown
                    update_add_dropdown()
                return remove_material

            entry_frame = tk.Frame(entries_container)
            entry_frame.pack(fill="x", pady=2)
            tk.Label(entry_frame, text=attr_name, width=20).pack(side="left")
            quantity_var = tk.StringVar(value=attr_value)
            tk.Entry(entry_frame, textvariable=quantity_var, width=8, validate="key", validatecommand=vcmd).pack(side="left", padx=5)
            tk.Button(entry_frame, text="Remove", command=create_remove_handler(attr_name, entry_frame)).pack(side="left", padx=5)
            self.player_state_widgets[(node_id, attr_name)] = quantity_var
            material_entries.append(entry_frame)

        # Add material section
        add_frame = tk.Frame(frame)
        add_frame.pack(fill="x", pady=5)
        tk.Label(add_frame, text="Add Material:").pack(side="left")

        def update_add_dropdown():
            current_materials = {attr for attr in node.attrib if attr in self.all_materials and attr != ""}
            available_materials = [m for m in self.all_materials if m not in current_materials and m != ""]
            material_var.set(available_materials[0] if available_materials else "")
            menu = add_dropdown["menu"]
            menu.delete(0, "end")
            for material in available_materials:
                menu.add_command(label=material, command=lambda m=material: material_var.set(m))

        material_var = tk.StringVar(value="")
        add_dropdown = tk.OptionMenu(add_frame, material_var, *self.all_materials[1:])  # Exclude empty string
        add_dropdown.config(width=20)
        add_dropdown.pack(side="left", padx=5)

        def add_material():
            material = material_var.get()
            if material and material not in node.attrib:
                node.attrib[material] = "0"  # Default quantity
                entry_frame = tk.Frame(entries_container)
                entry_frame.pack(fill="x", pady=2)
                tk.Label(entry_frame, text=material, width=20).pack(side="left")
                quantity_var = tk.StringVar(value="0")
                tk.Entry(entry_frame, textvariable=quantity_var, width=8, validate="key", validatecommand=vcmd).pack(side="left", padx=5)
                tk.Button(entry_frame, text="Remove", command=create_remove_handler(material, entry_frame)).pack(side="left", padx=5)
                self.player_state_widgets[(node_id, material)] = quantity_var
                material_entries.append(entry_frame)
                update_add_dropdown()

        tk.Button(add_frame, text="Add", command=add_material).pack(side="left", padx=5)
        update_add_dropdown()

    def _render_generic_node(self, parent, node, vertical_layout=False):
        """Render a generic node with attributes as entries or checkboxes."""
        frame = tk.LabelFrame(parent, text=node.attrib.get("id", "Node"))
        frame.pack(fill="x", padx=5, pady=5, anchor="w")
        node_id = node.attrib.get("id", "")

        def is_boolean_attr(attr_name):
            bool_keywords = ["enabled", "active", "is_", "has_", "allow_", "use_"]
            return any(k in attr_name.lower() for k in bool_keywords)

        def validate_numeric_input(action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
            if value_if_allowed == "":
                return True
            try:
                if '.' in value_if_allowed:
                    float(value_if_allowed)
                else:
                    int(value_if_allowed)
                if ',' in value_if_allowed:
                    return False
                return True
            except ValueError:
                return False

        vcmd = (self.root.register(validate_numeric_input), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        if vertical_layout:
            attr_container = tk.Frame(frame)
            attr_container.pack(fill="x", anchor="w")
            widgets = []

            for attr_name, attr_value in node.attrib.items():
                if attr_name == "id":
                    continue
                is_bool = node_id in self.force_boolean_nodes and attr_value in ("0", "1")
                if not is_bool:
                    try:
                        val_int = int(attr_value)
                        if is_boolean_attr(attr_name) and val_int in (0, 1):
                            is_bool = True
                    except ValueError:
                        pass

                attr_frame = tk.Frame(attr_container)
                tk.Label(attr_frame, text=attr_name).pack(side="left")
                if is_bool:
                    var = tk.IntVar(value=int(attr_value))
                    tk.Checkbutton(attr_frame, variable=var).pack(side="left", padx=2)
                    self.player_state_widgets[(node_id, attr_name)] = var
                else:
                    var = tk.StringVar(value=attr_value)
                    tk.Entry(attr_frame, textvariable=var, width=8, validate="key", validatecommand=vcmd).pack(side="left", padx=2)
                    self.player_state_widgets[(node_id, attr_name)] = var
                widgets.append(attr_frame)

            def do_layout(event=None):
                for w in widgets:
                    w.grid_forget()
                width = attr_container.winfo_width()
                columns = max(1, width // 150)
                for i, w in enumerate(widgets):
                    w.grid(row=i // columns, column=i % columns, sticky="w", padx=5, pady=2)
            attr_container.bind("<Configure>", do_layout)
            attr_container.after(10, do_layout)
        else:
            for attr_name, attr_value in node.attrib.items():
                if attr_name == "id":
                    continue
                is_bool = node_id in self.force_boolean_nodes and attr_value in ("0", "1")
                if not is_bool:
                    try:
                        val_int = int(attr_value)
                        if is_boolean_attr(attr_name) and val_int in (0, 1):
                            is_bool = True
                    except ValueError:
                        pass

                attr_frame = tk.Frame(frame)
                attr_frame.pack(side="left", padx=5, pady=2)
                tk.Label(attr_frame, text=attr_name).pack(side="left")
                if is_bool:
                    var = tk.IntVar(value=int(attr_value))
                    tk.Checkbutton(attr_frame, variable=var).pack(side="left", padx=2)
                    self.player_state_widgets[(node_id, attr_name)] = var
                else:
                    var = tk.StringVar(value=attr_value)
                    tk.Entry(attr_frame, textvariable=var, width=8, validate="key", validatecommand=vcmd).pack(side="left", padx=2)
                    self.player_state_widgets[(node_id, attr_name)] = var

    def _render_respawn_node(self, parent, node):
        """Render the respawn node with location coordinates, stage, and enabled checkbox."""
        node_id = node.attrib.get('id', 'respawn')
        frame = tk.LabelFrame(parent, text=node_id, padx=10, pady=5)
        frame.pack(fill="x", padx=5, pady=5)

        location = node.attrib.get("location", "0,0,0")
        loc_parts = location.split(",")
        if len(loc_parts) != 3:
            loc_parts = ["0", "0", "0"]

        tk.Label(frame, text="Location (x, y, z)").pack(anchor="w")
        loc_vars = []
        for i, coord in enumerate(["X", "Y", "Z"]):
            subframe = tk.Frame(frame)
            subframe.pack(fill="x", pady=2)
            tk.Label(subframe, text=coord).pack(side="left", padx=(0, 5))
            var = tk.StringVar(value=loc_parts[i])
            tk.Entry(subframe, textvariable=var).pack(side="left", fill="x", expand=True)
            loc_vars.append(var)

        stage_values = ["stages/dlc1/index.xml", "stages/dlc2/index.xml", "stages/dlc3/index.xml", "stages/island/index.xml"]
        stage = node.attrib.get("stage", stage_values[0])
        tk.Label(frame, text="Stage").pack(anchor="w")
        stage_var = tk.StringVar(value=stage)
        tk.OptionMenu(frame, stage_var, *stage_values).pack(fill="x", pady=2)

        enabled_val = node.attrib.get("enabled", "0")
        enabled_var = tk.IntVar(value=int(enabled_val))
        tk.Checkbutton(frame, text="Enabled", variable=enabled_var).pack(anchor="w", pady=2)

        self.player_state_widgets[(node_id, "location_x")] = loc_vars[0]
        self.player_state_widgets[(node_id, "location_y")] = loc_vars[1]
        self.player_state_widgets[(node_id, "location_z")] = loc_vars[2]
        self.player_state_widgets[(node_id, "stage")] = stage_var
        self.player_state_widgets[(node_id, "enabled")] = enabled_var

    def _render_inventory_slots(self, parent, nodes):
        """Render inventory slots with amount and material dropdowns."""
        frame = tk.LabelFrame(parent, text="Inventory Slots", padx=10, pady=5)
        frame.pack(fill="x", padx=5, pady=5)

        for node in nodes:
            node_id = node.attrib.get('id', 'unknown')
            amount = node.attrib.get("amount", "0")
            material = node.attrib.get("material", "")

            slot_frame = tk.Frame(frame)
            slot_frame.pack(fill="x", pady=2)
            tk.Label(slot_frame, text=node_id).pack(side="left", padx=(0, 5))
            tk.Label(slot_frame, text="Amount").pack(side="left")
            amount_var = tk.StringVar(value=amount)
            tk.Entry(slot_frame, textvariable=amount_var, width=8).pack(side="left", padx=(0, 10))
            tk.Label(slot_frame, text="Material").pack(side="left")
            material_var = tk.StringVar(value=material if material in self.all_materials else self.all_materials[0])
            tk.OptionMenu(slot_frame, material_var, *self.all_materials).pack(side="left", padx=(0, 10))

            self.player_state_widgets[(node_id, "amount")] = amount_var
            self.player_state_widgets[(node_id, "material")] = material_var

    def cancel_edit(self):
        """Cancel editing and reset the UI to the initial state."""
        self.action_frame.pack_forget()
        if self.player_state_frame:
            self.player_state_frame.destroy()
        self.xml_text.pack_forget()
        self.upload_button.pack(pady=5)

    def save_changes(self):
        """Save changes to the PLAYER_STATE data back to a .save file."""
        if not self.original_file_path or not self.original_binary_data:
            messagebox.showerror("Error", "No file loaded to save.")
            return
        if not self.current_player_state_data:
            messagebox.showerror("Error", "No PLAYER_STATE loaded for saving.")
            return

        try:
            # Update XML attributes from UI widgets
            for node in self.xml_root.findall('.//node'):
                for node in self.xml_root.findall('.//node'):
                    node_id = node.attrib.get('id')
                    if not node_id:
                        continue
                    keys_for_node = [key for key in self.player_state_widgets if key[0] == node_id]
                    loc_x_var = self.player_state_widgets.get((node_id, "location_x"))
                    loc_y_var = self.player_state_widgets.get((node_id, "location_y"))
                    loc_z_var = self.player_state_widgets.get((node_id, "location_z"))
                    if loc_x_var and loc_y_var and loc_z_var:
                        node.attrib["location"] = ",".join([loc_x_var.get(), loc_y_var.get(), loc_z_var.get()])
                    for key in keys_for_node:
                        attr = key[1]
                        if attr in ("location_x", "location_y", "location_z"):
                            continue
                        widget_var = self.player_state_widgets[key]
                        new_val = widget_var.get()
                        if attr == "material":
                            amount_var = self.player_state_widgets.get((node_id, "amount"))
                            amount_val = amount_var.get() if amount_var else "0"
                            if amount_val == "0" or amount_val == "" or int(amount_val) == 0:
                                if "material" in node.attrib:
                                    del node.attrib["material"]
                                continue
                        node.attrib[attr] = str(new_val)

            # Serialize updated XML
            new_xml_bytes = ET.tostring(self.xml_root, encoding='iso-8859-1')
            original_xml_length = self.xml_end_index - self.xml_start_index
            if len(new_xml_bytes) < original_xml_length:
                new_xml_bytes += b' ' * (original_xml_length - len(new_xml_bytes))

            # Rebuild decompressed data
            new_decompressed_data = (
                self.original_decompressed_data[:self.xml_start_index] +
                new_xml_bytes +
                self.original_decompressed_data[self.xml_end_index:]
            )

            # Verify decompressed data length
            if len(new_decompressed_data) != len(self.original_decompressed_data):
                logger.error(f"Decompressed data length mismatch: original={len(self.original_decompressed_data)}, new={len(new_decompressed_data)}")
                messagebox.showerror("Error", "Decompressed data length mismatch. Save aborted.")
                return

            # Compress data and update header
            new_compressed_data = zlib.compress(new_decompressed_data, level=9)
            header = bytearray(self.original_binary_data[:12])
            header[8:12] = struct.pack('<I', len(new_compressed_data))
            new_save_data = bytes(header) + new_compressed_data

            # Save file
            result = messagebox.askyesnocancel(
                "Save File",
                "Save changes?\n\nYes: overwrite original file\nNo: save as new _edited.save file\nCancel: abort"
            )
            if result is None:
                logger.info("Save cancelled by user.")
                return
            save_path = self.original_file_path if result else os.path.splitext(self.original_file_path)[0] + "_edited.save"

            with open(save_path, 'wb') as f:
                f.write(new_save_data)
            logger.info(f"File saved successfully to {save_path}")
            messagebox.showinfo("Success", f"File saved successfully:\n{save_path}")
        except Exception as e:
            logger.error(f"Error saving changes: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to save file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SaveFileEditor(root)
    root.mainloop()