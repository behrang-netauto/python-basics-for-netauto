
def main() -> None:
    x = "cisco"
    y = "cisco"
    a = [1, 2, 3]
    b = [1, 2, 3]

    print("x: ", x, " | id:", id(x))
    print("y: ", y, " | id:", id(y))
    print("x == y ?", x == y)
    print(x == y)
    print(x is y)
    print(a is b)
    print(id(a), id(b)) 

if __name__ == "__main__":
    main()


