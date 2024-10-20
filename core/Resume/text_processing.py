import cv2
from PIL import Image
import pytesseract
import re

# Configurer le chemin vers l'exécutable Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path, boxes):
    """Extraire le texte des zones délimitées par les boîtes englobantes dans l'image."""
    image = cv2.imread(image_path)
    extracted_texts = []
    for (x_min, y_min, x_max, y_max) in boxes:
        roi = image[y_min:y_max, x_min:x_max]  # Extraire la région d'intérêt
        pil_img = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))  # Convertir en format PIL
        text = pytesseract.image_to_string(pil_img, lang='fra')  # Extraire le texte avec Tesseract
        extracted_texts.append(text)
    return extracted_texts

def process_texts(texts):
    """Nettoyer les textes extraits pour supprimer les espaces superflus."""
    processed_texts = []
    for text in texts:
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        processed_texts.append(cleaned_text)
    return processed_texts
