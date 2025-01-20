from monitoring.logging_handler.logger import logger
import base64
import os
import httpx
import json
from utils.token_manager import TokenManager
import cv2
from dotenv import load_dotenv
import time
import datetime

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Inicializa el administrador de tokens que se encargará de la autenticación
token_manager = TokenManager()

last_sent_times = {}

def prepare_data(result):
    """
    Prepara los datos de la inferencia para ser enviados al servidor en formato JSON.
    
    Parameters:
        result (dict): Resultado de la inferencia, que incluye 'camera_id', 'timestamp' y 'frame'.
    
    Returns:
        str: Datos formateados en JSON listos para el envío al servidor.
    """
    # Codificar la imagen en formato JPEG y luego en Base64
    _, buffer = cv2.imencode('.jpg', result['frame'])
    image_base64 = base64.b64encode(buffer).decode('utf-8') 
    logger.info(f"Timestamp: {result['timestamp']}")
    timstamp = custom_date_to_epoch(result['timestamp'])
    logger.info(f"Timestamp convertido: {timstamp}")
    # Estructura de datos para el envío
    data = {
        'camera_id': result['camera_id'],
        'datealert': timstamp,
        'client_id': 1,
        'image_data': image_base64
    }
    return json.dumps(data)

def send_alert(result, max_retries=3, delay=0.5):
    """
    Envía una alerta al servidor con los datos de la inferencia en formato JSON.
    
    Parameters:
        result (dict): Resultado de la inferencia.
        max_retries (int): Número máximo de reintentos en caso de fallo al enviar la alerta.
        delay (int): Tiempo en segundos entre reintentos en caso de fallo.
    """
    headers = {
        'Authorization': f'Bearer {token_manager.get_access_token()}',  # Incluir el token de acceso en los headers
        'Content-Type': 'application/json'  # Especificar que el contenido es JSON
    }

    payload = prepare_data(result)  # Preparar el JSON a enviar
    url_alert = os.getenv("URL_INFERENCE")  # Obtener la URL del servidor de inferencias desde las variables de entorno
    if not url_alert:
        logger.error("URL_INFERENCE is not defined or is None.")
        return

    logger.info(f"Attempting to send alert for camera {result['camera_id']} to the server at {url_alert}.")

    attempt = 0

    while attempt < max_retries:
        try:
            # Realizar la solicitud POST al servidor
            response = httpx.post(url_alert, headers=headers, data=payload)
            
            if response.status_code == 200:
                logger.info(f"Alert for camera {result['camera_id']} sent successfully to {url_alert}. Status code: {response.status_code}. Server Response: {response.text}")
                return  # Si la solicitud fue exitosa, salir del bucle
            else:
                logger.error(f"Failed to send alert for camera {result['camera_id']}. Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            logger.error(f"Error sending alert for camera {result['camera_id']} (attempt {attempt + 1}): {str(e)}")

        attempt += 1
        time.sleep(delay)  # Esperar antes de reintentar

def should_send_alert(payload_id):
    """
    Verifica si han pasado al menos 2 minutos desde el último envío del payload con el mismo ID.
    """
    current_time = time.time()
    if payload_id in last_sent_times:
        if current_time - last_sent_times[payload_id] < 5:
            return False
    last_sent_times[payload_id] = current_time
    return True

def custom_date_to_epoch(date_str):
    """
    Convierte una fecha en formato YYYYMMDD_HHMMSS (por ejemplo, '20241230_085409')
    a un timestamp Unix en segundos (float).
    
    Parameters:
    date_str: Tiemstamp en formato YY/MM/DD/HH/MM/SS.
    
    Returns:
        timestamp: Timestamp en formato UNIX.
    """
    year = int(date_str[0:4])      # '2024'
    month = int(date_str[4:6])     # '12'
    day = int(date_str[6:8])       # '30'
    hour = int(date_str[9:11])     # '08'
    minute = int(date_str[11:13])  # '54'
    second = int(date_str[13:15])  # '09'
    
    dt = datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)
    
    timestamp = dt.timestamp()
    return timestamp