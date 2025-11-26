
"""
Main script: build a int config und save it to a file!!!!!
"""
from device_utils import (
    build_int_config,
    make_config_filename
)

HOSTNAME = "bld1-core-1"
INTERFACE_NAME = "GigabitEthernet1/0/1"
INTERFACE_DESC = "Uplink to Distribution"
VLAN_ID = 20

def main() -> None:

    interface_config= build_int_config(
        interface_name=INTERFACE_NAME,
        description=INTERFACE_DESC,
        vlan_id=VLAN_ID,
    )
    print(f"Generated int config:\n {interface_config}")

    filename = make_config_filename(HOSTNAME)
    print(f"\nwill be saved to file: {filename}\n")

    try:
        with open(filename, "w", encoding="utf-8") as config_file:
            config_file.write(interface_config)
    except OSError as error:
        print(f"Es gibt einen Fehler: {error}")
    else:
        print("Es gibt keinen Fehler\n siehe es noch einmal\n")
        try:
            with open(filename, "r", encoding="utf-8") as config_file:
                content = config_file.read()
                print(content)
        except OSError as error:
            print(f"Error mit lesen config file: {error}")
        else:
            print("\nAlles ist in Ordnung\n")

    finally:
        print("\nFinished script.")

if __name__ == "__main__":
    main()





