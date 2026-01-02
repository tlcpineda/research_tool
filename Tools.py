import csv
import json
import os
import sys
from datetime import datetime as dt
from datetime import timezone as tz
from os import path

import pytesseract
from PIL import Image, ImageGrab

from lib import display_message, display_path_desc, identify_path

# Class variables :
registry_name = "registry.json"  # JSON log of projects; list of objects
user_data = "user_data"  # Folder name containing the registry file
research_log = "research_log.json"  # JSON log of all research data.
tags = "tags.json"  # JSON log of tags used for each entry in research_log
img_folder = "assets"  # Folder name containing the images snipped
paths_csv = "paths.csv"  # The CSV file containing the path to tesseract.exe; initialised with possible locations.


class RegistryManager:
    def __init__(self):
        # Default running as a py script
        current_dir = path.abspath(path.dirname(__file__))

        # Redefine if run as executable file.
        if getattr(sys, "frozen", False):
            current_dir = path.dirname(path.abspath(sys.executable))

        # Move one level up if script is in 'dist' folder.
        self.app_parent = (
            path.dirname(current_dir)
            if path.basename(current_dir).lower() == "dist"
            else current_dir
        )

        # Set up user_data folder, in app_root.
        self.user_data_path = path.join(self.app_parent, user_data)

        if not path.exists(self.user_data_path):
            os.makedirs(self.user_data_path)

        self.paths_csv = path.join(self.user_data_path, paths_csv)
        self.registry_path = path.join(self.user_data_path, registry_name)

        self._check_paths_file()  # Ensure that CSV files containing possible locations of tesseract.exe exists.
        self.tesseract_path = self._config_tesseract_path()
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        self._clean_up_files_path()  # Wipe CSV file, and save only the correct path.
        self.projects = _load_log(self.registry_path)
        _save_to_log(self.registry_path, self.projects)

    def _config_tesseract_path(self):
        """Determine the path to the tesseract executable."""
        ocr_path = ""
        try:
            # Check if one of the paths listed is valid.
            with open(self.paths_csv, "r", encoding="utf-8") as file:
                reader = csv.reader(file)

                for row in reader:
                    if not row:
                        continue

                    ocr_path = path.normpath(path.expanduser(row[0]))

                    if path.exists(ocr_path):
                        display_message("INFO", f"OCR Engine linked : {ocr_path}")
                        return ocr_path

        except Exception as e:
            display_message("WARN", "OCR configuration error.", f"{e}")

        # Prompt user to install, and/or locate path to executable file.
        display_message("WARN", "Tesseract OCR engine not found.")
        display_message(
            "1",
            "Install engine based on OS - https://tesseract-ocr.github.io/tessdoc/Installation.html .",
        )
        display_message("2", "If already installed, locate the path to the executable.")
        display_message("", "Ex : C:/Program Files/Tesseract-OCR/tesseract.exe")

        user_input = False

        while not user_input:
            user_input = (
                input("\n>>> [L]ocate path / E[X]it and close window for now ?")
                .strip()
                .upper()
            )

            if user_input not in ["L", "X"]:
                user_input = False
            elif user_input == "X":
                sys.exit()
            elif user_input == "L":
                ocr_path = self._identify_ocr_path()

                if not ocr_path or ocr_path == ".":
                    user_input = False
                    display_message("WARN", "No file selected.")
                elif path.exists(ocr_path):
                    display_message("INFO", "Tesseract engine identified.")
                    display_path_desc(ocr_path, "file")
                else:
                    user_input = False
                    display_message("WARN", "Invalid path.")

        return ocr_path

    def _identify_ocr_path(self) -> str:
        print("\n>>> Locate Tesseract Executable File ...")
        path_input = identify_path("file", "exe")
        norm_path = path.normpath(path_input)

        display_path_desc(norm_path, "file")

        return norm_path

    def _clean_up_files_path(self):
        """Delete contents of paths.csv, and replace with the correctly identified / user-supplied path."""
        try:
            with open(self.paths_csv, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                tess_path = (
                    self.tesseract_path
                    if os.sep == "/"
                    else self.tesseract_path.replace(os.sep, "/")
                )
                writer.writerow([tess_path])

        except Exception as e:
            display_message("WARN", f"{paths_csv} cannot be updated.", f"{e}")

    def _check_paths_file(self):
        """Creates a default CSV file for paths to be used by Tesseract."""
        csv_file = self.paths_csv

        if not path.exists(csv_file):
            paths = [
                ["C:/Program Files/Tesseract-OCR/tesseract.exe"],
                ["~/AppData/Local/Tesseract-OCR/tesseract.exe"],
                ["/usr/homebrew/bin/tesseract"],
                ["/usr/local/bin/tesseract/"],
                ["/usr/bin/tesseract/"],
            ]  # Possible locations of tesseract.exe

            with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(paths)

    def add_project(self, name, project_path) -> bool:
        """
        Adds a new project to the registry.
        :param name: The name of the project; typically the name of the research project.
        :param project_path: The path to the project directory.
        :return: None
        """
        abs_path = path.abspath(project_path)

        # Check for duplicate paths.
        for proj in self.projects:
            if proj["path"] == abs_path:
                display_message("WARN", "Project already exists in registry.")
                return False

        self.projects.append(
            {
                "name": name,
                "path": abs_path if os.sep == "/" else abs_path.replace(os.sep, "/"),
            }
        )
        _save_to_log(self.registry_path, self.projects)

        display_message("INFO", f'Project "{name}" added to registry.')

        self.initialise_project(len(self.projects))
        display_message("INFO", f'Folder "{name}" initialised.')

        return True

    def initialise_project(self, project_number) -> bool:
        """ "
        Check if the project exists in the registry, then initialise project files.
        :param project_number: The project number corresponding to the project name.
        :return:
        """
        if not (1 <= project_number <= len(self.projects)):
            display_message("WARN", "Project number out of range.")
            return False

        project_path = self.projects[project_number - 1]["path"]

        if not path.exists(project_path):
            display_message("WARN", "Project path not found.")
            return False

        try:
            # Create 'assets' subfolder.
            asset_path = path.join(project_path, "assets")
            if not path.exists(asset_path):
                os.makedirs(asset_path)

            log_files = [research_log, tags]
            for name in log_files:
                file_path = path.join(project_path, name)

                if not path.exists(file_path):
                    with open(file_path, "w") as file:
                        json.dump([], file, indent=2)

            return True

        except Exception as e:
            display_message("WARN", "Error initialising project.", f"{e}")

            return False


class TagManager:
    def __init__(self, project_path) -> None:
        self.tags_path = path.normpath(path.join(project_path, tags))
        self.tags_list = _load_log(self.tags_path)

    def list_tags(self):
        """List tags currently used in the project."""
        if not self.tags_list:
            display_message("INFO", "No tags currently defined.")
            return

        # Determine number of rows for layout; with the number of columns limited to 4
        num_tags = len(self.tags_list)
        num_cols = 4
        col_width = 25
        text_limit = 20
        rows = (num_tags + num_cols - 1) // num_cols

        print("\n<=> Available tags :")

        for r in range(rows):
            line = ""

            for c in range(num_cols):
                index = r + (c * rows)

                if index < num_tags:
                    tag_name = self.tags_list[index]
                    tag_id = index + 1
                    display_text = f"[{tag_id}] {tag_name}"

                    if len(display_text) > text_limit:
                        display_text = display_text[:text_limit] + "..."

                    line += f"{display_text:<{col_width}}"

            if line.strip():
                print(line)

    def resolve_tags(self, user_input):
        """
        Maps numeric input to existing tags or adds new string tags.
        Numeric tags, for year, or statute numbers, are enclosed by angle brackets. eg "<1924>", "<1081>"
        Multi-word tags are truncated at the first space, and stripped of punctuations.
        """
        raw_items = [item.strip() for item in user_input.split(",") if item.strip()]
        final_tags = []
        updated = False

        for item in raw_items:
            # Handle tag IDs (no cleaning).
            if item.isdigit():
                idx = int(item) - 1

                if 0 <= idx < len(self.tags_list):
                    tag_name = self.tags_list[idx]

                    if tag_name not in final_tags:
                        final_tags.append(tag_name)

                    continue

                else:
                    display_message("WARN", f"Tag number ({item}) out of range.")

                    continue

            def clean_item(c):
                return "".join(char for char in c if char.isalnum())

            # Check for brackets.
            if "<" in item and ">" in item:
                # Extract content between brackets.
                content = item[item.find("<") + 1 : item.find(">")]

                # Clean up apparent multi-word entry, with extraneous punctuations.
                # Strip off punctuations, and get the first partition that is purely numeric.
                split_list = [n for n in clean_item(content).split() if n.isdigit()]

                if len(split_list) > 0:
                    tag_name = f"<{split_list[0]}>"
                else:
                    tag_name = "<000>"
                    display_message(
                        "WARN", f"No digits found in {item}.  Retagged as <000>"
                    )

            else:
                # Take first word of the raw string, and strip punctuations.
                clean_word = clean_item(item.split()[0])

                if not clean_word:
                    continue
                tag_name = clean_word.upper()

            # Finalise master list and selection.
            if tag_name not in self.tags_list:
                self.tags_list.append(tag_name)
                updated = True

            if tag_name not in final_tags:
                final_tags.append(tag_name)

        if updated:
            _save_to_log(self.tags_path, self.tags_list)

        return final_tags


class TextEntry:
    def __init__(self, project_path, tags_manager):
        """Initialise with the path to the active project."""
        self.project_path = project_path
        self.log_path = path.join(project_path, research_log)
        self.tags_manager = tags_manager
        self.log = _load_log(self.log_path)

    def _extract_text(self, img, lang="eng") -> str:
        """
        Extract contents from the snipped image.
        FUTURE formatting detection; boldface, italics, variable font face
        """
        try:
            text = pytesseract.image_to_string(
                img, lang=lang, config=r"--oem 3 --psm 3"
            )
            return text.strip()
        except Exception as e:
            display_message("WARN", "OCR text extraction failed.", f"{e}")
            return ""

    def capture_entry(self):
        """The main workflow for capturing a text entry"""
        print("\n>>> Create new text entry ...")

        # Prompt user for entry metadata.
        metadata = _capture_meta(self.tags_manager)
        text_detected = False
        content = None
        while not text_detected:
            img = _capture_img("text")  # Take a screen snip, and capture the content.

            if not img:
                return False  # Either user cancelled, no image in clipboard

            content = self._extract_text(img)

            if not content:
                display_message("WARN", "No text detected.")

                retry_snip = None
                while retry_snip not in ["R", "C"]:
                    print("\n>>> Select an option to continue :")
                    print(">>>  [R]etry taking a screenshot.")
                    print(">>>  [C]ancel text entry.")

                    retry_snip = input("\n>>> ").strip().upper()

                    if retry_snip == "R":
                        display_message("INFO", "Retry snipping.")
                    elif retry_snip == "C":
                        display_message("WARN", "Text entry cancelled.")
                        return False
                    else:
                        display_message("WARN", 'Enter one of the options ["R", "C"].')

            display_message("INFO", "Text entry captured.")
            print(f"<=> CONTENT :\n{content}")

            save_entry = None
            while save_entry not in ["S", "E"]:
                save_entry = (
                    input("\n>>> [S]ave entry to file, or [E]dit text entry ...")
                    .strip()
                    .upper()
                )
                if save_entry == "E":
                    content = self._edit_text()
                    text_detected = True
                elif save_entry == "S":
                    text_detected = True
                else:
                    display_message("WARN", 'Enter one of the options ["S", "E"].')

        self.log.append(_compile_entry("text", content, metadata))
        return _save_to_log(self.log_path, self.log)

    # FUTURE method to allow user edit a prefilled environment with the detected text; using notepad or similar
    def _edit_text(self):
        print("\n>>> Enter revised text entry ...")
        content = input(">>> ").strip()

        return content


def _capture_img(entry_type: str) -> Image.Image | None:
    """Prompt user to take a screenshot.  Image in clipboard will be processed."""
    print("\n<=> Use preferred snipping tool to copy image to clipboard.")

    extract_img = False
    while not extract_img:
        print("\n>>> Select an option to proceed :")
        print(f">>>  [E]xtract {entry_type} from image in clipboard.")
        print(f">>>  [C]ancel {entry_type} entry.")

        user_input = input(">>> ").strip().upper()
        if user_input == "E":
            extract_img = True
        if user_input == "C":
            display_message(
                "WARN",
                f"{entry_type.title()} entry cancelled.",
            )
            return None

    try:
        img = ImageGrab.grabclipboard()  # Pull the image from the system clipboard.

        if isinstance(img, Image.Image):
            display_message("INFO", "Image retrieved from clipboard.")
            return img
        elif img is None:
            display_message("WARN", "Clipboard is empty.")
        elif isinstance(img, list):  # Case when files are copied
            display_message("WARN", "Clipboard contains files.")
        else:
            display_message("WARN", "Clipboard content is not a valid format.")

        return None

    except Exception as e:
        display_message("WARN", "Error accessing clipboard.", f"{e}")
        return None


def _capture_meta(tags_manager):
    """Capture metadata."""
    title = input("\n>>> Entry Title : ").strip() or "untitled_entry"
    source = input("\n>>> Source (URL/Book) : ").strip() or "unidentified_source"
    notes = input("\n>>> Notes : ").strip()

    # Affix tags.
    if tags_manager:
        tags_manager.list_tags()

    print(">>> Limit new tags to single word entries.")
    print(">>> Enclose numeric tags in brackes <>; eg. <1812>")

    tag_input = input(">>> Enter tags (comma separated) : ")
    entry_tags = tags_manager.resolve_tags(tag_input)

    return title, source, notes, entry_tags


def _compile_entry(entry_type, content, metadata):
    title, source, notes, entry_tags = metadata
    entry = {
        "type": entry_type,
        "date": f"{dt.now(tz.utc).isoformat()}",
        "title": title,
        "content": content,
        "source": source,
        "tags": entry_tags,
        "notes": notes,
    }

    return entry


def _load_log(file_path):
    """Load contents of log file, or returns an empty list if not found."""
    if path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                return json.load(file)
            except json.decoder.JSONDecodeError:
                return []

    return []


def _save_to_log(log_path, data):
    """Helper function to save data to specified log file."""

    # Create a temp file as back up during saving process.
    temp_path = log_path + ".tmp"

    try:
        with open(temp_path, "w", encoding="utf-8") as log_file:
            json.dump(data, log_file, indent=2, ensure_ascii=False)

        # Replace the official file, but the temp file.
        os.replace(temp_path, log_path)
        display_message("INFO", "New entry added to log")
        return True
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)

        display_message("WARN", f"File save failed :\n{log_path}", f"{e}")
        return False
