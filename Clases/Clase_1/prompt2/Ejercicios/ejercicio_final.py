import argparse

def main():
    parser = argparse.ArgumentParser(description="procesar archivos de entrada y salida")
    parser.add_argument("-i", "--input", type=str, required=True, help="archivo de entrada")
    parser.add_argument("-o", "--output", type=str, required=True, help="archivo de salida")
    args = parser.parse_args()

    try:
        with open(args.input, "r") as infile:
            contenido = infile.read()

        with open(args.output, "w") as outfile:
            outfile.write(contenido)

        print(f"el contenido de '{args.input}' fue copiado a '{args.output}'")
    
    except FileNotFoundError:
        print(f"Error: el archivo '{args.input}' no existe")

    print(f"archivo de entrada: {args.input}")
    print(f"archivo de salida: {args.output}")

if __name__ == '__main__':
    main()