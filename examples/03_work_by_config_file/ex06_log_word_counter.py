
def main() -> None:

    try:
        with open("sample_log.txt", "r", encoding="utf-8") as f:
            file_log = f.read()

    except OSError as error:
        print(f"error reading file: {error}")
        return
    
    row = len(file_log.splitlines())
    words = len(set(file_log.split()))
    print(f"Lines: {row}, Uniqe words: {words}")


if __name__ == "__main__":
    main()
    
