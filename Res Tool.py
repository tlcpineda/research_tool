from lib import create_path, display_menu, display_message, hor_bar, welcome_sequence
from Tools import RegistryManager

# Module Variables
name = "Research Tool"
ver = "1.00.00"
date = "26 Dec 2025"
email = "tlcpineda.projects@gmail.com"
width = 100
indent = 10

reg = RegistryManager()


# Functions to process registry
def list_projects() -> list:
    projects = reg.projects
    proj_dir_list = []

    def truncate_name(text, num_chars):
        return text if len(text) < num_chars else f"{text[: num_chars - 5]}..."

    def truncate_path(text, num_chars):
        return text if len(text) < num_chars else f"...{text[len(text) - num_chars :]}"

    if projects:
        print("\n<=> PROJECTS IN REGISTRY :")
        for index, project in enumerate(projects):
            proj_dir_list.append(project["path"])
            name_width = 35
            path_width = 45

            # print(f" [ {index + 1:>2} ] {truncate_text(project['name'], 0):<35} {truncate_text(project['path'], 1):<45}")
            print(
                f"  [ {index + 1:>2} ]  "
                f"{f'{truncate_name(project['name'], name_width)}':<{name_width}}  "
                f"{f'{truncate_path(project['path'], path_width)}':<{path_width}}"
            )

        print("")

    else:
        display_message("WARN", "No projects found in registry.")

    return proj_dir_list


def add_new_project() -> int:
    folder_name, folder_path = create_path()
    reg.add_project(folder_name, folder_path)

    return len(reg.projects)


def select_project() -> int:
    proj_num = 0

    while not proj_num:
        resp = input("\n>>> Enter project number : ")

        if 0 <= int(resp) <= len(reg.projects):
            proj_num = int(resp)

    return proj_num


if __name__ == "__main__":
    options = [
        {"menu": "[N]ew Project", "shortkey": "N", "func": add_new_project},
        {"menu": "[L]ist Projects", "shortkey": "L", "func": list_projects},
        {"menu": "[S]elect Project", "shortkey": "S", "func": select_project},
        {"menu": "E[X]it", "shortkey": "X"},
    ]
    welcome_sequence([f"{name} v{ver}", date, email], width)
    project_list = list_projects()
    opts_filter = ["N", "S", "X"] if len(project_list) else ["N", "X"]
    options = [option for option in options if option["shortkey"] in opts_filter]

    confirm_exit = False

    while not confirm_exit:
        display_menu(width, indent, options)
        user_input = None

        while not user_input:
            resp = input(">>> ").upper()

            if resp in opts_filter:
                user_input = resp
            else:
                display_message("WARN", f"Select a valid option {opts_filter}.")

        if user_input == "X":
            hor_bar(width, indent, "CLOSING DOWN ...")
            confirm_exit = True
        else:
            print("")

            selected_option = [
                option for option in options if option["shortkey"] == user_input
            ][0]
            func_selected = selected_option["func"]

            hor_bar(width, indent, f"RUNNING : {func_selected.__name__}()")
            func_ret = func_selected()
            hor_bar(width, indent, f"COMPLETE : {func_selected.__name__}()")

            if user_input in ["N", "S"]:
                # load_project(func_ret)
                pass
