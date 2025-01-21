# Implementación de Tecnologías de Borde y Técnicas de Deep Learning para Vigilancia en Áreas Remotas con Canales de Comunicación Limitados

## Resumen
La necesidad de salvaguardar a las personas, los espacios y las ciudades ha sido un factor determinante para el desarrollo de sistemas de videovigilancia basados en modelos de aprendizaje profundo cada vez más robustos e inteligentes. Sin embargo, en contextos como el colombiano, caracterizado por limitaciones significativas en su infraestructura de telecomunicaciones a nivel nacional, esta tarea enfrenta diversos desafíos.

En respuesta a esta problemática, el presente trabajo aborda la investigación, prueba y evaluación práctica de tecnologías y técnicas óptimas para la implementación de modelos de aprendizaje profundo en dispositivos de borde. Para ello, se establecieron y aplicaron lineamientos derivados de la literatura actual, los cuales fueron evaluados en un entorno práctico.

Se llevó a cabo el entrenamiento de distintos modelos de aprendizaje profundo utilizando un conjunto de imágenes extraídas de datos diseñados específicamente para el dominio del problema. Posteriormente, se realizaron pruebas de los modelos mediante el diseño y desarrollo de un sistema de borde en un entorno práctico, cuyos resultados fueron contrastados con los de un sistema en producción actualmente activo.

**Palabras clave**: Videovigilancia, Aprendizaje Profundo, Dispositivos de borde.

---

## Abstract
The need to safeguard people, spaces, and cities has been a key driver for the development of video surveillance systems based on increasingly robust and intelligent deep learning models. However, in contexts like Colombia, characterized by significant limitations in its national telecommunications infrastructure, this task faces various challenges.

In response to this issue, the present work focuses on the research, testing, and practical evaluation of optimal technologies and techniques for implementing deep learning models on edge devices. To this end, guidelines derived from the current literature were established and applied, which were then assessed in a practical setting.

The training of different deep learning models was carried out using a dataset of images specifically designed for the problem domain. Subsequently, the models were tested through the design and development of an edge system in a practical environment, and the results were compared with those from a currently active production system.

**Keywords**: Video Surveillance, Deep Learning, Edge devices.

---

## Estructura del Repositorio

- **`Datos experimentales`**: Resultados de los experimentos realizados durante la investigación.
- **`Pesos entrenados`**: Modelos preentrenados desde `yolov8n` hasta `yolov11m`, ajustados con el dataset de esta investigación, además de los pesos preentrenados con COCO para enfoques de *transfer learning*.
- **`Plots` y `Datos`**: Gráficas y análisis de rendimiento y desempeño de cada experimento realizado, junto con el código correspondiente.
- **`Sistema de borde`**: Implementación funcional del sistema diseñado para pruebas y evaluación de los modelos.
  - **Nota**: Para usar este sistema, es necesario instalar [NVIDIA DeepStream](https://developer.nvidia.com/deepstream-sdk) y los bindings de Python.

---

## Ejemplo en Acción

A continuación, se muestran ejemplos del sistema en funcionamiento:

![Detección 1](https://raw.githubusercontent.com/SergioBohada99/monograf-a-recursos/main/Datos%20experimentales/Detections_jetson/frame_appsink_6630_20241218_094013.jpg)

![Detección 2](https://raw.githubusercontent.com/SergioBohada99/monograf-a-recursos/main/Datos%20experimentales/Detections_jetson/frame_appsink_1571_20241218_094855.jpg)

---

## Cita en LaTeX

Si deseas citar este documento en un trabajo académico, usa la siguiente referencia en formato BibTeX:

```bibtex
@misc{bohada2025,
  title = {Implementación de Tecnologías de Borde y Técnicas de Deep Learning para Vigilancia en Áreas Remotas con Canales de Comunicación Limitados},
  author = {Sergio David Bohada Vargas},
  year = {2025},
  institution = {Universidad Distrital Francisco José de Caldas},
  type = {Monografía},
  director = {Mg. John Freddy Parra Peña},
  keywords = {Videovigilancia, Aprendizaje Profundo, Dispositivos de borde},
  url = {https://github.com/SergioBohada99/monograf-a-recursos}
}
