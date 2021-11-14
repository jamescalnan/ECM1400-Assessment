from rich.console import Console
import msvcrt
c = Console()

def run_menu(menu_options: list):
    current_option = 0
    usr_choice = ""
    while not usr_choice == "g":
        c.clear()
        c.show_cursor = False
        prt_str = ""
        for i, x in enumerate(menu_options):
            if i == current_option:
                prt_str += f" > {x}[white]"
            else:
                prt_str += f"[white] {x}[white]"
            prt_str += "\n[white]"
        prt_str += f"\nPress w to go up, s to go down, g to choose\r"
        c.print(prt_str)

        usr_choice = str(msvcrt.getch()).split("'")[1]
        c.show_cursor = False        
        if usr_choice == "w":
            current_option -= 1 if current_option > 0 else 0
        elif usr_choice == "s":
            current_option += 1 if current_option < len(menu_options) - 1 else 0
        elif usr_choice == "g":
            return menu_options[current_option]
