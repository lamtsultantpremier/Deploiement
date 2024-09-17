
import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from fonctionnalite.traitement import traier_fichier
from streamlit_option_menu import option_menu
from fonctionnalite.distance import distance_par_semaine_km,distance_par_mois_km,distance_jour_km,distance_par_annee_km,distance_par_nuit_jour_km,distance_par_jour_metre
from fonctionnalite.activite_elephant import vitesse_jour_km,vitesse_jour_nuit,vitesse_jour_nuit_moyenne,vitesse_moyenne,vites_moyenne_jour
from io import StringIO
import locale
import sys
import plotly.graph_objects as go
import folium
#definir la date au format francais
locale.setlocale(locale.LC_TIME,"fr_FR.UTF-8")
sys.stdout.reconfigure(encoding='utf-8')
st.set_page_config(page_title="EarthRangers",layout="wide")
if "chemin_fichier" in st.session_state:
    chemin=st.session_state["chemin_fichier"]
    df_for_name=traier_fichier(chemin)
    df_for_last_date=df_for_name.sort_values("Date_Enregistrement",ascending=False).head(1)
    last_date_transmit=df_for_last_date["Date_Enregistrement"].values[0]
    last_hour_transmit=df_for_last_date["Heure_Enregistrement"].values[0]
    numero_colier= df_for_name["source"].values[0]
    nom_elephant=""
    src=df_for_name["SCR"].values[0]
    col1,col2,col3=st.columns([4,5,6])
    if numero_colier=="703630A":
         nom_elephant="Mâle Hamed"
         with col3:
            with st.container(border=True):
                name=st.radio("",["Mâle Hamed"],horizontal=True)
                st.text(f"Numéro de Collier : {numero_colier}")
                st.text(f"Derniere Transmission : {last_date_transmit}")
                st.text(f"Heure : {last_hour_transmit}")
                st.text(f"Système de coordonnée Géographique : {src}")
                st.text(f"Projection de Mercator")
    elif numero_colier=="715235A":
         nom_elephant="Mâle de Séguéla"
         with col3:
            with st.container(border=True):
                name=st.radio("",["Mâle de Séguéla"],horizontal=True)
                st.text(f"Numéro de Collier : {numero_colier}")
                st.text(f"Derniere Transmission : {last_date_transmit}")
                st.text(f"Heure : {last_hour_transmit}")
                st.text(f"Système de coordonnée Géographique : {src}")
                st.text(f"Projection de Mercator")
    elif numero_colier=="735999A":
         nom_elephant="Mâle de Lakota Guéyo"
         with col3:
            with st.container(border=True):
                name=st.radio("",["Mâle de Lakota Guéyo"],horizontal=True)
                st.text(f"Numéro de Collier : {numero_colier}")
                st.text(f"Derniere Transmission : {last_date_transmit}")
                st.text(f"Heure : {last_hour_transmit}")
                st.text(f"Système de coordonnée Géographique : {src}")
                st.text(f"Projection de Mercator")
    elif numero_colier=="704895A":
          nom_elephant="Femelle d'Abokouamekro"
          with col3:
            with st.container(border=True):
                name=st.radio("",["Femelle d'Abokouamekro"],horizontal=True)
                st.text(f"Numéro de Collier : {numero_colier}")
                st.text(f"Système de coordonnée Géographique : {src}")
                st.text(f"Projection de Mercator")
    elif numero_colier=="703632A":
         nom_elephant="Femelle de Dassioko"
         with col3:
            with st.container(border=True):
                name=st.radio("",["Femelle de Dassioko"],horizontal=True)
                st.text(f"Numéro de Collier : {numero_colier}")
                st.text(f"Derniere Transmission : {last_date_transmit}")
                st.text(f"Heure : {last_hour_transmit}")
                st.text(f"Système de coordonnée Géographique : {src}")
                st.text(f"Projection de Mercator")
    elif numero_colier=="738685A":
        nom_elephant="Mâle de Comoé"
        with col3:
         with st.container(border=True):
                name=st.radio("",["Mâle de Comoé"],horizontal=True)
                st.text(f"Numéro de Collier : {numero_colier}")
                st.text(f"Derniere Transmission : {last_date_transmit}")
                st.text(f"Heure : {last_hour_transmit}")
                st.text(f"Système de coordonnée Géographique : {src}")
                st.text(f"Projection de Mercator")
    elif numero_colier=="703631A":
        nom_elephant="Mâle de d'Abouokouamekro"
        with col3:
         with st.container(border=True):
                name=st.radio("",["Mâle de d'Abouokouamekro"],horizontal=True)
                st.text(f"Numéro de Collier : {numero_colier}")
                st.text(f"Derniere Transmission : {last_date_transmit}")
                st.text(f"Heure : {last_hour_transmit}")
                st.text(f"Système de coordonnée Géographique : {src}")
                st.text(f"Projection de Mercator")
    elif numero_colier=="8056":
        nom_elephant="NZI RIVER LOGDGE"
        with col3:
         with st.container(border=True):
                name=st.radio("",["NZI RIVER LOGDGE"],horizontal=True)
                st.text(f"Numéro de Collier : {numero_colier}")
                st.text(f"Derniere Transmission : {last_date_transmit}")
                st.text(f"Heure : {last_hour_transmit}")
                st.text(f"Système de coordonnée Géographique : {src}")
                st.text(f"Projection de Mercator")
    st.session_state["nom_elephant"]=nom_elephant
