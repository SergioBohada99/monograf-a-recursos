import time
import json
from ultralytics import YOLO

# Configuración: Cambia estos valores según tu configuración
model_path = "/ultralytics/proyecto_grado_v2/proyecto_grado_sergio/jetson_testing/jetson_tensorrt_testing/yolov8s/models/yolov8s_finetuned.pt"  # Ruta al modelo fine-tuned
test_dataset_path = "/ultralytics/proyecto_grado_v2/proyecto_grado_sergio/jetson_testing/dataset_test/data.yaml"  # Ruta al archivo YAML del dataset de testeo
test_data = "/ultralytics/proyecto_grado_v2/proyecto_grado_sergio/jetson_testing/dataset_test/test/images"  # Directorio de imágenes de testeo
output_file = "evaluation_results.json"  # Nombre del archivo para guardar los resultados


# Cargar el modelo
model = YOLO(model_path)

# Export the model to TensorRT
model.export(format="engine", dynamic=True, device=0)