import json

import os

import sys
from os import path
from lib import display_message

# Class variables :
registry_name = 'registry.json'  # JSON log of projects; list of objects
user_data = 'user_data' # Folder name containing the registry file
research_log = 'research_log.json'  # JSON log of all research data.
tags = 'tags.json'  # JSON log of tags used for each entry in research_log
img_folder = 'assets'   # Folder name containing the images snipped

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

        self.registry_path = path.join(self.user_data_path, registry_name)
        self.projects = self._load_registry()
        self._save_registry()


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


