import time
import json
from ultralytics import YOLO

test_dataset_path = "/ultralytics/proyecto_grado_v2/proyecto_grado_sergio/jetson_testing/dataset_test/data.yaml"  # Ruta al archivo YAML del dataset de testeo
test_data = "/ultralytics/proyecto_grado_v2/proyecto_grado_sergio/jetson_testing/dataset_test/test/images"  # Directorio de imágenes de testeo
output_file = "results/evaluation_predict_results_fp16.json"  # Nombre del archivo para guardar los resultados


# Load the exported TensorRT model
trt_model = YOLO("/ultralytics/proyecto_grado_v2/proyecto_grado_sergio/jetson_testing/jetson_tensorrt_testing/yolov8n/models/yolov8n_finetuned_fp16.engine")

# Medir tiempo de inferencia
print("\nRealizando inferencia en todo el dataset de testeo...")

# Realizar inferencia sobre todas las imágenes del dataset de testeo
predictions = trt_model.predict(source=test_data, device=0, save=False)  # Cambia save a True si deseas guardar resultados

# Velocidades
total_inf_speeds = 0
total_pre_speeds = 0
total_pos_speeds = 0
for i in range(len(predictions)):
    print(predictions[i].speed)
    total_inf_speeds = total_inf_speeds + predictions[i].speed['inference']
    total_pre_speeds = total_pre_speeds + predictions[i].speed['preprocess']
    total_pos_speeds = total_pos_speeds + predictions[i].speed['postprocess']


avg_inf_speeds = total_inf_speeds / len(predictions)
avg_pre_speeds = total_pre_speeds / len(predictions)
avg_pos_speeds = total_pos_speeds / len(predictions)
print(avg_inf_speeds)
print(avg_pos_speeds)
print(avg_pre_speeds)



# Crear un diccionario para almacenar los resultados

run_results = {
    "model_name": "yolov8n_tensorrt_fp16",
    "results": {
        "avg_preprocess_speed": avg_pre_speeds,
        "avg_inf_speed": avg_inf_speeds,
        "avg_postprocess_speed": avg_pos_speeds
    }
}


# Leer el archivo JSON existente o crear uno nuevo
try:
    with open(output_file, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    data = []

# Agregar los resultados de la ejecución actual
data.append(run_results)

# Guardar los resultados actualizados en el archivo JSON
with open(output_file, "w") as f:
    json.dump(data, f, indent=4)

