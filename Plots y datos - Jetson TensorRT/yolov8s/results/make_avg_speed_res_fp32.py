import json

def main():
    """
    Lee un archivo avg_speed.json con múltiples ejecuciones (runs) de un mismo modelo
    y calcula el promedio de tres métricas:
    - avg_preprocess_speed
    - avg_inf_speed
    - avg_postprocess_speed

    Luego muestra los promedios en pantalla.
    """
    filename = "evaluation_predict_results_fp32.json"

    with open(filename, "r") as file:
        data = json.load(file)

    # Listas para almacenar las velocidades de cada corrida
    preprocess_speeds = []
    inf_speeds = []
    postprocess_speeds = []

    # Recorrer todas las ejecuciones (runs) en el archivo JSON
    for run in data:
        results = run["results"]
        preprocess_speeds.append(results["avg_preprocess_speed"])
        inf_speeds.append(results["avg_inf_speed"])
        postprocess_speeds.append(results["avg_postprocess_speed"])

    # Calcular los promedios
    avg_preprocess = sum(preprocess_speeds) / len(preprocess_speeds)
    avg_inf = sum(inf_speeds) / len(inf_speeds)
    avg_postprocess = sum(postprocess_speeds) / len(postprocess_speeds)

    # Mostrar los resultados
    print("Promedios de velocidades de procesamiento (ms):")
    print(f"Preprocess:      {avg_preprocess:.4f}")
    print(f"Inference:       {avg_inf:.4f}")
    print(f"Postprocess:     {avg_postprocess:.4f}")

if __name__ == "__main__":
    main()
