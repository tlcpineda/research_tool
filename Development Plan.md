# Research Tool
**Date** : 26 Dec 2025

**Goal** : A Python-based "Digital Index Card" system for capturing research snippets.

---

## CORE PHILOSOPHY
* **Intentionality** : User inputs metadata BEFORE the snip to ensure organisation.
* **One-Shot Execution** : No background listeners. Run >> Capture >> Save >> Exit.
* **Portability** : Avoid global binaries (like `Tesseract`). Use pip-managed libraries only.
* **Atomic Data** : Each entry is a discrete JSON object representing one "Index Card."

---

## DATA STRUCTURE (JSON SCHEMA)
Each capture creates an object with the following keys:

- **id** : (System) UUID v4 string.
- **type** : (User) Selection of 'text_snippet', 'table', or 'image'.
- **title** : (User) Descriptive name of the entry.
- **source** : (User) URL or document reference.
- **notes** : (User) Personal annotations or context.
- **tags** : (User) List of strings (handled by hybrid resolution).
- **content** : (System) 
    - For text: Raw string of the OCR output.
    - For table: 2D Array (List of Lists).
    - For image: String path to the saved .png file.
- **date** : (System) ISO 8601 UTC timestamp.
- **schema_version** : "1.0"

---

## COMPONENT MODULES

### A. Central Controller
- Handles the workflow sequence.
- Triggers the system snipping tool (e.g., 'snippingtool /clip' on Windows).
- Grabs image from clipboard once the user finishes snipping.

### B. Tag Manager
- Uses a local 'tags.json' file for persistence.
- Hybrid Logic for Input:
    1. Check for Direct Match (Is '1812' already a tag?).
    2. Check for Index Match (Did user type '0' for the first tag in the list?).
    3. New Entry (If neither, create a new tag and update 'tags.json').

### C. Processing Modules
- Text Module: Uses `EasyOCR` with paragraph grouping for high-fidelity snippets.
- Table Module: Uses `OpenCV` or `img2table` to reconstruct 2D structure.
- Image Module: Handles file compression and local storage in an /assets/ folder.

### D. Display Module
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