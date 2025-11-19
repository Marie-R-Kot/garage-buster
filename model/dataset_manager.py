import os
import requests
#import json
import yaml
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split


class MapElement():
    
    def __init__(self, data, tag):
        self.coords = ''.join(str(data['coords']).split(' '))
        self.one_of_garage_coords = ''.join(str(data['coords_garage']).split(' '))
        self.target = 1 if data['target'] == 'да' else 0
        self.state = None
        self.tag = tag + 1
        self.gis_url = "https://static.maps.2gis.com/1.0?"
           
    def get_map_url(self, size, zoom):
        return f"{self.gis_url}s={size}x{size}@2x&z={zoom}&c={self.coords}"
    
    def download_map(self, folder, size, zoom):
        response = requests.get(self.get_map_url(size, zoom))
        if response.status_code == 200:
            try:
                with open(f'{folder}/{self.state}/{self.tag}.png', 'wb') as f:
                    f.write(response.content)
                    return True
            except FileNotFoundError:
                Path(f'{folder}/{self.state}').mkdir(parents=True, exist_ok=True)
                with open(f'{folder}/{self.state}/{self.tag}.png', 'wb') as f:
                    f.write(response.content)
                    return True
        else:
            return False



class MapManager():
    
    def __init__(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as file:
            self.config = yaml.safe_load(file)
            
        self.data_pd = pd.read_csv(self.config['coor_file_name'])
        self.data = {}
        for i in range(len(self.data_pd)):
            self.data[i+1] = MapElement(self.data_pd.iloc[i], i)
        
    def get_url_file(self):
        with open(self.config['url_file_name'], 'w+') as file:
            for key in self.data.keys():
                url = self.data[key].get_map_url(self.config['size'], self.config['zoom'])
                file.write(f"{url}\n")
                
        return True
        
    def download_maps(self): 
        for key in self.data.keys():
            self.data[key].download_map(f"{self.config['main_folder']}/images",
                                        self.config['size'],
                                        self.config['zoom'])
            
    def label_split(self):
        for key, value in self.data.items():
            with open(f"{self.config['label_folder']}/{key}.txt", 'r') as file:
                content = file.read()
            Path(f"{self.config['main_folder']}/labels/{value.state}").mkdir(parents=True, exist_ok=True)
            with open(f"{self.config['main_folder']}/labels/{value.state}/{key}.txt", 'w') as file:
                file.write(content)
                    
    @property
    def targets(self):
        targets = []
        for value in self.data.values():
            targets.append(value.target)
        
        return targets
    
    def data_split(self):
        train_idx, val_idx = train_test_split(
            range(len(self.targets)),
            test_size=0.2,
            stratify=self.targets,
            random_state=42
        )
        
        for idx in train_idx:
            self.data[idx+1].state = 'train'

        for idx in val_idx:
            self.data[idx+1].state = 'valid'
        
        return len(train_idx), len(val_idx)
    
    def create_dataset_yaml(self):
        current_dir = os.getcwd()  # текущая папка
        dataset_dir = os.path.join(current_dir, 'dataset')
        
        config = {
            'path': dataset_dir,
            'train': 'images/train',
            'val': 'images/valid', 
            'nc': 1,
            'names': ['garage'],
            'small_object_ratio': 0.05  
        }
        
        yaml_path = os.path.join(current_dir, 'dataset.yaml')
        with open('dataset.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        return True                         
                
if __name__ == "__main__":
    work_map = MapManager('model\config.yaml')
    work_map.get_url_file()
    t, v = work_map.data_split()
    #work_map.download_maps()
    #work_map.label_split()
    
    p = work_map.create_dataset_yaml()