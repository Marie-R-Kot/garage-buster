import requests
import io
from PIL import Image
from ultralytics import YOLO
from pathlib import Path
from clients.map_manager import get_world_coord
from clients.map_manager import get_url

def model_answer(image_url):
    response = requests.get(image_url)
    image = Image.open(io.BytesIO(response.content))
        
    if response.status_code != 200:
        return None
    
    # model_path = 'model/runs/detect'
    # model = YOLO(f'{model_path}/train/weights/best.pt')
    
    base_dir = Path(__file__).parent.parent
    model_path = base_dir / 'model' / 'best.pt'
    
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


def get_coords_from_model(center_coords):
    image_url = get_url(center_coords)
    
    garages_coords_list = model_answer(image_url)
    if not garages_coords_list:
        return None
    
    garage_coords = []
    
    for coords in garages_coords_list:
        map_coord = get_world_coord(coords, center_coords)
        garage_coords.append(map_coord)
    
    return garage_coords