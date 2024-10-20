from django.shortcuts import render
from .Resume.resume_processing import list_files, pdf_to_images, docx_to_images
from .Resume.yolo_model import load_yolo_model, get_bounding_boxes
from .Resume.text_processing import extract_text_from_image, process_texts
import os
from collections import defaultdict

# Chemin pour stocker les fichiers téléchargés et les images converties
OUTPUT_FOLDER = os.path.join('static', 'images')

# Charger les modèles YOLO
models = {
    'compétence': load_yolo_model('C:/Users/hp/Desktop/Competance_Data/mydata/model.pt'),
    'expérience': load_yolo_model('C:/Users/hp/Desktop/Experience_Data/mydata/model.pt'),
    'formation': load_yolo_model('C:/Users/hp/Desktop/Formation_Data/mydata/model.pt')
}

def home_view(request):
    return render(request, 'core/index.html')

def cv_view(request):
    if request.method == 'POST':
        # Gérer le téléchargement des fichiers par l'utilisateur
        uploaded_files = request.FILES.getlist('files')
        
        if not uploaded_files:
            return render(request, 'core/cv.html', {'error': 'Veuillez télécharger au moins un fichier.'})

        # Créer le dossier de sortie s'il n'existe pas
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        # Sauvegarder les fichiers et les convertir en images
        for file in uploaded_files:
            file_path = os.path.join(OUTPUT_FOLDER, file.name)
            with open(file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)

            if file.name.lower().endswith('.pdf'):
                pdf_to_images(file_path, OUTPUT_FOLDER)
            elif file.name.lower().endswith('.docx'):
                docx_to_images(file_path, OUTPUT_FOLDER)

        # Traitement des images converties
        compétence = defaultdict(list)
        expérience = defaultdict(list)
        formation = defaultdict(list)

        image_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        for image_name in image_files:
            image_path = os.path.join(OUTPUT_FOLDER, image_name)
            base_name = image_name.split('_page_')[0]  # Extraire le nom de base sans le suffixe de page

            for model_name, model in models.items():
                boxes = get_bounding_boxes(model, image_path)
                texts = extract_text_from_image(image_path, boxes)
                processed_texts = process_texts(texts)

                if model_name == 'compétence':
                    compétence[base_name].extend(processed_texts)
                elif model_name == 'expérience':
                    expérience[base_name].extend(processed_texts)
                elif model_name == 'formation':
                    formation[base_name].extend(processed_texts)

        # Envoyer les résultats au template
        context = {
            'compétence': dict(compétence),
            'expérience': dict(expérience),
            'formation': dict(formation)
        }
        return render(request, 'core/cv.html', context)

    return render(request, 'core/cv.html')
