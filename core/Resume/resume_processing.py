import os
import zipfile
from pdf2image import convert_from_path
from docx2pdf import convert as docx2pdf_convert

def list_files(directory, extensions=['.pdf', '.docx']):
    """Lister les fichiers PDF et DOCX dans un dossier donné."""
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(tuple(extensions))]

def pdf_to_images(pdf_path, output_folder):
    """Convertir un fichier PDF en images et les enregistrer dans un dossier."""
    pages = convert_from_path(pdf_path)
    for i, page in enumerate(pages):
        page.save(f"{output_folder}/{os.path.basename(pdf_path)}_page_{i+1}.png", "PNG")

def convert_docx_to_pdf(docx_path, output_folder):
    """Convertir un fichier DOCX en PDF et enregistrer le fichier PDF généré."""
    pdf_path = f"{output_folder}/{os.path.basename(docx_path).replace('.docx', '.pdf')}"
    docx2pdf_convert(docx_path, pdf_path)
    return pdf_path

def docx_to_images(docx_path, output_folder):
    """Convertir un fichier DOCX en images via PDF et les enregistrer dans un dossier."""
    pdf_path = convert_docx_to_pdf(docx_path, output_folder)
    pdf_to_images(pdf_path, output_folder)
    os.remove(pdf_path)  # Supprimer le fichier PDF temporaire une fois terminé

def extract_zip(file_path, extract_to):
    """Extraire un fichier ZIP vers un répertoire."""
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def process_uploaded_files(files, output_folder):
    """Traiter les fichiers envoyés, y compris les fichiers ZIP, PDF, et DOCX."""
    os.makedirs(output_folder, exist_ok=True)
    
    for file in files:
        file_path = os.path.join(output_folder, file.name)
        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        # Si le fichier est un ZIP, décompresser et traiter les fichiers extraits
        if file.name.lower().endswith('.zip'):
            extract_zip(file_path, output_folder)
            os.remove(file_path)  # Supprimer le fichier ZIP après extraction
            
            # Traiter les fichiers décompressés
            extracted_files = [os.path.join(output_folder, f) for f in os.listdir(output_folder)]
            for extracted_file in extracted_files:
                if extracted_file.lower().endswith('.pdf'):
                    pdf_to_images(extracted_file, output_folder)
                elif extracted_file.lower().endswith(('.doc', '.docx')):
                    docx_to_images(extracted_file, output_folder)

        # Traiter les fichiers PDF ou DOCX envoyés directement
        elif file.name.lower().endswith('.pdf'):
            pdf_to_images(file_path, output_folder)
        elif file.name.lower().endswith(('.doc', '.docx')):
            docx_to_images(file_path, output_folder)
