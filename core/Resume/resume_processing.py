import os
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
