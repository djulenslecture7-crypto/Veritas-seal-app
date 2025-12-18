import streamlit as st
import hashlib
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- CONFIGURATION SÉCURISÉE ---
# On récupère les clés depuis le coffre-fort "Secrets" de Streamlit
creds_dict = st.secrets["gcp_service_account"]

SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Connexion à Google Sheets
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
client = gspread.authorize(creds)
sheet = client.open("Veritas_Seal_Ancrage_MVP").sheet1

# --- FONCTION DE CALCUL DU HASH ---
def calculate_hash(file):
    sha256_hash = hashlib.sha256()
    for byte_block in iter(lambda: file.read(4096), b""):
        sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# --- INTERFACE ---
st.set_page_config(page_title="Veritas Seal", page_icon="🛡️")
st.title("🛡️ Veritas Seal : Certification de Documents")

# Création des onglets : Public et Admin
tab1, tab2 = st.tabs(["🔍 Vérifier un document (Public)", "✍️ Sceller un document (Admin)"])

# --- ONGLET PUBLIC : VÉRIFICATION ---
with tab1:
    st.header("Vérification d'authenticité")
    st.write("Déposez un fichier pour vérifier s'il est certifié.")
    
    file_to_check = st.file_uploader("Choisir un fichier", key="check")
    
    if file_to_check is not None:
        file_hash = calculate_hash(file_to_check)
        st.info(f"Empreinte (Hash) : `{file_hash}`")
        
        # On cherche dans le fichier Google Sheets
        data = sheet.get_all_records()
        match = next((item for item in data if item["Hash_SHA256"] == file_hash), None)
        
        if match:
            st.success("✅ DOCUMENT AUTHENTIQUE !")
            st.write(f"**Nom d'origine :** {match['Nom_du_Fichier']}")
            st.write(f"**Certifié le :** {match['Horodatage_Creation']}")
        else:
            st.error("❌ DOCUMENT NON RECONNU.")

# --- ONGLET PRIVÉ : ADMINISTRATION ---
with tab2:
    st.header("Espace Admin")
    # Remplace "1234" par ton code secret dans la ligne suivante si tu veux
    admin_code = st.text_input("Code secret", type="password")
    
    if admin_code == "1234":
        st.success("Accès Admin débloqué")
        file_to_seal = st.file_uploader("Document à sceller", key="seal")
        
        if file_to_seal is not None:
            if st.button("Ancrer définitivement"):
                new_hash = calculate_hash(file_to_seal)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Ajout direct dans ton Google Sheets
                sheet.append_row([new_hash, file_to_seal.name, timestamp])
                st.balloons()
                st.success("Le document est maintenant certifié !")
