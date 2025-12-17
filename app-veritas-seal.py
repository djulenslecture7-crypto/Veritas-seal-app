import streamlit as st
import hashlib
import gspread
from datetime import datetime
import pandas as pd

# --- PARAMÈTRES DE LA FEUILLE DE CALCUL ---
# IMPORTANT : Assurez-vous que les colonnes A1, B1, C1 sont Hash_SHA256, Nom_du_Fichier, Horodatage_Creation
NOM_FEUILLE_GOOGLE = "Veritas_Seal_Ancrage_MVP"
CLE_JSON_FILENAME = "keys.json"

# --- FONCTION DE CONNEXION À GOOGLE SHEETS (Mise en cache) ---
@st.cache_resource
def get_google_sheet_client():
    """
    Tente de se connecter au client gspread une seule fois
    en utilisant les clés du Compte de Service.
    """
    try:
        # Authentification et connexion au client gspread
        client = gspread.service_account(filename=CLE_JSON_FILENAME)
        return client
    except Exception as e:
        # Affiche l'erreur si la connexion échoue (ex: fichier keys.json manquant ou invalide)
        st.error(f"Erreur de connexion à Google Sheets. Vérifiez {CLE_JSON_FILENAME} et les permissions. Détails : {e}")
        return None

# --- FONCTION D'ANCRAGE DU SCEAU ---
def enregistrer_sceau_sheets(hash_sceau, nom_fichier):
    """
    Enregistre le sceau (hash) et le nom du fichier dans Google Sheets.
    """
    client = get_google_sheet_client()
    if client is None:
        return False # Échec de la connexion

    try:
        # Ouvrir la feuille de calcul par son nom
        sheet = client.open(NOM_FEUILLE_GOOGLE).sheet1 

        # Créer la ligne de données
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # L'ordre des données doit correspondre à l'ordre des colonnes dans Sheets (A, B, C)
        nouvelle_ligne = [hash_sceau, nom_fichier, now] 

        # Ajouter la ligne à la feuille
        sheet.append_row(nouvelle_ligne)

        return True # Succès de l'enregistrement

    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"Erreur: La feuille de calcul '{NOM_FEUILLE_GOOGLE}' est introuvable. Vérifiez le nom.")
        return False
    except gspread.exceptions.APIError as e:
        st.error(f"Erreur d'API: Vérifiez que le robot a le rôle 'Éditeur' pour la feuille. Détails: {e}")
        return False
    except Exception as e:
        st.error(f"Erreur imprévue lors de l'enregistrement: {e}")
        return False

# --- FONCTION PRINCIPALE DE L'APPLICATION STREAMLIT ---

st.set_page_config(layout="wide", page_title="Veritas Seal - Sceau Numérique")

# Titre
st.title("🛡️ Veritas Seal : Sceau Numérique Inaltérable")
st.markdown("---")

# Création de deux colonnes pour une meilleure lisibilité
col1, col2 = st.columns(2)

# =========================================================================
# COLONNE 1 : Créer le Sceau Numérique
# =========================================================================
with col1:
    st.header("1. Créer le Sceau Numérique 🖋️")
    st.info("Téléchargez votre fichier original pour générer son sceau SHA-256 unique et l'ancrer de manière permanente.")

    uploaded_file = st.file_uploader("Télécharger le fichier à sceller", type=None, key="create_uploader")

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_name = uploaded_file.name

        # 1. Calculer le Hash
        hash_object = hashlib.sha256()
        hash_object.update(file_bytes)
        hash_sceau = hash_object.hexdigest()

        st.success(f"**Sceau (Hash SHA-256) créé pour :** {file_name}")
        st.code(hash_sceau, language="text")

        # 2. Bouton d'Ancrage
        if st.button("Ancrer le Sceau (Sauvegarde Permanente)"):
            with st.spinner("Ancrage en cours... Veuillez patienter."):
                if enregistrer_sceau_sheets(hash_sceau, file_name):
                    st.success("🎉 Sceau ancré avec succès dans la base de données Google Sheets ! La preuve est enregistrée.")
                else:
                    st.error("Échec de l'ancrage. Veuillez vérifier les logs d'erreurs ci-dessus.")


# =========================================================================
# COLONNE 2 : Vérifier l'Authenticité
# =========================================================================
with col2:
    st.header("2. Vérifier l'Authenticité 🔍")
    st.warning("Collez le hash original (le sceau) pour vérifier si le fichier actuel a été altéré.")

    hash_original = st.text_input("Coller le Sceau (Hash) Original", key="original_hash")
    uploaded_file_check = st.file_uploader("Télécharger le fichier à vérifier", type=None, key="check_uploader")

    if st.button("Lancer la Vérification") and hash_original and uploaded_file_check is not None:
        file_bytes_check = uploaded_file_check.getvalue()

        # Calculer le Hash du fichier à vérifier
        hash_object_check = hashlib.sha256()
        hash_object_check.update(file_bytes_check)
        hash_actuel = hash_object_check.hexdigest() 
        # Comparaison
        if hash_actuel.lower() == hash_original.strip().lower():
            st.success("✅ AUTHENTIQUE ! Le fichier n'a pas été altéré depuis son scellement.")
        else:
            st.error("❌ MODIFIÉ / NON-SCELLE. Le hash ne correspond pas au sceau original. Le fichier a été altéré ou n'est pas le bon.")
            st.markdown(f"**Hash vérifié :** `{hash_actuel}`")
            st.markdown(f"**Hash attendu :** `{hash_original}`")
