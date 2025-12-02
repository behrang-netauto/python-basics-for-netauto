
from ex01_device_utils_function import is_core, make_description, extract_hostname

def ask_config_filename(defaul_filename: str = "config.txt") -> str:
    user_input = input(f"config file name? | [{defaul_filename}]").strip()
    if not user_input:
        return defaul_filename
    return user_input

def read_config_file(filename: str) -> str:
    with open(filename, "r", encoding= "utf-8") as f:
        return f.read()

def main() -> None:
    filename = ask_config_filename()

    try:
        config_text = read_config_file(filename)
    except FileNotFoundError:
        print(f"file {filename} not found!")
        return

    hostname = extract_hostname(config_text)
    if hostname is None:
        print("there is no hostname's row!!!")
    if hostname == "":
        print("hostname's row has any value!!!")
        return
    print(f"hostname is: {hostname}")

    if is_core(hostname):
        print("deivce is a core!!")
    else:
        print("device isn't core!!")
    
    desc1 = make_description("GigabitEthernet0/1", "Uplink to distribution")
    desc2 = make_description("GigabitEthernet0/2", "User VLAN 20")
    desc3 = make_description("Loopback0", "Router-ID")

    print(desc1)
    print(desc2)
    print(desc3)

if __name__ == "__main__":
    main()



