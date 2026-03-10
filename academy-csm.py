import streamlit as st
from openai import OpenAI

# Configuration
st.set_page_config(page_title="CSM Academy", page_icon="🎓", layout="wide")

# Initialisation OpenAI
if "OPENAI_API_KEY" not in st.secrets:
    st.error("Ajoutez votre clé API dans les secrets Streamlit.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- GESTION DE LA PROGRESSION ---
if "level" not in st.session_state:
    st.session_state.level = 1
if "messages_academy" not in st.session_state:
    st.session_state.messages_academy = []
if "show_next_button" not in st.session_state:
    st.session_state.show_next_button = False

# Niveaux
LEVELS = {
    1: {"titre": "🌱 Fondamentaux", "desc": "Comprendre le rôle du CSM et le cycle de vie client."},
    2: {"titre": "📊 Data & Métriques", "desc": "Maîtriser le Churn, le MRR et le Health Score."},
    3: {"titre": "🤝 Stratégie & QBR", "desc": "Mener des revues d'affaires et gérer les comptes à risque."},
    4: {"titre": "🚀 Expansion", "desc": "Générer de l'Upsell et transformer les clients en ambassadeurs."}
}

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("📍 Votre Parcours")
    for l_id, info in LEVELS.items():
        if st.session_state.level == l_id:
            st.info(f"👉 **Niveau {l_id} : {info['titre']}**")
        elif st.session_state.level > l_id:
            st.success(f"✅ Niveau {l_id} : Terminé")
        else:
            st.text(f"🔒 Niveau {l_id} : {info['titre']}")
    
    st.divider()
    if st.button("Réinitialiser ma progression"):
        st.session_state.level = 1
        st.session_state.messages_academy = []
        st.rerun()

# --- INTERFACE PRINCIPALE ---
st.title(f"Module {st.session_state.level} : {LEVELS[st.session_state.level]['titre']}")
st.caption(LEVELS[st.session_state.level]['desc'])

# Affichage du cours/chat
for msg in st.session_state.messages_academy:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Logique de tutorat IA
if not st.session_state.messages_academy:
    # Premier message du niveau
    prompt_initial = f"Bonjour Mentor ! Je commence le Niveau {st.session_state.level}. Peux-tu m'expliquer un concept clé et me donner un petit exercice ?"
    st.session_state.messages_academy.append({"role": "user", "content": prompt_initial})
    
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un mentor CSM. Enseigne un concept, donne un exemple et un exercice. Si l'élève réussit, dis 'BRAVO_SUIVANT'."},
                {"role": "user", "content": prompt_initial}
            ]
        )
        ai_resp = response.choices[0].message.content
        st.markdown(ai_resp)
        st.session_state.messages_academy.append({"role": "assistant", "content": ai_resp})

# Zone de réponse
st.divider()
if st.session_state.show_next_button:
    st.balloons()
    st.success("Félicitations ! Vous avez validé ce module.")
    if st.button(f"Passer au Niveau {st.session_state.level + 1} ➡️"):
        st.session_state.level += 1
        st.session_state.messages_academy = []
        st.session_state.show_next_button = False
        st.rerun()
else:
    ans = st.chat_input("Votre réponse ou vos questions ici...")
    if ans:
        st.session_state.messages_academy.append({"role": "user", "content": ans})
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "Mentor CSM. Analyse la réponse. Si correct, finis par BRAVO_SUIVANT."}] + st.session_state.messages_academy
            )
            ai_resp = response.choices[0].message.content
            st.markdown(ai_resp)
            st.session_state.messages_academy.append({"role": "assistant", "content": ai_resp})
            
            if "BRAVO_SUIVANT" in ai_resp:
                st.session_state.show_next_button = True
                st.rerun()
