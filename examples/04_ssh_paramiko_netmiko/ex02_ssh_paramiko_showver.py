
# ssh_paramiko_show_version_regex.py

import paramiko
import getpass
import re

def send_command(client: paramiko.SSHClient, command: str) -> str:
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode(errors="ignore")
    return output

def main() -> None:
    command = "show version"
    hostname = input("ip address: ").strip()
    username = input("username: ").strip()
    password = getpass.getpass("password: ")

    pattern = re.compile(r"\((X86\S+)\),\s+(Version\s+[\w.]+),", re.I)  #IOU
    #pattern = re.compile(r"Version\s+([\w().]+)", re.I)       #real IOS

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname= hostname,
            port= 22,
            username= username,
            password= password,
            look_for_keys= False,
            allow_agent= False, 
        )
        
        output = send_command(client, command)
        match_version = pattern.search(output)
        if match_version:
            part_num = match_version.group(1)
            version = match_version.group(2)
            print(f"{part_num} {version}")
        else:
            print("version not found!!")

    except Exception as error:
        print(f"there is a problem: {error}")

    finally:
        client.close()

if __name__ == "__main__":
    main()


