
def input_and_read(filename: str = "config.txt") ->str:
    config_filename = input(f"your filename? [{filename}]").strip()
    if not config_filename:
        config_filename = filename
    return config_filename

def main() -> None:
    try:
        with open(input_and_read(), "r") as f:
            content = f.read()
    except OSError as error:
        print(f"file not found: {error}")
    else:
        print(content)
    finally:
        print("\nFinished script.")

if __name__ == "__main__":
    main()


