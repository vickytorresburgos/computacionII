import json
from utils import calcular_hash

def verificar_blockchain(filename="blockchain.json"):
    try:
        with open(filename, "r") as f:
            blockchain = json.load(f)
    except Exception as e:
        print(f"Error al leer {filename}: {e}")
        return

    if not blockchain:
        print("Blockchain vacía.")
        return

    errores = []
    alertas = 0
    sum_frec = 0
    sum_oxi = 0
    sum_pres_sis = 0
    sum_pres_dia = 0
    total = len(blockchain)

    for i, bloque in enumerate(blockchain):
        esperado = calcular_hash(
            bloque["prev_hash"],
            bloque["datos"],
            bloque["timestamp"]
        )
        if bloque["hash"] != esperado:
            errores.append(f"Bloque {i}: hash incorrecto")
        if i > 0 and bloque["prev_hash"] != blockchain[i-1]["hash"]:
            errores.append(f"Bloque {i}: prev_hash incorrecto")
        if bloque.get("alerta"):
            alertas += 1

        # Sumar medias para promedios generales
        sum_frec += bloque["datos"]["frecuencia"]["media"]
        sum_oxi += bloque["datos"]["oxigeno"]["media"]
        sum_pres_sis += bloque["datos"]["presion"]["media"][0]
        sum_pres_dia += bloque["datos"]["presion"]["media"][1]

    prom_frec = sum_frec / total if total else 0
    prom_oxi = sum_oxi / total if total else 0
    prom_pres_sis = sum_pres_sis / total if total else 0
    prom_pres_dia = sum_pres_dia / total if total else 0

    print(f"Bloques verificados: {total}")
    print(f"Alertas detectadas: {alertas}")
    print(f"Promedio frecuencia: {prom_frec:.2f}")
    print(f"Promedio presión: [{prom_pres_sis:.2f}, {prom_pres_dia:.2f}]")
    print(f"Promedio oxígeno: {prom_oxi:.2f}")
    if errores:
        print("Errores encontrados:")
        for err in errores:
            print("  -", err)
    else:
        print("Integridad de la cadena: OK")

    # Generar reporte
    with open("reporte.txt", "w") as rep:
        rep.write(f"Bloques verificados: {total}\n")
        rep.write(f"Alertas detectadas: {alertas}\n")
        rep.write(f"Promedio frecuencia: {prom_frec:.2f}\n")
        rep.write(f"Promedio presión: [{prom_pres_sis:.2f}, {prom_pres_dia:.2f}]\n")
        rep.write(f"Promedio oxígeno: {prom_oxi:.2f}\n")
        if errores:
            rep.write("Errores encontrados:\n")
            for err in errores:
                rep.write(f"  - {err}\n")
        else:
            rep.write("Integridad de la cadena: OK\n")

if __name__ == "__main__":
    verificar_blockchain()