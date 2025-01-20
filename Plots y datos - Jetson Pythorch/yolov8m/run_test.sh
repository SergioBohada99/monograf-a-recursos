#!/bin/bash

# Nombre del script de Python
script_python_predict="yolov8m_test_predict.py"
script_python_val="yolov8m_test_val.py"


# Número de veces que se ejecutará
num_ejecuciones=10

# Bucle para ejecutar el script el número de veces especificado
for i in $(seq 1 $num_ejecuciones); do
  echo "Ejecutando el script $script_python_predict por la vez $i"
  python3 $script_python_predict
  echo "Ejecutando el script $script_python_val por la vez $i"
  python3 $script_python_val
done