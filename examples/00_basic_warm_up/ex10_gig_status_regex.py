
import re

def ask_file(default_file: str = "sh_ip_int_brief.txt") -> str:
    ip_file = input(f"ip_file | [{default_file}]: ").strip()
    if not ip_file:
        return default_file
    return ip_file
def read_file(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()
    
def main() -> None:
    pattern_up = re.compile(r"(\b[GLV]\S+\b)\s+.*(\bup\b.*?\bup\b)", re.M)             # ? = lazy
    pattern_down = re.compile(r"(\b[GLV]\S+\b)\s+.*(\bdown\b.*?\bdown\b)", re.M)
    filename = ask_file()
    try:
        text = read_file(filename)
    except FileNotFoundError:
        print(f"file {filename} not found!!!!!")
        return
    
    print("UP: ")
    for line in pattern_up.finditer(text):
        int = line.group(1)
        print(int)
    
    print("Down: ")
    for line in pattern_down.finditer(text):
        int = line.group(1)
        print(int)

if __name__ == "__main__":
    main()


    

