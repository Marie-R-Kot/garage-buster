import requests
import io
#from ultralytics import YOLO
from PIL import Image
import sys
import subprocess

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from ultralytics import YOLO
except ImportError:
    install_package("opencv-python-headless")
    install_package("ultralytics")
    from ultralytics import YOLO
    
def model_staff(image_url):
    response = requests.get(image_url)
    image = Image.open(io.BytesIO(response.content))
        
    if response.status_code != 200:
        return None
    
    # model_path = 'model/runs/detect'
    # model = YOLO(f'{model_path}/train/weights/best.pt')
    
    model = YOLO('model/best.pt')
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
