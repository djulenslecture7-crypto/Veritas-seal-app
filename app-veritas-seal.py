import streamlit as st
import hashlib
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- CONFIGURATION GOOGLE SHEETS ---
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# ICI : Tes clés que tu as déjà configurées (ne change rien à tes valeurs !)
creds_dict = {
    "# Connexion sécurisée via les Secrets de Streamlit
creds_dict = st.secrets["gcp_service_account"]}


# Connexion à la base de données
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
client = gspread.authorize(creds)
# [span_0](start_span)Nom exact de ton fichier Google Sheets[span_0](end_span)
sheet = client.open("Veritas_Seal_Ancrage_MVP").sheet1

# --- FONCTIONS TECHNIQUES ---
def calculate_hash(file):
    sha256_hash = hashlib.sha256()
    for byte_block in iter(lambda: file.read(4096), b""):
        sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# --- INTERFACE UTILISATEUR ---
st.set_page_config(page_title="Veritas Seal", page_icon="🛡️")
st.title("🛡️ Veritas Seal : Certification de Documents")

# Création des deux onglets
tab1, tab2 = st.tabs(["🔍 Vérifier un document (Public)", "✍️ Sceller un document (Admin)"])

# --- ONGLET 1 : VÉRIFICATION (POUR TOUT LE MONDE) ---
with tab1:
    st.header("Vérification d'authenticité")
    st.write("Déposez un fichier pour vérifier s'il est certifié dans notre base de données.")
    
    file_to_check = st.file_uploader("Choisir un fichier à vérifier", key="check")
    
    if file_to_check is not None:
        file_hash = calculate_hash(file_to_check)
        st.info(f"Empreinte calculée : `{file_hash}`")
        
        # [span_1](start_span)Recherche dans Google Sheets[span_1](end_span)
        data = sheet.get_all_records()
        match = next((item for item in data if item["Hash_SHA256"] == file_hash), None)
        
        if match:
            st.success(f"✅ DOCUMENT AUTHENTIQUE !")
            st.write(f"**Nom d'origine :** {match['Nom_du_Fichier']}")
            st.write(f"**Date de scellage :** {match['Horodatage_Creation']}")
        else:
            st.error("❌ DOCUMENT NON RECONNU ou MODIFIÉ.")
            st.warning("Ce document n'existe pas dans notre registre officiel.")

# --- ONGLET 2 : ADMINISTRATION (PROTÉGÉ) ---
with tab2:
    st.header("Espace Admin")
    admin_code = st.text_input("Entrez le code administrateur", type="password")
    
    if admin_code == "1234":  # Change "1234" par ton code secret
        st.success("Accès autorisé")
        file_to_seal = st.file_uploader("Document à certifier", key="seal")
        
        if file_to_seal is not None:
            if st.button("Ancrer le document"):
                new_hash = calculate_hash(file_to_seal)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # [span_2](start_span)Ajout dans Google Sheets[span_2](end_span)
                sheet.append_row([new_hash, file_to_seal.name, timestamp])
                st.balloons()
                st.success("Document certifié avec succès !")
    elif admin_code != "":
        st.error("Code incorrect")


