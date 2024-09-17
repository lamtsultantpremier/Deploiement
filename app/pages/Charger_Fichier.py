import streamlit as st
import pandas as pd
from io import StringIO
import os
import matplotlib.pyplot as plt
from pathlib import Path
from fonctionnalite.traitement import traier_fichier
if "chemin_fichier" in st.session_state:
    chemin=st.session_state["chemin_fichier"]
    df_for_name=traier_fichier(chemin)
    numero_colier= df_for_name["source"].values[0]
    src=df_for_name["SCR"].values[0]
    col1,col2,col3=st.columns([4,5,6])
    if numero_colier=="703630A":
         with col3:
            with st.container(border=True):
                name=st.radio("",["Mâle Hamed"],horizontal=True)
                st.text(f"Numéro de Collier : {numero_colier}")
                st.text(f"Système de coordonnée Géographique : {src}")
                st.text(f"Projection de Mercator")
    elif numero_colier=="715235A":
         with col3:
            with st.container(border=True):
                name=st.radio("",["Mâle de Séguéla"],horizontal=True)
                st.text(f"Numéro de Collier : {numero_colier}")
                st.text(f"Système de coordonnée Géographique : {src}")
                st.text(f"Projection de Mercator")
    elif numero_colier=="735999A":
         with col3:
            with st.container(border=True):
                name=st.radio("",["Mâle de Lakota Guéyo"],horizontal=True)
                st.text(f"Numéro de Collier : {numero_colier}")
                st.text(f"Système de coordonnée Géographique : {src}")
                st.text(f"Projection de Mercator")
    elif numero_colier=="704895A":
          with col3:
            with st.container(border=True):
                name=st.radio("",["Femelle d'Abokouamekro"],horizontal=True)
                st.text(f"Numéro de Collier : {numero_colier}")
                st.text(f"Système de coordonnée Géographique : {src}")
                st.text(f"Projection de Mercator")
    elif numero_colier=="703632A":
         with col3:
            with st.container(border=True):
                name=st.radio("",["Femelle de Dassioko"],horizontal=True)
                st.text(f"Numéro de Collier : {numero_colier}")
                st.text(f"Système de coordonnée Géographique : {src}")
                st.text(f"Projection de Mercator")
    elif numero_colier=="738685A":
        with col3:
         with st.container(border=True):
                name=st.radio("",["Mâle de Comoé"],horizontal=True)
                st.text(f"Numéro de Collier : {numero_colier}")
                st.text(f"Système de coordonnée Géographique : {src}")
                st.text(f"Projection de Mercator")
    elif numero_colier=="703631A":
        with col3:
         with st.container(border=True):
                name=st.radio("",["Mâle de d'Abouokouamekro"],horizontal=True)
                st.text(f"Numéro de Collier : {numero_colier}")
                st.text(f"Système de coordonnée Géographique : {src}")
                st.text(f"Projection de Mercator")
with st.sidebar:
    st.header('Navigation')
    st.image("image/elephant.png")
uploaded_file=st.file_uploader(label="Charger un fichier .CSV",type=["csv"])
rep_par_defaut="Excel"
    #creation d'une session pour le stockage du fichier
st.markdown(
        """
        <style>
            .st-emotion-cache-1jgv1qq
            {
            background-color:rgb(213, 218, 229);
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    #recuperer le fichier csv puis l'enregistrer dans un dossier séparé
if uploaded_file is not None:
        rep_par_defaut=Path(rep_par_defaut).glob("*")
        for fichier in rep_par_defaut:
            fichier.unlink()
        rep_par_defaut="Excel"
        nom_fichier=uploaded_file.name
        type_fichier=uploaded_file.type
        taille_fichier=uploaded_file.size
        st.session_state["nom_fichier"]=nom_fichier
        st.session_state["type_fichier"]=type_fichier
        st.session_state["taille_fichier"]=taille_fichier
        chemin_fichier=Path(rep_par_defaut,nom_fichier)
        st.session_state['chemin_fichier']=chemin_fichier
        with open(chemin_fichier,mode="wb") as f:
            f.write(uploaded_file.getbuffer())
            #Reinitialiser les variables nuit et jours
            st.session_state["nuit2"]=None
            st.session_state["nuit1"]=None
            st.session_state["jour1"]=None
            st.session_state["jour2"]=None
            #Reinitialiser les variables nuit et jours
if "nom_fichier" in st.session_state and "type_fichier" in st.session_state and "taille_fichier" in st.session_state:
        st.write(f"Nom du Fichier : {st.session_state["nom_fichier"]}")
        st.write(f"Type de fichier : {st.session_state["type_fichier"]}")
        st.write(f" Taille du fichier : {st.session_state["taille_fichier"]} Ko")
        st.text("Extrait du contenu du fichier")
        if "df" in st.session_state: 
            df=st.session_state["df"]
            st.dataframe(df.head(1))