import csv

def main () -> None:
    
    try:
        with open("devices_inventory.csv", "r", encoding="utf-8") as f:
            
            reader = csv.DictReader(f)
            
            for row in reader:
                hostname = row["hostname"]
                mgmt_ip = row["mgmt_ip"]

                print(f"connecting to {hostname} at {mgmt_ip}")
    
    except OSError as error:
        print(f"error reading CSV: {error}")


if __name__ == "__main__":
    main()
    