import streamlit as st
from openai import OpenAI
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuration
st.set_page_config(page_title="CSM Academy Pro", page_icon="🎓", layout="wide")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Connexion Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FONCTIONS DE DONNÉES ---
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
    df = conn.read(ttl=0)
    if user_id in df['user_id'].values:
        df.loc[df['user_id'] == user_id, 'level'] = level
    else:
        new_row = pd.DataFrame({"user_id": [user_id], "level": [level]})
        df = pd.concat([df, new_row], ignore_index=True)
    conn.update(data=df)

def speak(text):
    response = client.audio.speech.create(model="tts-1", voice="nova", input=text)
    st.audio(BytesIO(response.content), format="audio/mp3", autoplay=True)

# --- AUTHENTIFICATION ---
if "authenticated" not in st.session_state:
    st.title("🎓 CSM Academy : Connexion")
    u_id = st.text_input("Votre Email :")
    if st.button("Se connecter / Créer un compte"):
        if u_id:
            st.session_state.user_id = u_id
            st.session_state.level = load_user_level(u_id)
            st.session_state.authenticated = True
            st.session_state.messages = []
            st.session_state.show_next = False
            st.rerun()
    st.stop()

# --- COURS ---
LEVELS = {1: "🌱 Fondamentaux", 2: "📊 Métriques", 3: "🤝 Stratégie", 4: "🚀 Expansion"}
st.title(f"Module {st.session_state.level} : {LEVELS[st.session_state.level]}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not st.session_state.messages:
    with st.spinner("Chargement du cours..."):
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": f"Tu es un mentor CSM. Enseigne le niveau {st.session_state.level}. Finis par un exercice et 'BRAVO_SUIVANT' si réussi."}]
        )
        txt = resp.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": txt})
        st.rerun()

# Bouton de lecture vocale
if st.button("🔈 Écouter la consigne"):
    speak(st.session_state.messages[-1]["content"])

# Gestion des réponses
if st.session_state.show_next:
    if st.button("Passer au niveau suivant ➡️"):
        st.session_state.level += 1
        save_user_level(st.session_state.user_id, st.session_state.level)
        st.session_state.messages = []
        st.session_state.show_next = False
        st.rerun()
else:
    ans = st.chat_input("Répondez ici...")
    if ans:
        st.session_state.messages.append({"role": "user", "content": ans})
        with st.chat_message("assistant"):
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "Analyse. Si OK, dis BRAVO_SUIVANT."}] + st.session_state.messages
            )
            ai_txt = resp.choices[0].message.content
            st.markdown(ai_txt)
            st.session_state.messages.append({"role": "assistant", "content": ai_txt})
            if "BRAVO_SUIVANT" in ai_txt:
                st.session_state.show_next = True
                st.rerun()
