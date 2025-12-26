import os
import tkinter as tk
from tkinter import filedialog as fd

def welcome_sequence(items: list, width: int) -> None:
    max_chars = len(max(items, key=len))
    line_len =  max(max_chars + 10 * 2, width or 60)
    items = [''] + items + ['']

    hor_bar(line_len)

    for item in items:
        print(f"{item:^{line_len}}")

    hor_bar(line_len)


def hor_bar(num_chars: int, indent: int=0, text: str=None) -> None:
    display_x = num_chars * "░"

    if text is not None:    # Redefine display if text is defined
        text_len = len(text)
        padded_len = (0 if text is None else 2) * 2 + text_len
        indent = indent if indent else 0
        display_x = display_x[:indent] + f"{text:^{padded_len}}" + display_x[indent+padded_len:]

    print(display_x)


def identify_path(base_type: str) -> str:
    root = tk.Tk()
    root.withdraw()

    path = None

    match base_type:
        case "file":
            path = fd.askopenfilename(
                title="Select PDF File",
                filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
            )
        case "folder":
            path = fd.askdirectory(
                title="Select Folder"
            )

    return path


def create_path() -> tuple:
    print("\n>>> Create New Project ...")
    is_valid_name = False
    folder_name = None
    full_path = None

    print(">>>  Folder to place new project ...")

    folder_path = identify_path('folder')
    display_path_desc(folder_path, 'folder')

    while not is_valid_name:
        folder_name = input(">>>  New project name : ").strip()
        full_path = os.path.abspath(os.path.join(folder_path, folder_name))

        try:
            os.mkdir(full_path)
            display_message("INFO", "Project folder created")
            display_path_desc(full_path, 'folder')
            is_valid_name = True

        except OSError as os_e:
            display_message("ERROR", "Invalid directory.", f"{os_e}")
        except  Exception as e:
            display_message("ERROR", "Error creating new project.", f"{e}")

    return folder_name, full_path


def display_path_desc(filepath: str, base_type: str) -> tuple:
    parent_name, base_name = os.path.split(filepath)
    split_parent_name = parent_name.split(os.sep)
    num_levels = 3
    process_dirname = parent_name if len(split_parent_name) <= num_levels else f".../{"/".join(split_parent_name[-3:])}"

    print(f"\n<=> {base_type.title()} Details :"
          f"\n<=>  Directory : {process_dirname}"
          f"\n<=>  Base Name : {base_name}")

    return parent_name, base_name


def continue_sequence() -> bool:
    proper_resp = False
    resp = "C"

    while not proper_resp:
        print("\n>>> Select an option :"
              "\n>>>  [C]ontinue with another chapter ?"
              "\n>>>  E[X]it and close this window ?")

        resp = input(">>> ").upper()

        proper_resp = True if resp in ['C', 'X'] else False

    if resp == 'X':
        print("\n<=> Closing down ...")

        return True
    else:
        print("\n<=> Restarting ...\n")

        return False


def display_message(tag: str, message: str, exception: str=None) -> None:
    print(f"\n<=> [{tag}] {message}")

    if exception:
        print(f"<=>  {exception}")


def process_pathname(case_num: int, base_path: str, target: str="", data: list=None) -> str | None:
    psd_path = os.path.join(base_path, target)

    if not psd_path: return None

    display_path_desc(psd_path, "folder")

    for item in os.listdir(psd_path):
        filename, ext = os.path.splitext(item)

        display_message(
            "PROCESSING",
            f"{item} ..."
        )

        if ext.lower()==".psd": # Process only PSD files
            path0 = os.path.join(psd_path, item)

            if os.path.isfile(path0):

                match case_num:
                    case 1: # Initial case when appending page markers ("##X") to original file name.
                        page_num = filename[-2:]

                        if page_num.isdigit():
                            new_filename = f"{filename} {page_num}X{ext}"
                            path1 = os.path.join(psd_path, new_filename)

                            if path0 == path1:
                                display_message(
                                    "SKIP",
                                    "File with the same target name exists."
                                )
                            else: rename_path(path0, path1, "file")
                        else:
                            display_message(
                                "SKIP",
                                "Not a valid file path."
                            )

                    case 2: # Case when marking files for revision, with "X"
                        if " " in filename:
                            filename0, page = filename.split(" ")

                            if page.isdigit() and page in data:
                                new_filename = f"{filename}X{ext}"
                                path1 = os.path.join(psd_path, new_filename)

                                if path0 == path1:
                                    display_message(
                                        "SKIP",
                                        "File already marked."
                                    )
                                else: rename_path(path0, path1, "file")
                            else:
                                display_message(
                                    "SKIP",
                                    f"No revisions required."
                                )
                        else:
                            display_message(
                                "SKIP",
                                "No page marker found."
                            )

                    case 3: # Case when cleaning up files name, prior to submission, remove page markers ("##" or "##X")
                        if " " in filename:
                            filename0, page = filename.split(" ")

                            new_filename = f"{filename0}{ext}"
                            path1 = os.path.join(psd_path, new_filename)

                            if path0 == path1:
                                display_message(
                                    "SKIP",
                                    "File with the same name exists."
                                )
                            else:
                                rename_path(path0, path1, "file")
                        else:
                            display_message(
                                "SKIP",
                                "No page marker found."
                            )

            else:
                display_message(
                    "SKIP",
                    "Not a valid file path."
                )
        else:
            display_message(
                "SKIP",
                "Not a PSD file."
            )

    return psd_path


def rename_path(path_src: str, path_dst, pathtype: str) -> None:
    base_src = os.path.basename(path_src)
    base_dst = os.path.basename(path_dst)
    try:
        os.rename(path_src, path_dst)

        display_message(
            "SUCCESS",
            f"F{pathtype[1:]} renamed."
            f"\n<=>  From : {base_src}"
            f"\n<=>  To   : {base_dst}"
        )

    except Exception as e:
        display_message(
            "ERROR",
            f"Failed to rename {pathtype}.",
            f"{e}"
        )


def display_menu(width: int, indent: int, options):
    print("")

    hor_bar(width or 60, indent, "MENU")
    print("")

    for option in options:
        print(f"{" ":{indent or 5}}{option['menu']}")

    print("")
    hor_bar(width or 60, indent)

    print("\n>>> Select an option ...")