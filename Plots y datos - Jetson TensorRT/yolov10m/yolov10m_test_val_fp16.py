import time
import json
from ultralytics import YOLO

test_dataset_path = "/ultralytics/proyecto_grado_v2/proyecto_grado_sergio/jetson_testing/dataset_test/data.yaml"  # Ruta al archivo YAML del dataset de testeo
test_data = "/ultralytics/proyecto_grado_v2/proyecto_grado_sergio/jetson_testing/dataset_test/test/images"  # Directorio de imágenes de testeo
output_file = "results/evaluation_val_results_fp16.json"  # Nombre del archivo para guardar los resultados


# Load the exported TensorRT model
trt_model = YOLO("/ultralytics/proyecto_grado_v2/proyecto_grado_sergio/jetson_testing/jetson_tensorrt_testing/yolov10m/models/yolov10m_finetuned_fp16.engine")


# Evaluar el modelo en el conjunto de prueba
results = trt_model.val(data=test_dataset_path, split='test',verbose=True, device=0)  # 'val' indica evaluación

# Extraer métricas de evaluación
precision = results.box.mp  # Mean precision
recall = results.box.mr     # Mean recall
map_50 = results.box.map50  # Mean AP at IoU=0.5
map_50_95 = results.box.map  # Mean AP at IoU=0.5:0.95

# Velocidades
speed = results.speed  # Velocidades de preprocesamiento, inferencia y postprocesamiento
preprocess_speed = speed['preprocess']  # Preprocesamiento
inference_speed = speed['inference']  # Inferencia
postprocess_speed = speed['postprocess']  # Postprocesamiento


# Crear un diccionario para almacenar los resultados
run_results = {
    "model_name": "yolov10m_tensorrt_fp16",
    "results": {
        "precision": precision,
        "recall": recall,
        "map_50": map_50,
        "map_50_95": map_50_95,
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

