import argparse

def main():
    parser = argparse.ArgumentParser(description="procesar archivos de entrada y salida")

    parser.add_argument("-f", "--file", type=str, required=True, help="archivo de entrada")

    args = parser.parse_args()

    print(f"archivo de entrada: {args.file}")

if __name__ == '__main__':
    main()