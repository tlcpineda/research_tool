import os

from lib import display_message
from Tools import RegistryManager, TagManager, TextEntry


def main():
    display_message("INFO", "Starting Tools.py Validation Test")

    # 1. Setup Registry
    reg = RegistryManager()

    # 2. Define a Test Project
    test_name = "System_Test_Project"
    test_path = os.path.join(os.getcwd(), "Test_Project_Folder")

    # Add project (this handles folder creation and tesseract config)
    if reg.add_project(test_name, test_path):
        display_message("INFO", f"Created: {test_name}")
    else:
        # If it already exists, just initialize it
        reg.initialise_project(1)
        display_message("INFO", f"Using existing: {test_name}")

    # 3. Instantiate Managers
    # We grab the path from the registry to ensure it's the normalized version
    active_path = reg.projects[-1]["path"]
    tags_mgr = TagManager(active_path)
    text_tool = TextEntry(active_path, tags_mgr)

    # 4. Execute Capture Workflow
    # Note: Have an image with text copied to your clipboard before running!
    try:
        success = text_tool.capture_entry()

        if success:
            display_message("INFO", "Workflow successful. Check research_log.json.")
        else:
            display_message("WARN", "Workflow was cancelled.")

    except Exception as e:
        display_message("WARN", "Test failed during execution.", str(e))


if __name__ == "__main__":
    main()
