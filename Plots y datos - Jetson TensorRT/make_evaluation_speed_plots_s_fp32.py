import matplotlib.pyplot as plt
import numpy as np
import os

def plot_inference_times():
    """
    Genera una gráfica de barras comparando los tiempos de Preprocesamiento,
    Inferencia y Postprocesamiento (en ms) de varios modelos,
    con estilo y leyenda a la derecha, de forma similar al otro script.
    """

    # 1. Definir manualmente los datos
    models = ['YOLOv8s', 'YOLOv9s', 'YOLOv10s', 'YOLOv11s']
    preprocess =  [2.1134, 2.1295, 2.1340, 2.1184]
    inference =   [13.6336, 19.0919, 14.589, 14.5153]
    postprocess = [4.2391, 4.4149, 1.6319, 4.3104]

    # 2. Configuración para la gráfica de barras
    x = np.arange(len(models))
    width = 0.2  # Ancho de cada barra

    # Crear figura y ejes con un tamaño similar
    fig, ax = plt.subplots(figsize=(8, 5))

    # 3. Generar las barras
    p1 = ax.bar(x - width,      preprocess,  width, label='Preprocess (ms)')
    p2 = ax.bar(x,              inference,   width, label='Inference (ms)')
    p3 = ax.bar(x + width,      postprocess, width, label='Postprocess (ms)')

    # 4. Configurar las etiquetas del eje X y título
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.set_xlabel('Modelos')
    ax.set_ylabel('Tiempo (ms)')
    ax.set_title('Comparación de Tiempos de Procesamiento por Modelo - TensorRT - fp32')

    # Ajustar el rango del eje Y si se desea "zoom"
    ax.set_ylim([0, 25])

    # 5. Mover la leyenda afuera (a la derecha), similar al otro gráfico
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1))

    # 6. Agregar los valores encima de las barras
    for bars in [p1, p2, p3]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # desplazamiento en la dirección Y
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)

    plt.tight_layout()

    # 7. Guardar la figura (opcional) en la misma ruta del script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    save_path = os.path.join(script_dir, "processing_times_comparison.png")
    plt.savefig(save_path, dpi=300)

    # 8. Mostrar la gráfica
    plt.show()

if __name__ == '__main__':
    plot_inference_times()
