import getopt
import sys

def main():
    options, args = getopt.getopt(sys.argv[1:], "f:")

    for option, value in options:
        if option == "-f":
            print(f"archivo de entrada: {value}")

if __name__ == '__main__':
    main()