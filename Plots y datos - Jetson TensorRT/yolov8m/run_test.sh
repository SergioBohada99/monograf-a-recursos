#!/bin/bash

# Nombre del script de Python
script_python_predict_32="yolov8m_test_predict_fp32.py"
script_python_val_32="yolov8m_test_val_fp32.py"
script_python_predict_16="yolov8m_test_predict_fp16.py"
script_python_val_16="yolov8m_test_val_fp16.py"


# Número de veces que se ejecutará
num_ejecuciones=10

# Bucle para ejecutar el script el número de veces especificado
for i in $(seq 1 $num_ejecuciones); do
  echo "Ejecutando el script $script_python_predict_32 por la vez $i"
  python3 $script_python_predict_32
  echo "Ejecutando el script $script_python_val_32 por la vez $i"
  python3 $script_python_val_32
  echo "Ejecutando el script $script_python_predict_16 por la vez $i"
  python3 $script_python_predict_16
  echo "Ejecutando el script $script_python_val_16 por la vez $i"
  python3 $script_python_val_16
done