
import getpass

def authentication() -> tuple[str, str]:
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()
    return username, password

def main() -> None:
    username, password = authentication()

    if not password:
        print("password is empty")
        return
    
    print(f"Credentials for {username} received")

    if len(password) < 8:
        print("warning: password is shorter than 8 characters")
        
if __name__ == "__main__":
    main()
