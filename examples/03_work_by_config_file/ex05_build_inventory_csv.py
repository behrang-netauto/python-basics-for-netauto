
import csv

def main() -> None:
    devices = [
    {"site": "BER1", "hostname": "ber1-core-1", "mgmt_ip": "10.10.10.11"},
    {"site": "BER2", "hostname": "ber2-core-1", "mgmt_ip": "10.10.20.11"},]

    fieldnames = ["site", "hostname", "mgmt_ip"]

    try:
        with open("devices_inventory.csv", "w", newline="", encoding="utf-8") as f:
           writer = csv.DictWriter(f, fieldnames=fieldnames)
           
           writer.writeheader()
           writer.writerows(devices)

        print("devices_inventory.csv written successfully.")

    except OSError as error:
        print(f"error writing CSV: {error}")


if __name__ == "__main__":
    main()
    
      
