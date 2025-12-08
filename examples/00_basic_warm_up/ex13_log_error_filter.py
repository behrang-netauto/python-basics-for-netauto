
import re

def ask_finename (default_name: str = "sample_syslog.txt") -> str:
    file_name = input(f"your_file_name: | [{default_name}]").strip()
    if not file_name:
        return default_name
    return file_name

def read_file (file_name: str) -> str:
    with open(file_name, "r" , encoding= "utf-8") as f:
        return f.read()
def main() -> None:
    pattern_eeror = re.compile(r"\berror\b", re.I)
    file_name = ask_finename()
    try:
        text = read_file(file_name)
    except FileNotFoundError:
        print(f"file {file_name} not found!!!!")
        return
    found_flag = False

    for line in text.splitlines():
        if pattern_eeror.search(line):
            print(line)
            found_flag = True
    
    if not found_flag:
        print("no error!!!")

if __name__ == "__main__":
    main()
