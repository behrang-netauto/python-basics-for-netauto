
import re

def ask_file(default_file: str = "sh_ver.txt") -> str:
    ver_file = input(f"version_file: | [{default_file}]").strip()
    if not ver_file:
        return default_file
    return ver_file

def read_file(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()
    
def main() -> None:
    pattern = re.compile(r"\bC9\d{3}\S+\b", re.M)

    filename = ask_file()
    try:
        text = read_file(filename)
    except FileNotFoundError:
        print(f"file {filename} not found!!!")
        return
    for math in pattern.findall(text):
        version = math
        print(f"Router model: {version}")
        return
if __name__ == "__main__":
    main()

    """
    for math in pattern.finditer(text):
        version = math.group(0)
        pirnt(f"Router model: {version})
        return
    """
