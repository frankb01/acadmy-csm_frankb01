# 🎓 CSM Master Academy — AI-Powered Learning Platform

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://votre-app-url.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange.svg)

**CSM Master Academy** est une plateforme d'apprentissage adaptative conçue pour former les futurs **Customer Success Managers (CSM)** aux enjeux du SaaS moderne. Propulsée par l'intelligence artificielle, l'application propose un parcours certifiant en 8 modules, allant des fondamentaux à la stratégie de revenus.

---

## ✨ Fonctionnalités Clés

* **🧠 Mentorat IA Adaptatif** : Un mentor basé sur GPT-4o qui ajuste ses explications selon vos réponses et utilise des frameworks réels (Gainsight, SuccessHacker).
* **🎙️ Apprentissage Vocal** : Intégration de *Text-to-Speech* pour écouter les leçons et les études de cas.
* **💾 Sauvegarde Cloud** : Connexion à Google Sheets pour reprendre votre progression là où vous vous étiez arrêté.
* **🏆 Certification Finale** : Obtention d'un certificat de réussite personnalisé après validation des 8 modules experts.
* **📊 Curriculum Expert** : 8 niveaux couvrant le Churn, le NRR, l'Onboarding, les QBR et l'Advocacy.

---

## 📚 Programme de Certification

1. **Fondamentaux & Culture SaaS** : L'économie de l'abonnement et le rôle pivot du CSM.
2. **Onboarding & Adoption** : Réduire le Time-to-Value (TTV).
3. **Métriques de Performance** : Maîtriser le NRR, GRR et le Churn.
4. **Health Scoring & Data** : Prédire les comportements clients.
5. **Gestion des Risques** : Sauvetage de comptes et playbooks de crise.
6. **Strategic Business Reviews** : Animer des QBR avec un impact C-Level.
7. **Expansion & Stratégie de Revenu** : Upsell et Cross-sell.
8. **Advocacy & Leadership** : Bâtir une vision stratégique.

---

## 🛠️ Installation & Configuration

### Prérequis
- Python 3.9+
- Une clé API OpenAI
- Un compte Google Cloud (pour la connexion GSheets)

### Installation
1. Clonez le dépôt :
   ```bash
   git clone [https://github.com/votre-username/csm-master-academy.git](https://github.com/votre-username/csm-master-academy.git)
   cd csm-master-academy
Installez les dépendances :

Bash
pip install -r requirements.txt
Configurez vos secrets dans .streamlit/secrets.toml.

🏗️ Architecture Technique
L'application repose sur une architecture moderne combinant traitement du langage naturel et stockage cloud léger :

Frontend : Streamlit (Interface réactive et Wide Mode).

Intelligence Artificielle : OpenAI GPT-4o (Logique métier) & TTS-1 (Audio).

Base de données : Google Sheets API via st-gsheets-connection.

Langage : Python 3.1x.
