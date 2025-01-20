import json

def main():
    filename = "evaluation_val_results.json"

    with open(filename, "r") as file:
        data = json.load(file)

    precisions = []
    recalls = []
    map_50_values = []
    map_50_95_values = []

    for run in data:
        results = run["results"]
        precisions.append(results["precision"])
        recalls.append(results["recall"])
        map_50_values.append(results["map_50"])
        map_50_95_values.append(results["map_50_95"])

    avg_precision = sum(precisions) / len(precisions)
    avg_recall = sum(recalls) / len(recalls)
    avg_map_50 = sum(map_50_values) / len(map_50_values)
    avg_map_50_95 = sum(map_50_95_values) / len(map_50_95_values)

    print("Promedios de las métricas:")
    print(f"Precision:  {avg_precision:.4f}")
    print(f"Recall:     {avg_recall:.4f}")
    print(f"mAP@0.50:   {avg_map_50:.4f}")
    print(f"mAP@0.50:0.95: {avg_map_50_95:.4f}")

if __name__ == "__main__":
    main()
