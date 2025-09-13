from python_runtime.probe import probe
from ai_runtime.runtime import AIRuntime


def main() -> None:
    my_list = probe([1, 2, 3], "be a good list :)", AIRuntime())
    my_list.append(4)
    my_list.append(5)
    my_list.append(6)
    length = my_list.__len__()
    print(my_list)
    print(f"Length: {length}")


if __name__ == "__main__":
    main()
