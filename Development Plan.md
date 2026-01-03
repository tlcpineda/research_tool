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

## REGISTRY SCHEMA
Each project has a corresponding object stored in `registry.json`.

Example :

```
{
  "name": "Legal Research on the Impact of Government Subsidies 2025",
  "path": "C:/Users/Name/Documents/History Project",
  "lang": "fra+eng+deu",
  "created": "2025-10-25T05:05:35.000000+00:00"
}
```

- **name** : (User) The name of the project
- **path** : (User) The local path to the folder containing the resources for project
- **lang** : (User) The languages used in OCR methods; currently only ENG is supported.
- **created** : (System) The UTC date object when the folder is created


## DATA SCHEMA
Each capture creates an object with the following keys:

Example :

```
{
  "type": "text",
  "title": "INDUSTRIAL-REVOLUTION-NOTES",
  "source": "https://en.wikipedia.org/wiki/Industrial_Revolution",
  "notes": "Found this particularly useful for the chapter on steam power."
  "tags": ["HISTORY", "ECONOMICS", "<1760>", "<1840>"],
  "content": "The transition to new manufacturing processes in Great Britain, continental Europe and the United States, in the period from about 1760 to sometime between 1820 and 1840.",
  "lang": "eng",
  "created": "2025-10-25T05:05:35.000000+00:00",
}
```

- ~~**id** : (System) UUID v4 string.~~
- **type** : (User) Selection of 'text', 'table', or 'image'.
- **title** : (User) Descriptive name of the entry.
- **source** : (User) URL or document reference.
- **notes** : (User) Personal annotations or context.
- **tags** : (User) List of strings (handled by hybrid resolution).
- **content** : (System) 
    - for text: Raw string (with embedded formatting) of the OCR output;
    - for table: 2D Array (List of Lists); and,
    - for image: String path to the saved .png/.jpg file.
- **lang** : (System/User) Language to be used by OCR engine.
- **created** : (System) ISO 8601 UTC timestamp.
- ~~**schema_version** : "1.0"~~

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
  1. `research_log.json` - master list of index cards by : 'table', 'text', 'image';
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


## Future Development
1. [ ] Function UI
2. [ ] Detect, store text formatting in markdown.
3. [ ] Allow user to edit OCR-captured text; in text editor, or in dedicated UI.
4. [ ] User-set OCR language setting.
5. [ ] Allow user-specified OCR engine configuration for each entry; psm, oem.
6. [ ] OCR-captured text clean up.
