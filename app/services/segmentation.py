import torch
from PIL import Image
import io
from pathlib import Path

model_path_1 = Path("./app/models/best_1.pt")
model_path_2 = Path("./app/models/best_2.pt")

def get_yolov5_1():
    # local best.pt
    model = torch.hub.load('./yolov5', 'custom', path=model_path_1, source='local', force_reload=True)  # local repo
    model.conf = 0.5
    return model

def get_yolov5_2():
    # local best.pt
    model = torch.hub.load('./yolov5', 'custom', path=model_path_2, source='local', force_reload=True)  # local repo
    model.conf = 0.5
    return model

def resize_image(binary_image, max_size=1024):
    input_image = Image.open(io.BytesIO(binary_image)).convert("RGB")
    width, height = input_image.size
    resize_factor = min(max_size / width, max_size / height)
    resized_image = input_image.resize(
        (
            int(input_image.width * resize_factor),
            int(input_image.height * resize_factor),
        )
    )
    return resized_image