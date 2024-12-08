from app.services.segmentation import resize_image, get_yolov5_1, get_yolov5_2
from PIL import Image
from PIL import Image
from io import BytesIO
import numpy as np
import cv2
import logging

# Configuración básica del logging
logging.basicConfig(level=logging.DEBUG)  # Establece el nivel de logging

# Cargar el modelo YOLOv5
model1 = get_yolov5_1()
model2 = get_yolov5_2()

# Función para procesar la imagen, detectar narices y dibujar las cajas
def detect_nose_to_dict(binary_image):
    input_image = resize_image(binary_image)
    results = model2(input_image)
    df = results.pandas().xyxy[0]
    if df.empty:
        results = model1(input_image)
        df = results.pandas().xyxy[0]
    # df to dict
    detect_res = df.to_dict(orient="records")
    logging.debug("deteeeeeeect "+ str(detect_res))
    return {"result": detect_res}

def crop_nose(img, coords: dict):
    #img = Image.open(BytesIO(img))
    coords = coords["result"][0]
    print("COOORDS", coords)
    xmin, ymin, xmax, ymax = (
        int(coords["xmin"]),
        int(coords["ymin"]),
        int(coords["xmax"]),
        int(coords["ymax"])
    )
    # Decodificar la imagen desde bytes a un objeto PIL
    img = Image.open(BytesIO(img))
    print("IMAGE", img)

    # Verificar que las coordenadas estén dentro de los límites de la imagen
    img_width, img_height = img.size
    xmin = max(0, min(xmin, img_width - 1))
    ymin = max(0, min(ymin, img_height - 1))
    xmax = max(0, min(xmax, img_width))
    ymax = max(0, min(ymax, img_height))

    print(f"Recortando con las coordenadas: xmin={xmin}, ymin={ymin}, xmax={xmax}, ymax={ymax}")

    # Realizar el recorte
    cropped_img = img.crop((xmin, ymin, xmax, ymax))
    img_crop = np.array(cropped_img)
    print("cropped_img", cropped_img)

    # Convertir la imagen de RGB (formato PIL) a BGR (formato OpenCV)
    img_crop = cv2.cvtColor(img_crop, cv2.COLOR_RGB2BGR)

    return img_crop


# def detect_nose_to_image(binary_image:bytes):
#     input_image = get_image_from_bytes(binary_image)
#     results = model1(input_image)
#     df = results.pandas().xyxy[0]
#     if df.empty:
#         results = model2(input_image)
#     results.render()  # updates results.ims with boxes and labels
#     for img in results.ims:
#         bytes_io = io.BytesIO()
#         img_base64 = Image.fromarray(img)
#         img_base64.save(bytes_io, format="jpeg")
#     return bytes_io