with st.sidebar:
    st.header('Navigation')
    st.image("image/elephant.png")
    infos=st.selectbox("Pattern de Mouvement",["Vitesse de déplacement","Distance parcourue"],index=None,placeholder='choisir une action')
    st.title("")#
    st.title("")
    st.image("./image/minef.png")
    #st.selectbox("Dynamique de Mouvement",["Direction Geographique","Trajectoire Dominante"])
    #st.title("")
    #st.selectbox("Temps Passé à différents endroits",["Temps de marche","Temps de repos"])
    #st.button("Rapport Journalier")
if "csv_content" not in st.session_state:
    st.session_state["csv_content"]=None
    #Header
    st.subheader("🐘 Description Analytics")
    #Sidebar
    #style css
    #.st-emotion-cache-ue6h4q:classe des selectBox
    st.markdown(
        """
        <style>
            .st-emotion-cache-ue6h4q{
                color: rgb(255, 255, 255);
            }
        .b{
                text-decoration:None;
                color: rgb(255, 255, 255);
                }
        </style>
        """,
        unsafe_allow_html=True
    )
if "chemin_fichier" in st.session_state:
    chemin=st.session_state["chemin_fichier"]
    df=traier_fichier(chemin)
    df=df.sort_values(by="Date_Enregistrement",ascending=False)
    st.session_state["df"]=df
    st.dataframe(df)
    st.write(f"Source : EarthRanger avec {len(df)} Données")
