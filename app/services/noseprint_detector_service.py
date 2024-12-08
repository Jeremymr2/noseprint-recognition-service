import httpx
import cv2
import base64
from io import BytesIO

async def noseprint_detector_service(first_image, second_image):
    # Convierte las imágenes numpy a formato de archivo (JPEG)
    _, buffer_one = cv2.imencode('.jpg', first_image)
    _, buffer_two = cv2.imencode('.jpg', second_image)

    # Paso 2: Convertir la imagen a base64
    first_image = base64.b64encode(buffer_one).decode('utf-8')
    second_image = base64.b64encode(buffer_two).decode('utf-8')

    url = "http://localhost:8003/api/v1/predict"
    data = {"image_1": first_image, "image_2": second_image}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        response_json = response.json()  # Sin 'await', ya es un diccionario

        # Extraer el valor de 'result' en lugar de acceder a la lista anidada
        result_value = response_json.get('result')  # Accede a 'result' del diccionario
        return result_value
