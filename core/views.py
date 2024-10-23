from django.shortcuts import render
import openai
import re
from collections import defaultdict
from .Resume.resume_processing import list_files, pdf_to_images, docx_to_images
from .Resume.yolo_model import load_yolo_model, get_bounding_boxes
from .Resume.text_processing import extract_text_from_image, process_texts
import os
import zipfile
import os  # Pour la gestion des chemins de fichiers et des opérations sur les fichiers
import zipfile  # Pour gérer les fichiers ZIP
from collections import defaultdict  # Pour créer des dictionnaires avec des listes par défaut
from django.shortcuts import render  # Pour rendre les templates
from django.http import HttpResponse  # (Optionnel) Pour retourner des réponses HTTP

# Les importations pour les fonctions de traitement des fichiers et des images
from .Resume.resume_processing import list_files, pdf_to_images, docx_to_images
from .Resume.yolo_model import load_yolo_model, get_bounding_boxes
from .Resume.text_processing import extract_text_from_image, process_texts

# Importer OpenAI si tu utilises l'API OpenAI pour la comparaison des CVs
import openai
import re  # Pour la manipulation de chaînes de caractères et l'extraction de données avec regex

# Chemin pour stocker les fichiers téléchargés et les images converties
OUTPUT_FOLDER = os.path.join('static_Resume', 'DOC_images')

# Charger les modèles YOLO
models = {
    'compétence': load_yolo_model('C:/Users/hp/Desktop/Competance_Data/mydata/model.pt'),
    'expérience': load_yolo_model('C:/Users/hp/Desktop/Experience_Data/mydata/model.pt'),
    'formation': load_yolo_model('C:/Users/hp/Desktop/Formation_Data/mydata/model.pt')
}

def home_view(request):
    return render(request, 'core/index.html')

def process_uploaded_files(files):
    """Traiter les fichiers envoyés, y compris les fichiers ZIP."""
    # Définir le dossier de sortie pour les images
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    for file in files:
        file_path = os.path.join(OUTPUT_FOLDER, file.name)
        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        # Si le fichier est un ZIP, décompressez-le
        if file.name.lower().endswith('.zip'):
            extract_zip(file_path, OUTPUT_FOLDER)
            os.remove(file_path)  # Supprimer le fichier ZIP après extraction

            # Traiter les fichiers décompressés (PDF et DOCX)
            extracted_files = [os.path.join(OUTPUT_FOLDER, f) for f in os.listdir(OUTPUT_FOLDER)]
            for extracted_file in extracted_files:
                if extracted_file.lower().endswith('.pdf'):
                    pdf_to_images(extracted_file, OUTPUT_FOLDER)
                elif extracted_file.lower().endswith(('.doc', '.docx')):
                    docx_to_images(extracted_file, OUTPUT_FOLDER)

        # Traiter les fichiers PDF ou DOCX envoyés directement
        elif file.name.lower().endswith('.pdf'):
            pdf_to_images(file_path, OUTPUT_FOLDER)
        elif file.name.lower().endswith(('.doc', '.docx')):
            docx_to_images(file_path, OUTPUT_FOLDER)


def cv_view(request):
    if request.method == 'POST':
        # Récupérer l'offre d'emploi depuis le formulaire
        offre_emploi = request.POST.get('offre_emploi', '')

        if not offre_emploi:
            return render(request, 'core/cv.html', {'error': 'Veuillez saisir une offre d\'emploi.'})

        # Gérer le téléchargement des fichiers par l'utilisateur
        uploaded_files = request.FILES.getlist('files')
        
        if not uploaded_files:
            return render(request, 'core/cv.html', {'error': 'Veuillez télécharger au moins un fichier.'})

        # Traiter les fichiers envoyés
        process_uploaded_files(uploaded_files)

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

        # Classer les CVs en fonction de la similarité avec l'offre d'emploi
        results = rank_profiles(compétence, expérience, formation, offre_emploi)

        # Passer les résultats au template
        return render(request, 'core/cv.html', {'results': results})

    return render(request, 'core/cv.html')

# Fonction pour comparer les informations des CV avec l'offre d'emploi et les classer
def rank_profiles(compétence, expérience, formation, offre_emploi):
    # Configurer l'API OpenAI (utiliser ta propre clé ici)
    openai.api_key = "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"

    results = []

    for image, competences in compétence.items():
        formations = formation.get(image, [])
        expériences = expérience.get(image, [])

        competences_text = " | ".join(competences)
        formations_text = " | ".join(formations)
        expériences_text = " | ".join(expériences)

        prompt = (
            f"Comparer les informations suivantes avec l'offre d'emploi:\n\n"
            f"Compétences : {competences_text}\n"
            f"Formations : {formations_text}\n"
            f"Expériences : {expériences_text}\n\n"
            f"Offre d'emploi : {offre_emploi}\n\n"
            f"Donne une évaluation du taux de similarité et les pourcentages pour chaque catégorie (compétences, formations, expériences) et "
            f"fournis également le pourcentage final du profil par rapport à l'offre d'emploi."
        )

        # Envoyer la requête à l'API OpenAI et obtenir la réponse
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Ou "gpt-4" selon ton accès
            messages=[
                {"role": "system", "content": "Tu es un assistant utile."},
                {"role": "user", "content": prompt},
            ]
        )
        
        # Afficher les résultats dans la console pour chaque CV
        print(f"\nRésultats pour le CV {image} :")
        print(response['choices'][0]['message']['content'])

        # Extraire le pourcentage final de similarité à partir de la réponse
        final_percentage = extract_final_percentage(response['choices'][0]['message']['content'])
        results.append({
            'image': image,
            'score': final_percentage,
            'details': response['choices'][0]['message']['content']
        })

    # Trier les profils en fonction du pourcentage final (du plus élevé au plus bas)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results

# Fonction pour extraire le pourcentage final de similarité du texte de la réponse
def extract_final_percentage(response_text):
    match = re.search(r'(\d+)%', response_text)
    if match:
        return int(match.group(1))
    return 0
