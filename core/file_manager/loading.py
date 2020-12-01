import json
import torch


def load_json(json_path):
    with open(json_path, 'r') as j:
        json_dict = json.load(j)

    return json_dict


def load_object(filepath):

    return torch.load(filepath)