
# ssh_paramiko_show_clock.py

import paramiko
import getpass

def send_command(client: paramiko.SSHClient, command: str) -> str:
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode(errors="ignore")
    return output

def main() -> None:
    command = "show clock"
    hostname = input("ip address: ").strip()
    username = input("username: ").strip()
    password = getpass.getpass("password: ")

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
        print(f"\n----Show Clock----\n{output}")

    except Exception as error:
        print(f"there is a problem: {error}")

    finally:
        client.close()

if __name__ == "__main__":
    main()