if infos=="Distance parcourue":
    options_distances=["Distance par Jour","Distance par Semaine","Distance par Mois","Distance par Année"]
    option_selected=st.radio("Distance",options_distances,horizontal=True)
    if option_selected=="Distance par Jour":
        st.write(option_selected)
        col1,col2=st.columns(2)
        with col1:
            st.text(f"Distance par Jour {st.session_state['nom_elephant']}")
            distance_jour=distance_jour_km(df)
            distance_jour_date_debut=pd.to_datetime(distance_jour.tail(1)["Date"].values[0]).date()
            distance_jour_date_fin=pd.to_datetime(distance_jour.head(1)["Date"].values[0]).date()
            st.dataframe(distance_jour)
        with col2.container(border=True):
            fig=px.line(distance_jour,x="Date",y="distance",width=600,height=500,title=f"Distance par Jour {st.session_state['nom_elephant']} à la date du {distance_jour_date_debut} au {distance_jour_date_fin}")
            st.plotly_chart(fig,selection_mode="points")
    if option_selected=="Distance par Semaine":
        distance_semaine=distance_par_semaine_km(df)
        distance_semaine_date_fin=pd.to_datetime(distance_semaine.tail(1)["Date"].values[0]).date()
        distance_semaine_date_debut=pd.to_datetime(distance_semaine.head(1)["Date"].values[0]).date()
        col1,col2=st.columns(2)
        with col1:
            st.text(f"Distance par Semaine {st.session_state['nom_elephant']}")
            st.dataframe(distance_semaine)
        with col2.container(border=True):
            fig=px.line(distance_semaine,x="Date",y="distance",width=500,height=500,title=f"Distance par Semaine {st.session_state['nom_elephant']} à la date du {distance_semaine_date_debut} au {distance_semaine_date_fin}")
            st.plotly_chart(fig,selection_mode="points")
    if option_selected=="Distance par Mois":
        distance_mois=distance_par_mois_km(df)
        col1,col2=st.columns(2)
        with col1:
            st.text(f"Distance par Mois {st.session_state['nom_elephant']}")
            st.dataframe(distance_mois)
        with col2.container(border=True):
            first_record=distance_mois.head(1)
            last_record=distance_mois.tail(1)
            date_debut=pd.to_datetime(first_record["Date"]).dt.date[0]
            date_fin=pd.to_datetime(last_record["Date"]).dt.date[len(distance_mois)-1]
            date_debut_aff=date_debut
            date_fin_aff=date_fin
            fig=px.bar(distance_mois,x="Date",y="distance",width=500,height=500,title=f"Courbe des distances du {date_debut_aff} au {date_fin_aff} du male de {st.session_state['nom_elephant']}",labels={"distance":"Distance par Mois"})
            st.plotly_chart(fig,selection_mode="points")
    if option_selected=="Distance par Année":
        distance_annee=distance_par_annee_km(df)
        col1,col2=st.columns(2)
        with col1:
            st.text(f"Distance par Année {st.session_state['nom_elephant']}")
            st.dataframe(distance_annee)
        with col2.container(border=True): 
            fig=px.bar(distance_annee,x="Date",y="distance",width=200,height=300)
            st.plotly_chart(fig)
    distance_nuit_jour=st.radio("Distance de Jour et de Nuit",["","Distance nuit et Jour"],horizontal=True)
    if distance_nuit_jour!="Distance nuit et Jour":
            distance_nuit_jour=distance_par_nuit_jour_km(df)
            distance_nuit_jour_unstack=distance_nuit_jour.unstack()
            distance_nuit_jour_formated=distance_nuit_jour_unstack["Distance_parcourue_km"]
            dates=[]
            for index,rows in distance_nuit_jour_formated.iterrows():
                print(distance_nuit_jour_formated.loc[[index]])
                dates.append(index)
            with st.expander("Choisir une date"):
                choix=st.selectbox("",dates,index=None,placeholder="Choisir une Date")
            ##on est ICI
            if choix:
                color_sequences=["orange","yellow"]
                df=distance_nuit_jour_formated.loc[[choix]]
                col1,col2,col3=st.columns(3)
                col4,col5,col6=st.columns(3)
                dist_nuit=df["Nuit"].values[0]
                distance_jour=df["Jour"].values[0]
                data_sector={"Distance":[dist_nuit,distance_jour],"Type":["Nuit","Jour"]}
                df_sector=pd.DataFrame(data_sector)
                with col1:
                    st.text(f"Distance {st.session_state['nom_elephant']}")
                    st.dataframe(df)
                with col3:
                    st.text("Distance")
                    st.dataframe(df_sector)
                form=px.pie(df_sector,names="Type",values="Distance",title=f"Distance Parcourue Jour et Nuit {st.session_state["nom_elephant"]} le {choix}",width=500,height=500,color_discrete_sequence=["orange","gray"])
                with col5:
                    st.plotly_chart(form)
                
                #Debut de la partie concernant la comparaison entre deux date
            options_compare=["Comparaison entre deux Date",""]
            choix1=st.radio("",options_compare,horizontal=True)
            if choix1=="Comparaison entre deux Date":
                    col1,col2,col3=st.columns(3)
                    with col1:
                        with st.expander("Choisi la prémière date"):
                            choix_date1=st.selectbox("Choisir une date",dates,index=None,placeholder="Choisissez la Premiere Date")
                            if choix_date1:
                            #Information concernant la premiere Liste déroulante
                            #selectionner la dataframe resultant de la date1
                                df_date1=distance_nuit_jour_formated.loc[[choix_date1]]
                                dist_nuit_date1=df_date1["Nuit"].values[0]
                                dist_jour_date1=df_date1["Jour"].values[0]
                                st.session_state["nuit1"]=dist_nuit_date1
                                st.session_state["jour1"]=dist_jour_date1
                                data_sector_date1={"Type":["Nuit","Jour"],"Distance":[dist_nuit_date1,dist_jour_date1]}
                                df_sector_date1=pd.DataFrame(data_sector_date1)
                                st.dataframe(df_sector_date1)
                                form_date1=px.pie(df_sector_date1,names="Type",values="Distance",color_discrete_sequence=["blue","green"],width=430,height=300)
                                st.plotly_chart(form_date1)
                    with col3:
                        with st.expander("Choisi la deuxieme date"):
                            choix_date2=st.selectbox("Choisir une date",dates,index=None,placeholder="Choisissez la Deuxieme Date")
                            if choix_date2:
                            #selectionner la dataframe resultante de la date2
                                df_date2=distance_nuit_jour_formated.loc[[choix_date2]]
                                dist_nuit_date2=df_date2["Nuit"].values[0]
                                dist_jour_date2=df_date2["Jour"].values[0]
                                st.session_state["nuit2"]=dist_nuit_date2
                                st.session_state["jour2"]=dist_jour_date2
                                data_sector_date2={"Type":["Nuit","Jour"],"Distance":[dist_nuit_date2,dist_jour_date2]}
                                df_sector_date2=pd.DataFrame(data_sector_date2)
                                st.dataframe(df_sector_date2)
                                form_date2=px.pie(df_sector_date2,names="Type",values="Distance",color_discrete_sequence=["yellow","gray"],width=430,height=300)
                                st.plotly_chart(form_date2)     
                    with col2:
                        if st.session_state["nuit2"]!=None:
                            diff_nuit=st.session_state["nuit2"]-st.session_state["nuit1"]
                            diff_jour=st.session_state["jour2"]-st.session_state["jour1"]
                            if diff_nuit<0 or diff_jour<0 or (diff_jour<0 and diff_nuit<0):
                                st.write("La difference de nuit ou de jour est inferieure à Zero")
                                diff_dict={"Type":["Nuit","Jour"],"Distance":[diff_nuit,diff_jour]}
                                df_diff=pd.DataFrame(diff_dict)
                                st.dataframe(df_diff)
                            else:
                                diff_dict={"Type":["Nuit","Jour"],"Distance":[diff_nuit,diff_jour]}
                                df_diff=pd.DataFrame(diff_dict)
                                st.dataframe(df_diff)
                                form_diff=px.pie(df_diff,values="Distance",names="Type",color_discrete_sequence=["orange","gray"],width=200,height=200)
                                st.plotly_chart(form_diff)
            else:
                    st.session_state["nuit2"]=None
                    st.session_state["nuit1"]=None
                    st.session_state["jour1"]=None
                    st.session_state["jour2"]=None         
    else:
        distance_nuit_jour=distance_par_nuit_jour_km(df)
        col1,col2=st.columns(2)
        with col1:
            st.dataframe(distance_nuit_jour)
        with col2.container(border=True):
             distance_nuit_jour_unstack=distance_nuit_jour.unstack(level="temps")
             distance_nuit_jour_formated=distance_nuit_jour_unstack["Distance_parcourue_km"]
             fig,ax=plt.subplots(figsize=(18,12))
             distance_nuit_jour_formated.head(60).plot(kind="barh",ax=ax,color={"Jour":"blue","Nuit":"orange"},grid=False)
             ax.set_xlabel('Distance_parcourue_Km')
             ax.set_ylabel('Date')
             st.pyplot(fig)

