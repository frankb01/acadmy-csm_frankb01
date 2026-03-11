import streamlit as st
from openai import OpenAI
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="CSM Master Academy", page_icon="🏆", layout="wide")

# Initialisation OpenAI
if "OPENAI_API_KEY" not in st.secrets:
    st.error("Clé API manquante dans les Secrets !")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Connexion Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Erreur de connexion à la base de données Cloud.")
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
        # On limite le texte pour la synthèse vocale (max 4096 car.)
        clean_text = text[:4000]
        response = client.audio.speech.create(model="tts-1", voice="nova", input=clean_text)
        st.audio(BytesIO(response.content), format="audio/mp3", autoplay=True)
    except Exception as e:
        st.error(f"Erreur audio : {e}")

# --- 3. STRUCTURE DU CURRICULUM (8 MODULES) ---
LEVELS = {
    1: {"titre": "🌱 Fondamentaux & Culture SaaS", "desc": "L'économie de l'abonnement, le TTV et le rôle pivot du CSM."},
    2: {"titre": "🚀 Onboarding & Adoption", "desc": "Réduire le Time-to-Value et orchestrer une implémentation réussie."},
    3: {"titre": "📊 Métriques de Performance", "desc": "Maîtriser le NRR, GRR, LTV et l'analyse fine du Churn."},
    4: {"titre": "🔍 Health Scoring & Data", "desc": "Construire un score de santé prédictif et segmenter sa base client."},
    5: {"titre": "🛡️ Gestion des Risques & Escalades", "desc": "Sauvetage de comptes, playbooks de crise et gestion de l'attrition."},
    6: {"titre": "📈 Strategic Business Reviews (QBR)", "desc": "Animer des revues de valeur et engager les décideurs C-Level."},
    7: {"titre": "💰 Expansion & Stratégie de Revenu", "desc": "Upsell, Cross-sell et techniques de négociation commerciale pour CSM."},
    8: {"titre": "👑 Advocacy & Leadership", "desc": "Transformer les clients en ambassadeurs et bâtir une vision stratégique."}
}

# --- 4. AUTHENTIFICATION ---
if "authenticated" not in st.session_state:
    st.title("🎓 CSM Master Academy")
    st.markdown("### Devenez un Expert certifié en Customer Success Management")
    u_id = st.text_input("Entrez votre Email pour commencer ou reprendre :")
    if st.button("Accéder à l'Académie"):
        if u_id:
            st.session_state.user_id = u_id
            st.session_state.level = load_user_level(u_id)
            st.session_state.authenticated = True
            st.session_state.messages = []
            st.session_state.show_next = False
            st.rerun()
        else:
            st.warning("Identifiant requis.")
    st.stop()

# --- 5. INTERFACE ET NAVIGATION ---
with st.sidebar:
    st.title(f"👤 {st.session_state.user_id}")
    st.divider()
    if st.session_state.level <= 8:
        st.write(f"**Progression : {st.session_state.level}/8**")
        st.progress(st.session_state.level / 8)
    else:
        st.success("✅ Certification Complétée")
    
    st.divider()
    if st.button("🚪 Déconnexion"):
        st.session_state.clear()
        st.rerun()

# --- 6. ÉCRAN FINAL : LE CERTIFICAT ---
if st.session_state.level > 8:
    st.balloons()
    st.markdown(f"""
    <div style="border: 10px solid #2E86C1; padding: 50px; text-align: center; background-color: #FBFCFC; border-radius: 15px; color: #2c3e50; font-family: 'Helvetica';">
        <h1 style="font-size: 60px; color: #1B4F72; margin-bottom: 10px;">CERTIFICAT DE RÉUSSITE</h1>
        <p style="font-size: 24px; text-transform: uppercase; letter-spacing: 2px;">Décerné fièrement à</p>
        <h2 style="font-size: 50px; color: #2E86C1; margin: 20px 0;">{st.session_state.user_id}</h2>
        <p style="font-size: 22px;">Pour avoir complété avec brio le parcours d'expertise de</p>
        <h3 style="font-size: 32px; font-weight: bold;">CUSTOMER SUCCESS MANAGER MASTER</h3>
        <hr style="width: 50%; margin: 30px auto; border: 1px solid #BDC3C7;">
        <p style="font-size: 18px;"><i>Délivré par le Mentor IA - Date : {pd.Timestamp.now().strftime('%d/%m/%Y')}</i></p>
        <p style="color: #7F8C8D; margin-top: 20px;">ID : CSM-{hash(st.session_state.user_id) % 1000000}</p>
    </div>
    """, unsafe_allow_html=True)
    st.info("💡 Prenez une capture d'écran pour partager votre réussite sur LinkedIn !")
    st.stop()

# --- 7. LOGIQUE D'APPRENTISSAGE ---
st.header(f"Module {st.session_state.level} : {LEVELS[st.session_state.level]['titre']}")

# Initialisation du message de l'IA si vide
if not st.session_state.messages:
    system_prompt = {
        "role": "system",
        "content": f"""Tu es un Mentor Senior en Customer Success Management. 
        Tu enseignes le niveau {st.session_state.level} : {LEVELS[st.session_state.level]['titre']}.
        
        STRUCTURE DE TA RÉPONSE :
        1. Théorie Approfondie : Explique les concepts clés (ex: {LEVELS[st.session_state.level]['desc']}).
        2. Méthodologie : Cite des frameworks réels (Gainsight, SuccessHacker, etc.).
        3. Étude de Cas : Un scénario SaaS complexe.
        4. Exercice Stratégique : Pose une question ouverte.
        
        CONSIGNES :
        - Développe ton explication (sois exhaustif).
        - Si la réponse est excellente, termine par 'BRAVO_SUIVANT'.
        - Ne confonds jamais avec Scrum Master."""
    }
    st.session_state.messages.append(system_prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Le mentor prépare la leçon..."):
            resp = client.chat.completions.create(model="gpt-4o", messages=st.session_state.messages)
            ai_txt = resp.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_txt})
            st.markdown(ai_txt)

else:
    # Affichage de l'historique
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# Barre d'actions
st.divider()
col_audio, col_empty = st.columns([1, 4])
with col_audio:
    if st.button("🔈 Écouter la leçon"):
        last_ai_txt = [m["content"] for m in st.session_state.messages if m["role"] == "assistant"][-1]
        speak(last_ai_txt)

# Gestion de la progression
if st.session_state.show_next:
    st.balloons()
    st.success("Leçon maîtrisée !")
    if st.button("Passer au Module Suivant ➡️"):
        st.session_state.level += 1
        save_user_level(st.session_state.user_id, st.session_state.level)
        st.session_state.messages = []
        st.session_state.show_next = False
        st.rerun()
else:
user_input = st.chat_input("Répondez à l'exercice ici...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("assistant"):
            with st.spinner("Analyse du mentor..."):
                resp = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=st.session_state.messages
                )
                ai_txt = resp.choices[0].message.content
                st.markdown(ai_txt)
                st.session_state.messages.append({"role": "assistant", "content": ai_txt})
                
                # LA CORRECTION EST ICI :
                if "BRAVO_SUIVANT" in ai_txt:
                    st.session_state.show_next = True
                    st.rerun()  # Force Streamlit à recharger pour afficher le bouton vert
