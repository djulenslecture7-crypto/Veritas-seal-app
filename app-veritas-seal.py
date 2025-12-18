import streamlit as st
import hashlib
import pandas as pd
from datetime import datetime, timezone
import uuid
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURATION SÉCURISÉE ---
CODE_SECRET = "Lumie2025"

# Interface de verrouillage (Backdoor)
st.sidebar.title("🔐 Administration")
mot_de_pass = st.sidebar.text_input("Accès Admin", type="password")

if mot_de_pass != CODE_SECRET:
    st.info("👋 Bienvenue sur Veritas Seal. Entrez le code admin pour activer le scellage.")
    
    # Affichage du "Comment ça marche" même sans code
    st.write("### 🛡️ Qu'est-ce que Veritas Seal ?")
    st.write("Une empreinte cryptographique est une signature unique. Modifier un seul caractère change complètement le hash.")
    st.warning("🔒 Aucun document n'est stocké ou conservé sur nos serveurs.")
    st.stop()

# --- SI LE CODE EST BON, ON CONTINUE ---
st.sidebar.success("Accès autorisé")

# Paramètres Google (Remplis avec tes vrais IDs dans Pydroid 3)
GOOGLE_KEYS = {
  "type": "service_account",
  "project_id": "veritas-seal-projet",
  "private_key_id": "9d96d00015cd8ebe366055b9fd3ef8b86c14ff1a",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDVw4o8OGBRCm/\nU\\neeb4H8IS/Iu+slRIboJJRQGxr+\nn8BfEEPLdZ8h/Y+\nnXCG0HOW8Xbig4uTFWifkNr\\nnnMLcafdMBP7Ief/SgeWd/\nnA0z0EoDx7I8t74K3FSgpGohTJ0Z+\nngdwwVhC2mWP\no4Pw\\nnn8GSgZpweuypoVFRp0N88hdaei2szn+U9nj1vLk6PXQ95t/\nnXCiGYqGpzELhH7of61\\nnnQ6ARNJoyrzJgL9Fdwls4h9n1cGqILT4j190tQeq9rG39LQH+\nnlZhOfFE5P4vMTqj\\nnRBs/\nn33DCkUmBmTyuDeLJJNN1hXxEYJuSlvbgRw2Jpfhf94YNzsNn8ZI/\nn8LKF9f\\nnnkuv3lwhTAgMBAAECggEAID6NtIXAfu5Mbh1G2ZfYxiquG3aJjaPfxA6JaxM8aBf\nx\\nVn3VH0akvL/\nnh4W9HhSftxmX8q3ltkwN19fj0Nb/\nnlZgYpvmJtugretapWh3v3c4Mw\\nnnoUH0z+6U/reuS/WVi7HmZhYUF97VC7Sw6/\nnaeHaFn34fg5KiOtTiDWKIuD5oEE\\nnn345UR8Yek6pTaXoWkr0+L7vhGBmclgRjbjahU+\nn5CoZVI7aJISltNUEdspKubdyRt\\nnn6MHJzRiAHpqWvJ+9U3NKhnMiuIbshRWH+\nnbeAeyR0NYwyJNXOZsZ1+dHrRHP++\nR9I\\nnnQGNJHDOLM4mLODwGKeiKQL4eTjtha4vSPm/\nn8tCfkQKBgQD9L4GSnYzsE4r0So6A\\nnnpFhErAE3fvnTPWElABV4ITt31PuF5MTgkhBBcqFbb1GMMQwAU3l5+b6DnlVc3d\\nnnKOb/\nn8sQRfP081Funs3lJdq47y3RCklvlZ4m7PV+eCStFkAFUGz3Spt/\nn4r945LUWI\\nnnWTHcKn3qVG/\nnGSJrY4S7YLm4xuQKBgQDYI9nOzZj30l4it2oGFHtTiqpthR4ofW8Y\\nnnMiWCrIfIxNHQoBWXm9VIUbdTjUsuZJt8ZiWTx+\nnFvxFQdadVYlauwAyrKDv2vd8\\nnn10YJWdCa/E62j9RydUkNeSQqxL4PnUPVffzu3TTZK29Oh+uvs204eh1vDURt3Z8v\\nn\\nnIQUAtZAawkBgCu+\nnWHm3ZNCo87oPY52QR3vd5/\nnvdKuPlWlti0Grq79wZ+\nnLmcVhaC\\nnn6QreRQ5NYCXqmFE9i+\nnk19iqerdUSfHz6cJQJQFU9LhejbQ6FcLajpcjKlxSTIsug\\nnnMAK+\nnEq4gUwycW85nQoAxusKhyBhC3R+\nnYoYezg7vHyOQOSuqtZUWOiBVpAoGAJ7Uu\\nnnZpfO6ngeJLKdf9BZd72Z4dT63WV t63wK+B7K0KQYB8PhM6Elax+\nnIXNQERM85D4H7\\nnnQEXMnz2Jyw1m3bMG+H5EnX+\nnlSXIUOQNmHQXHo5BE4bm6tpRQEWPCcE7JlrAgh\\nnV6C7/MnGAR9nZTgJcL6+\nneZBuaeC1RhLZ8PM0eVECgYEAs2+QAP9/+kw7inN+\nnBQeZ\\nnnTCCmff7gxgGOIcCBPB1HVw3YdBmJwJZNT4Ljqmy01KGs3kj7ps1WnqSD/\nnRFMaZ7xm\\nnnqQiY62fZvUe0ds01FHYWfLc qoyZblmd+\nns32c8LTLwjf7j9EoLbPPXVqbxVTOurWd\\nnnWjHR7hNlwu3yRz/H2wNNsVM=\\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@veritas-seal-project.iam.gserviceaccount.com",
  "client_id": "100913077740203582046",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.google.com/token",
  "auth_proviter_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40veritas-seal-project.iam.gserviceaccount.com"
}