elif infos=="Vitesse de déplacement":
    df_vitesse=vitesse_jour_km(df)
    max_vitesse=df_vitesse["vitesse"].max()
    date_list=[]
    for index,row in df_vitesse.iterrows():
        date_list.append(index)
    #Boucle pour recuperer la date selectionner
    with st.expander("Choisissez une date"):
        date_selecteds=st.selectbox("",date_list,index=None,placeholder="Choisisszez une date")
    #Fin
    #print(date_selected.strftime("%d %B %Y"))
    st.write("Parametre de Vitesse")
    if date_selecteds!=None:
        #Un probleme avec le format de la date
        date_a_affich=date_selecteds.strftime("%d/%m/%Y")
        st.write(f"Vitesse effecctuer le {date_a_affich}")
        dataframe_vitesse=df_vitesse.loc[[date_selecteds]]
        st.table(dataframe_vitesse)
        col1,col2,col3=st.columns(3)
        vitesse=round(dataframe_vitesse["vitesse"].values[0],6)
        with col2:
            with st.container(border=True):
                distance=round(dataframe_vitesse["distance_km"].values[0],6)
                distance_metre=round(distance*1000,5)
                temps=dataframe_vitesse["duree_heure"].values[0]
                vitess_moyenne=vites_moyenne_jour(df)
                st.text(f"Distance en Km : {distance}")
                st.text(f"distance en Mètre :{distance_metre}")
                st.text(f"La durée :  {temps}")
                st.text(f"Vitesse en km/h :{vitesse}")
                st.text(f"vitesse moyenne: {round(vitess_moyenne,5)}")
       
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = vitesse,
            number={"suffix":"km/h"},
            title = {'text': "Vitesse"},
            gauge = {
                'axis': {'range': [None, max_vitesse]},
                'steps': [
                {'range': [0,vitesse],'color':"lightgray"}],
                    'threshold': {
                    'line': {'color': "red", 'width': 1},
                    'thickness': 0.75,
                    'value':vitesse}}))
        st.plotly_chart(fig,use_container_width=True)
    else:
        first_dataframe=df_vitesse.sort_values("index",ascending=False).head(1)
        last_date=first_dataframe["index"].values[0]
        last_vitesse=round(first_dataframe["vitesse"].values[0],5)
        st.text(f"La vitesse de {st.session_state['nom_elephant']} le {last_date.strftime("%d/%m/%Y")}")
        st.dataframe(first_dataframe)
        col1,col2,col3=st.columns(3)
        with col2:
            with st.container(border=True):
                distance=round(first_dataframe["distance_km"].values[0],5)
                distance_metre=distance*1000
                temps=first_dataframe["duree_heure"].values[0]
                vitess_moyenne=vites_moyenne_jour(df)
                st.text(f"Distance en Km : {distance}")
                st.text(f"distance en Mètre :{distance_metre}")
                st.text(f"La durée :  {temps}")
                st.text(f"Vitesse en km/h :{last_vitesse}")
                st.text(f"vitesse moyenne: {round(vitess_moyenne,5)}")

        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value =last_vitesse,
            number={"suffix":"km/h"},
            title = {'text': "Vitesse"},
            gauge = {
                'axis': {'range': [None, max_vitesse]},
                'steps': [
                {'range': [0,last_vitesse],'color':"lightgray"}],
                    'threshold': {
                    'line': {'color': "red", 'width': 1},
                    'thickness': 0.75,
                    'value':last_vitesse}}))
        st.plotly_chart(fig,use_container_width=True)
        choix_vitesse_nuit_jour=st.radio("",["","Vitesse Nuit et Jour"],horizontal=True)
        if choix_vitesse_nuit_jour=="Vitesse Nuit et Jour":
             col1,col2=st.columns([4,6])
             df_vitesse_nuit_jour=vitesse_jour_nuit(df)
             df_vitesse_nuit_jour_unstack=df_vitesse_nuit_jour.unstack(level="temps",fill_value=0)["vitesse"]
             df_dist_nuit_jour_unstack=df_vitesse_nuit_jour.unstack(level="temps",fill_value=0)["distance"]
             with col1:
                st.text("Données Concernant les Vitesse")
                st.table(df_vitesse_nuit_jour_unstack.head(10))
                st.text("Données concernant les Distances")
                st.table(df_dist_nuit_jour_unstack.head(10))
             with col2:
                with st.container(border=True):
                    vitesse_display=df_vitesse_nuit_jour_unstack
                    fig,ax=plt.subplots(figsize=(20,10))
                    vitesse_display.head(60).plot(kind="barh",ax=ax,color={"Jour":"blue","Nuit":"orange"},grid=False)
                    ax.set_xlabel('vitesse en Km/h')
                    ax.set_ylabel('Date')
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines["left"].set_visible(False)
                    ax.spines['bottom'].set_visible(False)
                    ax.set_title("vitesse de Nuit et de Jours",fontsize=11)
                    st.pyplot(fig)
             st.subheader("Vitesse Moyenne de Jour et de nuit")
             st.text("Vitesse Moyenne")
             vit_moy=vitesse_moyenne(df)
             st.text(vit_moy)
             df_vitesse_moy=vitesse_jour_nuit_moyenne(df)
             st.table(df_vitesse_moy.head(10))
             fig,ax=plt.subplots(figsize=(6,11))
             df_vitesse_moy.head(10).plot(kind="barh",ax=ax,color={"vitesse_moyenne_jour":"gray","vitesse_moyenne_nuit":"green"},grid=False) 
             ax.set_xlabel=("Vitesse Moyenne")  
             ax.set_ylabel("Date")
             ax.set_title("Vitesse Moyenne de Jour et de Nuit")
             ax.spines[["top","left","right","bottom"]].set_visible(False)
             st.pyplot(fig)   
    #Reserver pour les vitesse de Jour et de nuit
    #with st.container(border=True):
    #    col1,col2=st.columns([2,4])
    #    df_vitesse=vitesse_jour(df)
    #    maximum=df_vitesse["distance_m"].max()
    #    st.dataframe(df_vitesse)
    #    #ICI ON EST
    #    for index,rows in df_vitesse.iterrows():
    #        with col1:
    #          with st.container(border=True):
    #                distance=round(df_vitesse.loc[index]["distance_m"],4)
    #                st.text(distance)
    #        with col2:
    #            with st.container(border=True):
    #                fig = go.Figure(go.Indicator(
    #                mode = "gauge+number",
    #                value = distance,
    #                delta = {'reference':20},
    #                title = {'text': "Vitesse"},
    #                gauge = {
    #                    'axis': {'range': [None, maximum]},
    #                    'steps': [
    #                    {'range': [0, distance],'color': "lightgray"}],
    #                    'threshold': {
    #                    'line': {'color': "red", 'width': 2},
    #                    'thickness': 0.75,
    #                    'value': distance}}))
    #                st.plotly_chart(fig,use_container_width=True)

#st-emotion-cache-1d4lk37
#col1, col2,col3,col4,col5= st.columns(5)

#with col1:
    #st.header("Colonne 1")
    #st.write("Contenu de la première colonne")

#with col2:
    #st.header("Colonne 2")
    #st.write("Contenu de la deuxième colonne")
#with col3:
    #st.header("Colonne 2")
    #st.write("Contenu de la deuxième colonne")
#with col4:
    #st.header("Colonne 2")
    #st.write("Contenu de la deuxième colonne")
#with col5:
    #st.header("Colonne 2")
    #st.write("Contenu de la deuxième colonne")

#tab1, tab2= st.tabs(["Tab 1", "Tab 2"])

# Contenu pour le premier onglet
#with tab1:
    #st.header("Contenu du premier onglet")
    #st.write("AAAA")

# Contenu pour le deuxième onglet
#with tab2:
    #st.header("Contenu du deuxième onglet")
    #st.write("AAAAA")
#st.write()
