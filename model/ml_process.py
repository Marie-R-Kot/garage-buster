import requests
import io
from PIL import Image
from ultralytics import YOLO
import os
from pathlib import Path

def model_staff(image_url):
    response = requests.get(image_url)
    image = Image.open(io.BytesIO(response.content))
        
    if response.status_code != 200:
        return None
    
    # model_path = 'model/runs/detect'
    # model = YOLO(f'{model_path}/train/weights/best.pt')
    
    base_dir = Path(__file__).parent.parent
    model_path = base_dir / 'model' / 'best.pt'
    
    # Проверяем существование файла
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at: {model_path}")
    
    model = YOLO(str(model_path))
    
    results = model(
        image,
        conf=0.25,
        iou=0.5,    
        imgsz=1280,    
        save=False,     
        save_txt=False,  
        show=False      
    )
    
    coords_list = []
    
    for box in results[0].boxes:
        x = box.xywhn[0][0]
        y = box.xywhn[0][1]
        coords_list.append([float(x), float(y)])
        
    return coords_list
