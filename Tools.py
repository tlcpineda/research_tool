import csv
import datetime
import json
import os
import pytesseract
import sys
from os import path
from PIL import ImageGrab, Image
from lib import display_message, identify_path, display_path_desc

# Class variables :
registry_name = 'registry.json'  # JSON log of projects; list of objects
user_data = 'user_data' # Folder name containing the registry file
research_log = 'research_log.json'  # JSON log of all research data.
tags = 'tags.json'  # JSON log of tags used for each entry in research_log
img_folder = 'assets'   # Folder name containing the images snipped
paths_csv = 'paths.csv'

class RegistryManager:
    def __init__(self):
        current_dir = path.abspath(path.dirname(__file__))  # Default running as a py script

        # Redefine if run as executable file.
        if getattr(sys, 'frozen', False):
            current_dir = path.dirname(path.abspath(sys.executable))

        # Move one level up if script is in 'dist' folder.
        self.app_parent = path.dirname(current_dir) if path.basename(current_dir).lower() == 'dist' else current_dir

        # Set up user_data folder, in app_root.
        self.user_data_path = path.join(self.app_parent, user_data)

        if not path.exists(self.user_data_path):
            os.makedirs(self.user_data_path)

        self.paths_csv = path.join(self.user_data_path, paths_csv)  # Define path to paths.csv file.
        self.registry_path = path.join(self.user_data_path, registry_name)  # Create registry.json file

        self._check_paths_file() # Ensure that CSV files containing possible locations of tesseract.exe exists.
        self.tesseract_path = self._config_tesseract_path() # Identify path to tesseract.exe, or ask user to install it.
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        self._clean_up_files_path() # Wipe CSV file, and save only the correct path.
        self.projects = self._load_registry()
        self._save_registry()


    def _config_tesseract_path(self):
        """Determine the path to the tesseract executable."""
        ocr_path = None
        try:
            # Check if one of the paths listed is valid.
            with open(self.paths_csv, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)

                for row in reader:
                    if not row: continue

                    ocr_path = path.normpath(path.expanduser(row[0]))

                    if path.exists(ocr_path):
                        display_message("INFO", f"OCR Engine linked : {ocr_path}")
                        return ocr_path

        except Exception as e:
            display_message("WARN", "OCR configuration error.")

        # Prompt user to install, and/or locate path to executable file.
        display_message("WARN", "Tesseract OCR engine not found.")
        display_message("1", "Install engine based on OS - https://tesseract-ocr.github.io/tessdoc/Installation.html .")
        display_message("2", "If already installed, locate the path to the executable.")
        display_message("", "Ex : C:/Program Files/Tesseract-OCR/tesseract.exe")

        user_input = False

        while not user_input:
            user_input = input("\n>>> [L]ocate path / E[X]it and close window for now ?").strip().upper()

            if user_input == 'X': sys.exit()
            if user_input == 'L':
                ocr_path = self._identify_ocr_path()

                if not ocr_path or ocr_path == ".":
                    user_input = False
                    display_message("WARN", "No file selected.")
                elif path.exists(ocr_path):
                    display_message("INFO", "Tesseract engine identified.")
                    display_path_desc(ocr_path, 'file')
                else:
                    user_input = False
                    display_message("WARN", "Invalid path.")

        return ocr_path


    def _identify_ocr_path(self) -> str:
        print("\n>>> Locate Tesseract Executable File ...")
        path_input = identify_path('file', 'exe')
        norm_path = path.normpath(path_input)

        display_path_desc(norm_path, 'file')

        return norm_path


    def _clean_up_files_path(self):
        """Delete contents of paths.csv, and replace with the correctly identified / user-supplied path."""
        try:
            with open(self.paths_csv, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                tess_path = self.tesseract_path if os.sep=='/' else self.tesseract_path.replace(os.sep, '/')
                writer.writerow([tess_path])

        except Exception as e:
            display_message("WARN", f"{paths_csv} cannot be updated.", f"{e}")


    def _check_paths_file(self):
        """Creates a default CSV file for paths to be used by Tesseract."""
        csv_file = self.paths_csv

        if not path.exists(csv_file):
            paths = [
                ['C:/Program Files/Tesseract-OCR/tesseract.exe'],
                ['~/AppData/Local/Tesseract-OCR/tesseract.exe'],
                ['/usr/homebrew/bin/tesseract'],
                ['/usr/local/bin/tesseract/'],
                ['/usr/bin/tesseract/']
            ]   # Possible locations of tesseract.exe

            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(paths)


    def _load_registry(self):
        """Loads registry JSON file, or returns an empty list if not found."""
        if path.exists(self.registry_path):
            with open(self.registry_path, 'r') as file:
                try:
                    return json.load(file)
                except json.decoder.JSONDecodeError:
                    return []

        return []


    def _save_registry(self):
        """Saves the current project list to registry JSON file."""
        with open(self.registry_path, 'w') as file:
            json.dump(self.projects, file, indent=2)


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
            if proj['path'] == abs_path:
                display_message("WARN", "Project already exists in registry.")
                return False

        self.projects.append({
            'name': name,
            'path': abs_path if os.sep == '/' else abs_path.replace(os.sep, "/")
        })

        self._save_registry()
        display_message("INFO", f"Project \"{name}\" added to registry.")

        self.initialise_project(len(self.projects))
        display_message("INFO", f"Folder \"{name}\" initialised.")

        return True


    def initialise_project(self, project_number) -> bool:
        """"
        Check if the project exists in the registry, then initialise project files.
        :param project_number: The project number corresponding to the project name.
        :return:
        """
        if not (1 <= project_number <= len(self.projects)):
            display_message("WARN", "Project number out of range.")
            return False

        project_path = self.projects[project_number - 1]['path']

        if not path.exists(project_path):
            display_message("WARN", "Project path not found.")
            return False

        try:
            # Create 'assets' subfolder.
            asset_path = path.join(project_path, 'assets')
            if not path.exists(asset_path):
                os.makedirs(asset_path)

            log_files = [research_log, tags]
            for name in log_files:
                file_path = path.join(project_path, name)

                if not path.exists(file_path):
                    with open(file_path, 'w') as file:
                        json.dump([], file, indent=2)

            return True

        except Exception as e:
            display_message("WARN", "Error initialising project.", f"{e}")

            return False


class TextEntry:
    def __init__(self, project_path):
        """Initialise with the path to the active project."""
        self.project_path = project_path
        self.log_path = path.join(project_path, 'research_log.json')

    def capture_img(self):
        """Prompt user to take a screenshot.  Image in clipboard will be processed."""
        print("\n<=> Use preferred snipping tool to copy image to clipboard.")

        # Wait for user confirmation
        # user_input = input(
        #     "\nIs the image in your clipboard? (Press ENTER to continue, or 'q' to cancel): ").strip().lower()
        #
        # if user_input == 'q':
        #     display_message("INFO", "Capture cancelled by user.")
        #     return None

        in_clipboard = False

        while not in_clipboard:
            user_input = input(">>> Image copied to clipboard [Y]es/[No] ? ").strip().upper()
            in_clipboard = True if user_input=='Y' else False

        try:
            # Pull the image from the system clipboard.
            img = ImageGrab.grabclipboard()

            if isinstance(img, Image.Image):
                display_message("INFO", "Image retrieved from clipboard.")
                return img

            elif img is None:
                display_message("WARN", "Clipboard is empty.")
                return None

            elif isinstance(img, list):
                # If it's a list (some OS return a list of file paths if you copy a file)
                display_message("WARN", "Clipboard contains files.")
                return None

            else:
                display_message("WARN", "Clipboard content is not a valid format.")
                return None

        except Exception as e:
            display_message("WARN", "Error accessing clipboard.", f"{e}")
            return None


    def capture_entry(self, tags_manager=None):
        """The main workflow for capturing a text entry."""
        print("\n--- NEW TEXT ENTRY ---")

        # 1. Capture the Content (The Snip)
        print("Paste your text (Press Enter on an empty line to finish):")
        content_lines = []
        while True:
            line = input()
            if line == "":
                break
            content_lines.append(line)

        content = "\n".join(content_lines).strip()

        if not content:
            display_message("WARN", "Entry cancelled: No text provided.")
            return False

        # 2. Capture Metadata
        title = input("Entry Title: ").strip() or "Untitled Entry"
        source = input("Source (URL/Book): ").strip()

        # 3. Handle Tags (Placeholding for your TagManager)
        if tags_manager:
            tags_manager.display_tags()
            tag_input = input("Enter tags (comma separated or numbers): ")
            final_tags = tags_manager.resolve_tags(tag_input)
        else:
            tag_input = input("Tags (comma separated): ")
            final_tags = [t.strip() for t in tag_input.split(',') if t.strip()]

        notes = input("Personal Notes: ").strip()

        # 4. Save
        return self._save_to_log(title, content, source, final_tags, notes)


    def _save_to_log(self, title, content, source, tags, notes):
        entry = {
            "timestamp": f"{datetime.datetime.now()}Z",
            "title": title,
            "content": content,
            "source": source,
            "tags": tags,
            "notes": notes
        }

        try:
            data = []
            if path.exists(self.log_path):
                with open(self.log_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = []

            data.append(entry)

            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            display_message("INFO", "Entry saved to research log.")
            return True

        except Exception as e:
            display_message("WARN", "Could not save entry.", str(e))
            return False

