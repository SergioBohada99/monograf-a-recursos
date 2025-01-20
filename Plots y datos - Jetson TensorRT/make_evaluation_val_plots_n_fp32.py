import matplotlib.pyplot as plt
import numpy as np

def plot_manual_metrics():
    """
    Ejemplo de código para graficar manualmente los valores de
    Precision, Recall, mAP@0.50 y mAP@0.50:0.95 (en porcentaje)
    de varios modelos, con 'zoom' en Y y la leyenda afuera.
    """

    # 1. Definir manualmente los datos (en porcentajes)
    model_names = ["Yolov8n", "Yolov9t", "Yolov10n", "Yolov11n"]
    avg_precision = [96.75, 97.94, 96.77, 97.26]
    avg_recall = [94.85, 95.14, 94.48, 95.34]
    avg_map50 = [97.84, 97.91, 97.87, 97.87]
    avg_map50_95 = [71.40, 71.57, 70.83, 70.91]

    # 2. Configuración para la gráfica de barras
    x = np.arange(len(model_names))
    width = 0.2  # Ancho de cada barra

    # Crear la figura y los ejes
    fig, ax = plt.subplots(figsize=(8, 5))

    # 3. Generar las barras
    p1 = ax.bar(x - 1.5*width, avg_precision,  width, label='Precision (%)')
    p2 = ax.bar(x - 0.5*width, avg_recall,     width, label='Recall (%)')
    p3 = ax.bar(x + 0.5*width, avg_map50,      width, label='mAP@0.50 (%)')
    p4 = ax.bar(x + 1.5*width, avg_map50_95,   width, label='mAP@0.50:0.95 (%)')

    # 4. Configurar las etiquetas del eje X y título
    ax.set_xticks(x)
    ax.set_xticklabels(model_names)
    ax.set_xlabel('Modelos')
    ax.set_ylabel('Porcentaje (%)')
    ax.set_title('Comparación de Métricas por Modelo - TensorRT - fp32')

    # --- Aquí hacemos zoom para resaltar el rango de interés ---
    # Por ejemplo, si sabemos que todos los valores están arriba de 70,
    # podemos iniciar el eje Y en 70. Ajusta según tus valores reales.
    ax.set_ylim([70, 100])  

    # 5. Mover la leyenda fuera y acomodarla para que no tape las barras
    #    Ajusta bbox_to_anchor y loc para posicionarla.
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1))

    # 6. Agregar los valores encima de las barras (opcional):
    for bars in [p1, p2, p3, p4]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # desplazamiento en la dirección Y
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_manual_metrics()
