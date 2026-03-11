import streamlit as st
from openai import OpenAI
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CSM Master Academy", page_icon="🏆", layout="wide")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. FONCTIONS DE DONNÉES ---
def load_user_level(user_id):
    try:
        df = conn.read(ttl=0)
        user_data = df[df['user_id'] == user_id]
        if not user_data.empty:
            return int(user_data.iloc[0]['level'])
    except: pass
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
    response = client.audio.speech.create(model="tts-1", voice="nova", input=text[:4000])
    st.audio(BytesIO(response.content), format="audio/mp3", autoplay=True)

# --- 3. CURRICULUM ---
LEVELS = {
    1: {"titre": "🌱 Fondamentaux & Culture SaaS", "desc": "L'économie de l'abonnement et le rôle du CSM."},
    2: {"titre": "🚀 Onboarding & Adoption", "desc": "Réduire le Time-to-Value (TTV)."},
    3: {"titre": "📊 Métriques de Performance", "desc": "Maîtriser le NRR, GRR et le Churn."},
    4: {"titre": "🔍 Health Scoring & Data", "desc": "Prédire les comportements clients."},
    5: {"titre": "🛡️ Gestion des Risques", "desc": "Playbooks de rétention et crise."},
    6: {"titre": "📈 Strategic Business Reviews", "desc": "Animer des QBR/EBR avec impact."},
    7: {"titre": "💰 Expansion & Revenu", "desc": "Upsell et Cross-sell."},
    8: {"titre": "👑 Advocacy & Leadership", "desc": "Transformer les clients en ambassadeurs."}
}

# --- 4. AUTHENTIFICATION ---
if "authenticated" not in st.session_state:
    st.title("🎓 CSM Master Academy")
    u_id = st.text_input("Votre Email :")
    if st.button("Accéder à l'Académie"):
        if u_id:
            st.session_state.user_id = u_id
            st.session_state.level = load_user_level(u_id)
            st.session_state.authenticated = True
            st.session_state.messages = []
            st.session_state.show_next = False
            st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title(f"👤 {st.session_state.user_id}")
    if st.session_state.level <= 8:
        st.write(f"Niveau : {st.session_state.level}/8")
        st.progress(st.session_state.level / 8)
    if st.button("🚪 Déconnexion"):
        st.session_state.clear()
        st.rerun()

# --- 6. CERTIFICAT FINAL ---
if st.session_state.level > 8:
    st.balloons()
    st.markdown(f"""
    <div style="border: 10px solid #2E86C1; padding: 50px; text-align: center; background-color: white; border-radius: 15px;">
        <h1 style="color: #1B4F72;">CERTIFICAT DE RÉUSSITE</h1>
        <h2>{st.session_state.user_id}</h2>
        <h3>CUSTOMER SUCCESS MANAGER MASTER</h3>
        <p>Délivré le {pd.Timestamp.now().strftime('%d/%m/%Y')}</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- 7. INTERFACE DE COURS ---
st.header(f"Module {st.session_state.level} : {LEVELS[st.session_state.level]['titre']}")

# Premier message du mentor
if not st.session_state.messages:
    system_prompt = {
        "role": "system",
        "content": f"Tu es un Mentor Senior CSM. Enseigne le module {st.session_state.level} : {LEVELS[st.session_state.level]['titre']}. Structure : Théorie, Framework, Cas pratique, Exercice. Termine par BRAVO_SUIVANT si l'exercice est réussi."
    }
    st.session_state.messages.append(system_prompt)
    with st.spinner("Le mentor prépare le cours..."):
        resp = client.chat.completions.create(model="gpt-4o", messages=st.session_state.messages)
        ai_txt = resp.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ai_txt})

# Affichage du chat
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 8. LOGIQUE DE VALIDATION ET NAVIGATION (CORRIGÉE) ---
st.divider()

# On affiche le bouton de passage au niveau supérieur SI validé
if st.session_state.show_next:
    st.success("✅ Exercice validé par le mentor !")
    if st.button("Passer au Module Suivant ➡️", use_container_width=True):
        st.session_state.level += 1
        save_user_level(st.session_state.user_id, st.session_state.level)
        st.session_state.messages = []
        st.session_state.show_next = False
        st.rerun()
else:
    # Zone de réponse et lecture
    col_audio, col_input = st.columns([1, 4])
    with col_audio:
        if st.button("🔈 Écouter"):
            last_txt = [m["content"] for m in st.session_state.messages if m["role"] == "assistant"][-1]
            speak(last_txt)
    
    user_ans = st.chat_input("Votre réponse ici...")
    if user_ans:
        st.session_state.messages.append({"role": "user", "content": user_ans})
        with st.chat_message("assistant"):
            with st.spinner("Analyse en cours..."):
                resp = client.chat.completions.create(model="gpt-4o", messages=st.session_state.messages)
                ai_txt = resp.choices[0].message.content
                st.markdown(ai_txt)
                st.session_state.messages.append({"role": "assistant", "content": ai_txt})
                if "BRAVO_SUIVANT" in ai_txt:
                    st.session_state.show_next = True
                    st.rerun() # Crucial pour afficher le bouton vert immédiatement
