#!/usr/bin/env python3
from main import launch_pipeline
from threading import Thread
from monitoring.logging_handler.logger import logger

# Códigos ANSI para colores
RESET = "\033[0m"
RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
BLUE = "\033[34m"

def launch_pipeline_thread(urls, pipeline_id):
    """
    Lanza una pipeline y monitorea si está corriendo.
    """
    try: 
        logger.info(f"INICIANDO PIPELINE {pipeline_id}...")
        launch_pipeline(urls)
        logger.info(f"PIPELINE {pipeline_id} FINALIZADO.")
    except Exception as e:
        logger.error(f"Error en launch pipeline: {e}")
        raise BaseException

if __name__ == "__main__":
    logger.info("Empezando sistema de monitoreo GuardIA")
    val = True
    while val:
        try:
            
            urls_pipeline_1 = {0: "rtsp://admin:3l3ctr0c4qu3t4$@10.30.21.62:554/Streaming/Channels/101"}
            urls_pipeline_2 = {1: "rtsp://admin:3l3ctr0c4qu3t4$@10.30.21.55:554/Streaming/Channels/101"}
            urls_pipeline_3 = {2: "rtsp://admin:3l3ctr0c4qu3t4$@10.30.21.57:554/Streaming/Channels/101"}
            urls_pipeline_4 = {3: "rtsp://admin:3l3ctr0c4qu3t4$@10.30.21.56:554/Streaming/Channels/101"}
            urls_pipeline_5 = {4: "rtsp://admin:3l3ctr0c4qu3t4$@10.30.21.58:554/Streaming/Channels/101"}
            

            # Paso 2: Lanzar el primer pipeline en un hilo separado
            thread_0 = Thread(target=launch_pipeline_thread, args=(urls_pipeline_1, 1))
            thread_0.start()

            # Paso 5: Lanzar el segundo pipeline en un hilo separado
            thread_1 = Thread(target=launch_pipeline_thread, args=(urls_pipeline_2, 2))
            thread_1.start()
            
            # Paso 5: Lanzar el segundo pipeline en un hilo separado
            thread_2 = Thread(target=launch_pipeline_thread, args=(urls_pipeline_3, 3))
            thread_2.start()
            
            # Paso 5: Lanzar el segundo pipeline en un hilo separado
            thread_3 = Thread(target=launch_pipeline_thread, args=(urls_pipeline_4, 4))
            thread_3.start()

            # Paso 5: Lanzar el segundo pipeline en un hilo separado
            thread_4 = Thread(target=launch_pipeline_thread, args=(urls_pipeline_5, 5))
            thread_4.start()



            # Esperar a que ambos pipelines terminen
            thread_0.join()
            thread_1.join()
            thread_2.join()
            thread_3.join()
            thread_4.join()

        except KeyboardInterrupt as e:
            logger.error(f"Sistema detenido desde el teclado.")
            val = False
        except BaseException as e:
            logger.error(f"Sistema detenido por un error: {e}")
            logger.error("Reiniciando Sitema")
    logger.info("Sistema finalizado con exito.")

