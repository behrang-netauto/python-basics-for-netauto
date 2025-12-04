
def string_bytes() -> tuple[bytes, str]:
    user_input = input("Type your command: ").strip()
    
    command_bytes = user_input.encode("utf-8")
    decode_command = command_bytes.decode("utf-8")

    return command_bytes, decode_command

def main() -> None:
    command_bytes, decode_command = string_bytes()

    print(f"byte value: {command_bytes!r}, type: {type(command_bytes)}")
    print(f"decode value: {decode_command!r}, type: {type(decode_command)}")

if __name__ == "__main__":
    main()

