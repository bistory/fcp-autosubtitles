import xml.etree.ElementTree as ET
import sys
from fractions import Fraction

def convert_timecode_to_seconds(timecode):
    """
    Convertit un timecode (en secondes ou fraction, par ex. '208900/2500s' ou '5s') en secondes décimales.
    """
    try:
        if "s" in timecode:
            timecode = timecode.replace("s", "")  # Retirer le 's' final
        if "/" in timecode:
            # Si le timecode est une fraction (par ex. '208900/2500')
            return float(Fraction(timecode))
        else:
            # Si c'est un nombre entier (par ex. '5')
            return float(timecode)
    except ValueError:
        raise ValueError(f"Impossible de convertir le timecode : {timecode}")

def extract_chapters_from_ref_clips(fcpxml_file):
    try:
        # Charger le fichier FCPXML
        tree = ET.parse(fcpxml_file)
        root = tree.getroot()

        # Trouver les balises <ref-clip> avec les attributs "offset" et "name"
        chapters = []
        for ref_clip in root.findall(".//ref-clip"):
            offset = ref_clip.get("offset")  # Timecode de début
            name = ref_clip.get("name")     # Nom du chapitre
            
            if offset and name:
                try:
                    # Extraire la troisième série de chiffres
                    timecode_parts = offset.split("/")  # Séparer la fraction
                    if len(timecode_parts) == 2:
                        # Calculer les secondes en tenant compte de la fraction
                        seconds = convert_timecode_to_seconds(offset)

                        # Convertir en format YouTube (mm:ss)
                        minutes = int(seconds // 60)
                        secs = int(seconds % 60)
                        formatted_time = f"{minutes:02}:{secs:02}"

                        # Ajouter le chapitre
                        chapters.append(f"{formatted_time} {name}")
                    else:
                        print(f"Attention : Timecode mal formé (pas une fraction) pour '{name}': {offset}")
                except Exception as e:
                    print(f"Erreur lors de l'extraction du timecode pour '{name}': {e}")
        
        return chapters

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{fcpxml_file}' est introuvable.")
        return []
    except ET.ParseError:
        print(f"Erreur : Le fichier '{fcpxml_file}' n'est pas un fichier FCPXML valide.")
        return []
    except ValueError as e:
        print(f"Erreur lors de la conversion du timecode : {e}")
        return []
    except Exception as e:
        print(f"Erreur lors de l'extraction des chapitres : {e}")
        return []

if __name__ == "__main__":
    # Vérifier si un argument a été passé
    if len(sys.argv) < 2:
        print("Usage : python script.py <fichier.fcpxml>")
        sys.exit(1)

    # Récupérer le fichier FCPXML passé en argument
    fcpxml_file = sys.argv[1]
    chapters = extract_chapters_from_ref_clips(fcpxml_file)

    if chapters:
        print("Chapitres générés pour YouTube :")
        for chapter in chapters:
            print(chapter)
    else:
        print("Aucun chapitre trouvé ou erreur lors du traitement.")

