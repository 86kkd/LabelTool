import json
import os.path

import numpy as np
import os


def save_as_json(points, label, shape_type, imgHeight, imgWidth, filePath):
    name, ext = os.path.splitext(filePath)
    filename = filePath.split("/")[-1]
    if type(points) == np.ndarray:
        points =points.tolist()
        #points = {'points': points}
    shape = {'label': label,
             'points': points,
             'shape_type': shape_type}
    shapes = [shape]
    jsonFile = {'shapes': shapes,
                'imagePath': filename,
                'imageData': None,
                'imageHight': imgHeight,
                'imageWidth': imgWidth}

    with open(f'{name}.json', 'w') as file:
        json.dump(jsonFile, file,indent=2,ensure_ascii=False)
        print(f"save to {name}.json")


if __name__ == '__main__':
    """test function"""
    points = np.ndarray([4, 2])
    save_as_json(points, 'ore_port', 'polygon', 1200, 1920, './image.jpg')
    print(points.shape)
