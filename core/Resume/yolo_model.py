from ultralytics import YOLO

def load_yolo_model(model_path):
    """Charger le modèle YOLO à partir du chemin spécifié."""
    return YOLO(model_path)

def get_bounding_boxes(model, image_path):
    """Obtenir les boîtes englobantes prédites par le modèle YOLO."""
    results = model(image_path)
    boxes = []
    for result in results:
        for bbox in result.boxes.xyxy:
            x_min, y_min, x_max, y_max = map(int, bbox.tolist())
            boxes.append((x_min, y_min, x_max, y_max))
    return boxes
