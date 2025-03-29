import argparse
import time

def main():
    parser = argparse.ArgumentParser(description="Procesar archivos de entrada y salida con opciones avanzadas")
    parser.add_argument("-i", "--input", type=str, required=True, help="Archivo de entrada")
    parser.add_argument("-o", "--output", type=str, required=True, help="Archivo de salida")
    parser.add_argument("-n", "--numero", type=int, default=1, help="Número de repeticiones (por defecto: 1)")
    parser.add_argument("-m", "--modo", choices=["rapido", "lento"], default="rapido", help="Modo de ejecución (por defecto: rapido)")
    args = parser.parse_args()

    try:
        with open(args.input, "r") as infile:
            contenido = infile.read()
        
        with open(args.output, "w") as outfile:
            for _ in range(args.numero):
                outfile.write(contenido + "\n")
                if args.modo == "lento":
                    time.sleep(1)  
        
        print(f"El contenido de '{args.input}' fue copiado {args.numero} veces en '{args.output}' en modo {args.modo}.")

    except FileNotFoundError:
        print(f"Error: El archivo '{args.input}' no existe. Verifica el nombre e intenta nuevamente.")

if __name__ == "__main__":
    main()
