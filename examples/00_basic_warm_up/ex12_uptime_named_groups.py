
import re

def ask_file(default_name: str = "sh_ver.txt") -> str:
    filename = input(f"name your file: | [{default_name}]").strip()
    if not filename:
        return default_name
    return filename
def read_file(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()
def main() -> None:
    pattern_name = re.compile(r"Device name:\s+(?P<Device_name>\S+)", re.M)
    pattern_uptime = re.compile(r"(?P<years>\d+)\s+year,.*?(?P<day>\d+)\s+day\(s\),\s+(?P<hour>\d+)\s+hour\(s\)", re.M)
    
    filename = ask_file()
    try:
        text = read_file(filename)
    except FileNotFoundError:
        print(f"file {filename} not found!!!!!")
        return
    name_match = pattern_name.search(text)
    if not name_match:
        print("name not found!!!!")
        return
    
    uptime_match = pattern_uptime.search(text)
    if not uptime_match:
        print("not found uptime!!!!")
        return
    
    print(f"Device name: {name_match.group('Device_name')}")

    print(f"Years: {uptime_match.group('years')}, Days: {uptime_match.group('day')}, Hour: {uptime_match.group('hour')}")


if __name__ == "__main__":
    main()





