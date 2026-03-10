import streamlit as st
from openai import OpenAI
from io import BytesIO

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="CSM Academy Pro", page_icon="🎓", layout="wide")

# --- INITIALISATION API ---
if "OPENAI_API_KEY" not in st.secrets:
    st.error("Clé API manquante dans les Secrets Streamlit !")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- FONCTION TEXT-TO-SPEECH (TTS) ---
def speak(text):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova", # Voix claire et pédagogique
            input=text
        )
        audio_data = BytesIO(response.content)
        st.audio(audio_data, format="audio/mp3", autoplay=True)
    except Exception as e:
        st.error(f"Erreur de lecture vocale : {e}")

# --- SYSTÈME D'AUTHENTIFICATION & PROGRESSION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🎓 Bienvenue à la CSM Academy")
    st.write("Connectez-vous pour reprendre votre progression.")
    
    user_id = st.text_input("Votre Email ou Pseudo :", key="login_input")
    if st.button("Démarrer l'apprentissage"):
        if user_id:
            st.session_state.user_id = user_id
            st.session_state.authenticated = True
            # Initialisation par défaut (Ici on pourrait charger depuis une DB)
            st.session_state.level = 1
            st.session_state.messages_academy = []
            st.session_state.show_next_button = False
            st.rerun()
        else:
            st.warning("Veuillez entrer un identifiant.")
    st.stop()

# --- DONNÉES DES MODULES ---
LEVELS = {
    1: {"titre": "🌱 Fondamentaux", "desc": "Le rôle du CSM et le cycle de vie client."},
    2: {"titre": "📊 Data & Métriques", "desc": "Maîtriser le Churn et le Health Score."},
    3: {"titre": "🤝 Stratégie & QBR", "desc": "Mener des revues d'affaires."},
    4: {"titre": "🚀 Expansion", "desc": "Upsell et Advocacy."}
}

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title(f"👤 {st.session_state.user_id}")
    st.progress(st.session_state.level / 4)
    st.write(f"Niveau actuel : {st.session_state.level}/4")
    st.divider()
    if st.button("🚪 Déconnexion"):
        st.session_state.clear()
        st.rerun()

# --- INTERFACE PRINCIPALE ---
st.title(f"Module {st.session_state.level} : {LEVELS[st.session_state.level]['titre']}")

# Affichage de l'historique
for msg in st.session_state.messages_academy:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Premier lancement du module
if not st.session_state.messages_academy:
    prompt_init = f"Je suis prêt pour le niveau {st.session_state.level}. Enseigne-moi un concept et donne-moi un exercice."
    with st.spinner("Le mentor prépare le cours..."):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un mentor CSM. Explique un concept et donne UN exercice. Si l'élève réussit, termine par BRAVO_SUIVANT."},
                {"role": "user", "content": prompt_init}
            ]
        )
        ai_resp = response.choices[0].message.content
        st.session_state.messages_academy.append({"role": "assistant", "content": ai_resp})
        st.rerun()

# Zone de contrôle Vocal & Réponse
last_ai_msg = [m for m in st.session_state.messages_academy if m["role"] == "assistant"][-1]

col_vocal, col_next = st.columns([1, 1])
with col_vocal:
    if st.button("🔈 Écouter la consigne"):
        speak(last_ai_msg["content"])

if st.session_state.show_next_button:
    st.success("Module validé !")
    if st.button("Passer au niveau suivant ➡️"):
        st.session_state.level += 1
        st.session_state.messages_academy = []
        st.session_state.show_next_button = False
        st.rerun()
else:
    user_input = st.chat_input("Votre réponse...")
    if user_input:
        st.session_state.messages_academy.append({"role": "user", "content": user_input})
        with st.chat_message("assistant"):
            with st.spinner("Analyse de votre réponse..."):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "Analyse la réponse. Si correcte, finis par BRAVO_SUIVANT."}] + st.session_state.messages_academy
                )
                ai_resp = response.choices[0].message.content
                st.markdown(ai_resp)
                st.session_state.messages_academy.append({"role": "assistant", "content": ai_resp})
                if "BRAVO_SUIVANT" in ai_resp:
                    st.session_state.show_next_button = True
                    st.rerun()