# Connexion Sheets
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(GOOGLE_KEYS, scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("Veritas-seal-database")
    sheet = spreadsheet.sheet1
except Exception as e:
    st.error("Erreur de connexion à la base de données.")
    st.stop()

# --- INTERFACE PRINCIPALE ---
st.title("🛡️ Veritas Seal")
st.caption("Preuve technique d'intégrité et d'antériorité numérique")

tabs = st.tabs(["📄 Sceller un document", "🔍 Vérifier l'authenticité"])

# --- TAB 1 : SCELLAGE ---
with tabs[0]:
    st.write("### Sceller un nouveau fichier")
    uploaded_file = st.file_uploader("Choisissez un fichier", type=None)
    st.info("🔐 Traitement local - fichier non transmis")

    if uploaded_file is not None:
        # Calcul du Hash
        file_bytes = uploaded_file.read()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        file_size = len(file_bytes)

        st.write(f"**Taille du fichier :** {file_size} octets")
        st.write(f"**Empreinte (SHA-256) :** `{file_hash}`")

        if st.button("Confirmer le scellage"):
            # Génération des données de traçabilité
            unique_id = f"VS-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"
            date_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            timestamp_unix = int(datetime.now(timezone.utc).timestamp())

            # Sauvegarde dans Google Sheets (On ne stocke PAS le nom du fichier pour plus de privacy)
            sheet.append_row([unique_id, file_hash, date_utc, timestamp_unix])

            st.success(f"✅ Document scellé avec l'ID : {unique_id}")

            # Création du certificat textuel
            certificat = f"""
--- CERTIFICAT DE SCELLAGE VERITAS SEAL ---
ID de preuve : {unique_id}
Empreinte SHA-256 : {file_hash}
Date de scellage : {date_utc}
Timestamp Unix : {timestamp_unix}
---------------------------------------
Attestation : Ce document est une preuve technique 
d'intégrité. Aucune modification n'est possible sans 
altérer l'empreinte ci-dessus.
"""

            st.download_button(
                label="📄 Télécharger le certificat",
                data=certificat,
                file_name=f"Certificat_{unique_id}.txt",
                mime="text/plain"
            )

# --- TAB 2 : VÉRIFICATION ---
with tabs[1]:
    st.write("### Vérifier un document")
    verify_file = st.file_uploader("Déposez le fichier pour vérification", type=None, key="verify")

    if verify_file is not None:
        check_hash = hashlib.sha256(verify_file.read()).hexdigest()

        if st.button("Lancer la vérification"):
            records = sheet.get_all_records()
            df = pd.DataFrame(records)

            # On cherche si le hash existe dans la colonne 'Hash_SHA256' (ou adapte selon ton Sheets)
            match = df[df.iloc[:, 1] == check_hash]

            if not match.empty:
                st.success("✅ Document authentique trouvé dans la base !")
                st.json(match.iloc[0].to_dict())
            else:
                st.error("❌ Document modifié ou inconnu. L'empreinte ne correspond à aucun scellage.")

# --- PIED DE PAGE LÉGAL ---
st.divider()
st.caption("""
⚖️ **Transparence Légale** : Veritas Seal fournit une preuve technique d'intégrité et d'antériorité. 
Il ne remplace pas un notaire ou une autorité légale.
🛡️ **Confidentialité** : Aucun document n'est stocké. Seules les empreintes numériques sont conservées.
""")

