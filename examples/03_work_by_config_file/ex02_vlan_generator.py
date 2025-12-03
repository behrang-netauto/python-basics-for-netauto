def ask_vlans() -> tuple[int, int]:
    start_vlan = int(input("Start VLAN: ").strip())
    end_vlan = int(input("End VLAN: ").strip())
    return start_vlan, end_vlan


def print_vlans(start_vlan: int, end_vlan: int, only_even: bool = False) -> None:
    for vlan_id in range(start_vlan, end_vlan + 1):
        if only_even and vlan_id % 2 != 0:
            continue

        print(f"vlan {vlan_id}")
        print(f"  name VLAN_{vlan_id}")


def main() -> None:
    start_vlan, end_vlan = ask_vlans()

    print("=== All VLANs ===")
    print_vlans(start_vlan, end_vlan)

    print("\n=== Even VLANs only ===")
    print_vlans(start_vlan, end_vlan, only_even=True)


if __name__ == "__main__":
    main()
    
