# Research Tool : General Development Plan

**Date** : 26 Dec 2025

**Goal** : A Python-based "Digital Index Card" system for capturing research snippets.

**Status** : Under development.

---

## CORE PHILOSOPHY
* **Intentionality** : User inputs metadata BEFORE the snip to ensure organisation.
* **One-Shot Execution** : No background listeners. Run >> Capture >> Save >> Exit.
* ~~**Portability** : Avoid global binaries (like `Tesseract`). Use pip-managed libraries only.~~
* **Atomic Data** : Each entry is a discrete JSON object representing one "Index Card."

---

## DATA STRUCTURE (JSON SCHEMA)
Each capture creates an object with the following keys:

- **id** : (System) UUID v4 string.
- **type** : (User) Selection of 'text', 'table', or 'image'.
- **title** : (User) Descriptive name of the entry.
- **source** : (User) URL or document reference.
- **notes** : (User) Personal annotations or context.
- **tags** : (User) List of strings (handled by hybrid resolution).
- **content** : (System) 
    - for text: Raw string (with embedded formatting) of the OCR output;
    - for table: 2D Array (List of Lists); and,
    - for image: String path to the saved .png/.jpg file.
- **date** : (System) ISO 8601 UTC timestamp.
- **schema_version** : "1.0"

---

## COMPONENT MODULES

### Project Registry - Bookmarks
- Maintain a registry in script's root.
- Store project name (folder name) and absoluate path
- Validate path, on start up. If missing user is prompted to re-locate the folder.

### Central Controller
- Handle the workflow sequence.
- Triggers the system snipping tool (e.g., 'snippingtool /clip' on Windows).
- Grab image from clipboard once the user finishes snipping.
- Maintain project-level storage structure :
  1. `research_log.json` - master list of index cards by : 'table', 'text', 'images';
  2. `tags.json` - project-specific tag library; and,
  3. `/assets` - a subfolder for image captures.

### Tag Manager
- Uses a local 'tags.json' file for persistence.
- Hybrid Logic for Input :
    1. Check for direct match (Is '1812' already a tag?).
    2. Check for index match (Did user type '0' for the first tag in the list?).
    3. New Entry (If neither, create a new tag and update 'tags.json').

### Processing Modules
- Text Module: Uses ~~`EasyOCR`~~ `PyTesseract` with paragraph grouping for high-fidelity snippets.
- Table Module: Uses `OpenCV` or `img2table` to reconstruct 2D structure.
- Image Module: Handles file compression and local storage in an /assets/ folder.

### Display Module
- Displays the stored data based on filter options; primarily by tag.
---

## USER WORKFLOW
1. User launches script.
2. Script prompts for 'research' to find/load the correct files.  (Multiple ongoing research topics.)
3. Script prompts for Title, Source, Notes, and Tags.
4. User selects 'Type' (Text/Table/Image).
5. Script launches native Snipping Tool.
6. User captures area; Snip goes to clipboard.
7. Script detects clipboard content, processes it, and appends to 'research_log.json'.