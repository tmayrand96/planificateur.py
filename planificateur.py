import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Planificateur de Journée", layout="wide")

# ----- Chargement des activités -----
@st.cache_data
def charger_activites():
    return pd.read_csv("activites_ajustees.csv")

df_activites = charger_activites()

# ----- Thème pastel en fonction du profil -----
def appliquer_couleur_profil(profil):
    couleurs = {"Famille": "#FFF2E6", "Amis": "#E6F2FF", "Seul": "#F2E6FF"}
    couleur = couleurs.get(profil, "#FFFFFF")
    st.markdown(
        f"<style>body {{ background-color: {couleur}; color: #000000; }}</style>",
        unsafe_allow_html=True,
    )

st.title("🗓️ Planificateur de Journée Personnalisée")

# ----- Choix de l'âge -----
ages = ["16-17", "18-21", "22-25", "26-29", "30-35", "36-40", "41-45", "45+"]
age_choisi = st.selectbox("Sélectionnez votre tranche d'âge :", ages)
if age_choisi:
    df_activites = df_activites[df_activites["Tranche_age"] == age_choisi]

# ----- Choix du profil utilisateur -----
profil = st.radio("Quel est votre type de journée ?", ["Famille", "Amis", "Seul"], horizontal=True)
appliquer_couleur_profil(profil)

# ----- Sélection de plages horaires disponibles -----
st.subheader("🕒 Vos disponibilités (entre 6h et 23h)")

# Initialisation du compteur dans la session
if "compteur" not in st.session_state:
    st.session_state.compteur = 1

plages = []
heure_debut = st.time_input("Heure de début", value=pd.to_datetime("08:00").time(), key="debut_0")
heure_fin = st.time_input("Heure de fin", value=pd.to_datetime("12:00").time(), key="fin_0")
plages.append((heure_debut, heure_fin))

# Boutons pour ajouter ou supprimer une plage horaire
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("➕ Ajouter une autre plage horaire"):
        st.session_state.compteur += 1
with col2:
    if st.button("➖ Supprimer la dernière plage horaire") and st.session_state.compteur > 1:
        st.session_state.compteur -= 1

# Affichage des autres plages horaires
for i in range(1, st.session_state.compteur):
    heure_debut = st.time_input(f"Heure de début {i+1}", value=pd.to_datetime("13:00").time(), key=f"debut_{i}")
    heure_fin = st.time_input(f"Heure de fin {i+1}", value=pd.to_datetime("16:00").time(), key=f"fin_{i}")
    plages.append((heure_debut, heure_fin))

# ----- Génération du planning -----
if st.button("🎯 Générer mon planning"):
    planning = []
    for debut, fin in plages:
        h1 = debut.hour + debut.minute / 60
        h2 = fin.hour + fin.minute / 60
        duree_totale = h2 - h1

        temps_dispo = duree_totale * 60  # en minutes
        activites = df_activites.sample(frac=1).reset_index(drop=True)

        bloc = []
        cumul = 0
        for _, row in activites.iterrows():
            if cumul + row["Duree_minutes"] <= temps_dispo:
                bloc.append(row)
                cumul += row["Duree_minutes"]

        planning.append(pd.DataFrame(bloc))

    st.subheader("🧩 Votre planning personnalisé :")
    for i, p in enumerate(planning):
        st.markdown(f"### Plage {i+1}")
        st.dataframe(p[["Nom", "Duree_minutes", "Lieu", "Effort"]])

    st.success("Planning généré avec succès 🎉")
