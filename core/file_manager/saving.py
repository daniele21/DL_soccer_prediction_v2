import torch
import json
import pickle

from scripts.utils.utils import ensure_folder

def save_json(json_dict, filepath):
   
    with open(filepath, 'w') as j:
        json.dump(json_dict, j, indent=4)
        j.close()

    return

def save_str_file(content, filepath, mode='a'):
    
    with open(filepath, mode) as f:
        f.write(content)
        f.close()
        
    return


def save_model(model, filepath):
    
    save_object(model, filepath)
    # print(f'> Saving model at {filepath}')

    return filepath


def save_object(my_object, filepath):
    
    torch.save(my_object, filepath)
    # print(f'> Saving object at {filepath}')

    return filepath


