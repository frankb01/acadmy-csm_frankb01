import streamlit as st
from openai import OpenAI
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="CSM Academy Pro", page_icon="🎓", layout="wide")

# Initialisation OpenAI
if "OPENAI_API_KEY" not in st.secrets:
    st.error("Clé API manquante dans les Secrets Streamlit !")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Connexion Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Erreur de connexion au Google Sheet. Vérifiez vos secrets.")
    st.stop()

# --- 2. FONCTIONS DE DONNÉES & AUDIO ---
def load_user_level(user_id):
    try:
        df = conn.read(ttl=0)
        user_data = df[df['user_id'] == user_id]
        if not user_data.empty:
            return int(user_data.iloc[0]['level'])
    except:
        pass
    return 1

def save_user_level(user_id, level):
    try:
        df = conn.read(ttl=0)
        if user_id in df['user_id'].values:
            df.loc[df['user_id'] == user_id, 'level'] = level
        else:
            new_row = pd.DataFrame({"user_id": [user_id], "level": [level]})
            df = pd.concat([df, new_row], ignore_index=True)
        conn.update(data=df)
    except Exception as e:
        st.error(f"Erreur de sauvegarde : {e}")

def speak(text):
    try:
        response = client.audio.speech.create(model="tts-1", voice="nova", input=text)
        st.audio(BytesIO(response.content), format="audio/mp3", autoplay=True)
    except Exception as e:
        st.error(f"Erreur audio : {e}")

# --- 3. SYSTÈME D'AUTHENTIFICATION ---
if "authenticated" not in st.session_state:
    st.title("🎓 CSM Academy : Spécialiste SaaS")
    st.markdown("### Apprenez le métier de Customer Success Manager")
    u_id = st.text_input("Entrez votre Email pour charger votre progression :")
    if st.button("Démarrer l'apprentissage"):
        if u_id:
            st.session_state.user_id = u_id
            st.session_state.level = load_user_level(u_id)
            st.session_state.authenticated = True
            st.session_state.messages = []
            st.session_state.show_next = False
            st.rerun()
        else:
            st.warning("Veuillez entrer un email valide.")
    st.stop()

# --- 4. CONFIGURATION DU MÉTIER (CSM SaaS) ---
LEVELS = {
    1: {"titre": "🌱 Fondamentaux du CSM", "desc": "Cycle de vie client, Onboarding vs Support."},
    2: {"titre": "📊 Métriques de Rétention", "desc": "Churn rate, MRR, Health Score et NPS."},
    3: {"titre": "🤝 Pilotage Stratégique", "desc": "Mener des QBR (Quarterly Business Reviews) et ROI."},
    4: {"titre": "🚀 Expansion & Advocacy", "desc": "Upsell, Cross-sell et transformation en ambassadeur."}
}

# --- 5. INTERFACE PRINCIPALE ---
with st.sidebar:
    st.title(f"👤 {st.session_state.user_id}")
    st.write(f"**Niveau actuel : {st.session_state.level}/4**")
    st.progress(st.session_state.level / 4)
    st.divider()
    if st.button("🚪 Déconnexion"):
        st.session_state.clear()
        st.rerun()

st.header(f"Module {st.session_state.level} : {LEVELS[st.session_state.level]['titre']}")
st.info(LEVELS[st.session_state.level]['desc'])

# Affichage de l'historique
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 6. LOGIQUE DU MENTOR IA ---
if not st.session_state.messages:
    # Initialisation du prompt système spécifique CSM SaaS
    system_prompt = {
        "role": "system",
        "content": f"""Tu es un Mentor Expert en Customer Success Management (CSM) dans le SaaS.
        Tu enseignes le niveau {st.session_state.level} : {LEVELS[st.session_state.level]['titre']}.
        IMPORTANT : Ne confonds jamais avec Scrum Master. Ton sujet est la rétention et le succès client.
        1. Explique un concept métier précis.
        2. Donne une mise en situation réelle.
        3. Pose une question ou un exercice.
        Si l'élève répond correctement, termine ton message par le mot 'BRAVO_SUIVANT'."""
    }
    st.session_state.messages.append(system_prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Le mentor prépare le cours..."):
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages
            )
            ai_txt = resp.choices[0].message.content
            st.markdown(ai_txt)
            st.session_state.messages.append({"role": "assistant", "content": ai_txt})

# Contrôles (Audio et Validation)
st.divider()
col_audio, col_info = st.columns([1, 3])

with col_audio:
    if st.button("🔈 Écouter la leçon"):
        # On lit le dernier message de l'assistant
        last_ai_text = [m["content"] for m in st.session_state.messages if m["role"] == "assistant"][-1]
        speak(last_ai_text)

if st.session_state.show_next:
    st.balloons()
    st.success("Bravo ! Vous avez maîtrisé ce concept.")
    if st.session_state.level < 4:
        if st.button("Passer au niveau suivant ➡️"):
            st.session_state.level += 1
            save_user_level(st.session_state.user_id, st.session_state.level)
            st.session_state.messages = []
            st.session_state.show_next = False
            st.rerun()
    else:
        st.write("🏆 Vous avez terminé tous les modules de l'Academy !")
else:
    u_ans = st.chat_input("Votre réponse au mentor...")
    if u_ans:
        st.session_state.messages.append({"role": "user", "content": u_ans})
        with st.chat_message("assistant"):
            with st.spinner("Analyse de votre réponse..."):
                resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=st.session_state.messages
                )
                ai_txt = resp.choices[0].message.content
                st.markdown(ai_txt)
                st.session_state.messages.append({"role": "assistant", "content": ai_txt})
                if "BRAVO_SUIVANT" in ai_txt:
                    st.session_state.show_next = True
                    st.rerun()
