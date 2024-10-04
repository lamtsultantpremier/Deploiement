import streamlit as st
import folium as f
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
import datetime
import requests
import plotly.express as px
import pandas as pd
from fonctionnalite.zone_frequentation import distance_dbscan,make_cluster,find_location,number_in_index,color,generate_and_download_image,generate_and_download_image_heatmap
from fonctionnalite.distance import distance,dist_jour_nuit,distance_jour_km,dist_group_temps,distance_periode_jour,distance_total,distance_total_jour_nuit
from selenium import webdriver
import os
from folium.plugins import HeatMap
from folium.plugins import AntPath
import branca
import branca.colormap as cm
from collections import defaultdict
from streamlit.components.v1 import html
from geopy.distance import geodesic
import base64
import geopandas as gpd
from shapely.geometry import Polygon
st.set_page_config(page_title="ElephantCI",layout="wide",page_icon="🐘")
st.subheader("🐘 ELEPHANT CI")
if "df" not in st.session_state:
    st.write("Veuillez Charger un fichier avant de continuer")
else:
    df=st.session_state["df"]
    df=df.sort_values(by=["Date_Enregistrement","Heure_Enregistrement"],ascending=False)
    with st.sidebar:
        carte=st.selectbox("Carte",["","Zone les plus fréquentés","Carte de chaleur"],index=0,placeholder="Choisir une action")
    if carte=="":
        first_record=df.head(1)
        first_lat=first_record['Latitude'].values[0]
        first_long=fird=first_record["Longitude"].values[0]
        first_date=first_record["Date_Enregistrement"].values[0]
        first_hour=first_record["Heure_Enregistrement"].values[0]
        html=f"""
            <h5>Date: {first_date}</h5>
            <p>Longitude: {first_long}</p>
            <p>Latitude: {first_lat}</p>
            <p>Heure: {first_hour}</p>
        """ 
        iframe=f.IFrame(html,width=200,height=200)
        popup=f.Popup(iframe,max_width=300)
        map=f.Map(location=(first_lat,first_long),zoom_start=10)
        icon=f.CustomIcon("image/elephant_marker.png",icon_size=(20,20))
        f.Marker([first_lat,first_long],popup=popup,icon=icon).add_to(map)
        st_folium(map,width=1000)
    if carte=="Zone les plus fréquentés":
        options=["Gaphe des Zones","Visulaisation des Zones de Forte Frequentations"]
        zone_frequenter=st.radio("",options,index=0,horizontal=True)
        if zone_frequenter=="Gaphe des Zones":
            col4,col5=st.columns(2)
            latitudes=[]
            longitudes=[]
            dates_times=[]
            datimes=[]
            col1,col2=st.columns(2)
             #reserver à l'affichage sur matplolib
            if "nom_elephant" in st.session_state:
                nom_elephant=st.session_state["nom_elephant"]
            df_for_trajet=df[["Date_Enregistrement","Heure_Enregistrement","Latitude","Longitude"]]
            for index,rows in df_for_trajet.iterrows():
                latitudes.append(float(rows["Latitude"]))
                longitudes.append(float((rows["Longitude"])))
                dates_times.append(datetime.datetime.combine(rows["Date_Enregistrement"],rows["Heure_Enregistrement"]))
            for date_time in dates_times:
                datimes.append(str(date_time))
            dataframes_from_trajet=pd.DataFrame({"Latitude":latitudes,"Longitude":longitudes,"date":datimes})
            #Afficher les differentes date de debut et de Fin
            date_debut=dataframes_from_trajet.tail(1)["date"].values[0]
            date_fin=dataframes_from_trajet.head(1)["date"].values[0]
            #afficher les longitude et latitudes
            date_debut=date_debut.split(" ")[0]
            date_fin=date_fin.split(" ")[0]
            fig=px.scatter(dataframes_from_trajet,x="Longitude",y="Latitude",hover_data={"date":True,"Longitude":True,"Latitude":True},title=f"Position {nom_elephant} du {date_debut} au {date_fin}")
            fig.update_layout({"width":900,"height":300})
            st.plotly_chart(fig)
            st.write("")
            #determine the different cluster
            epsilon=distance_dbscan(df)
            if epsilon!=0.0:
                df_cluster=make_cluster(df,epsilon)
               #zones proches des endroits de concentrations
                distance=[]
                df_lieux_proche=find_location(df_cluster)
                df_lieux_proche["Distance_Actuel_Elephant"]=""
                latitude_actuel=float(df.head(1)["Latitude"].values[0])
                longitude_actuel=float(df.head(1)["Longitude"].values[0])
                for index,row in df_lieux_proche.iterrows():
                   distance_calculer=(geodesic((latitude_actuel,longitude_actuel),(float(row["Latitude"]),float(row["Longitude"]))).km)
                   df_lieux_proche.loc[index,"Distance_Actuel_Elephant"]=f"{distance_calculer} Km"
                st.write("Lieux Proches des Zones de fortes concentration")
                st.dataframe(df_lieux_proche)            
                fig=px.scatter(df_cluster,x="Longitude",y="Latitude",title=f"Zone de Forte Fréquentation {nom_elephant} du {date_debut} au {date_fin}",color="cluster",labels={"cluster":"niveau de Frequentation"})
                st.plotly_chart(fig)
            else:
                df_cluster=make_cluster(df,0.011)
                #zones proches des endroits de concentrations
                distance=[]
                df_lieux_proche=find_location(df_cluster)
                df_lieux_proche["Distance_Actuel_Elephant"]=""
                latitude_actuel=float(df.head(1)["Latitude"].values[0])
                longitude_actuel=float(df.head(1)["Longitude"].values[0])
                for index,row in df_lieux_proche.iterrows():
                   distance_calculer=(geodesic((latitude_actuel,longitude_actuel),(float(row["Latitude"]),float(row["Longitude"]))).km)
                   df_lieux_proche.loc[index,"Distance_Actuel_Elephant"]=f"{distance_calculer} Km"
                st.write("Lieux Proches des Zones de fortes concentration")
                st.dataframe(df_lieux_proche)
                fig=px.scatter(df_cluster,x="Longitude",y="Latitude",title=f"Zone de Forte Fréquentation {nom_elephant} du {date_debut} au {date_fin}",color="cluster")
                st.plotly_chart(fig)
        elif zone_frequenter=="Visulaisation des Zones de Forte Frequentations":
            epsilon=distance_dbscan(df)
            if epsilon!=0.0:
                df_cluster=make_cluster(df,epsilon)
                c=color(df_cluster)
                m=f.Map(location=[df_cluster["Latitude"].mean(),df_cluster["Longitude"].mean()],zoom_start=9)
                for index,row in df_cluster.iterrows():
                    f.CircleMarker(location=[row["Latitude"],row["Longitude"]],
                    raduis=0.3,
                    fill=True,
                    fill_opacity=1,
                    ).add_to(m)
                st_folium(m,width=1000)        
            else:
               df_cluster=make_cluster(df,0.02)
               m=f.Map(location=[df_cluster["Latitude"].mean(),df_cluster["Longitude"].mean()],zoom_start=9)
               for index,row in df_cluster.iterrows():
                    f.CircleMarker(location=[row["Latitude"],row["Longitude"]],
                    raduis=0.3,
                    fill=True,
                    fill_opacity=1,
                    ).add_to(m)
               st_folium(m,width=1000)
               generate_and_download_image()
    elif carte=="Carte de chaleur":
        options=["liste des Points","Carte des chaleurs"]
        carte_selected=st.radio("",options,index=0,horizontal=True)
        if carte_selected=="Carte des chaleurs":
            cart_chaleur_options=["Mode claire","Mode sombre"]
            cart_chaleur_selected=st.radio("",cart_chaleur_options,horizontal=True)
            if cart_chaleur_selected=="Mode claire":
                    epsilon=distance_dbscan(df)
                    if epsilon!=0.0:
                        file_path=os.path.abspath("heat_map_mode_claire.html")
                        if st.button("Telechargr la carte"):
                            generate_and_download_image_heatmap(file_path,"heat_map_mode_claire")
                        df_cluster=make_cluster(df,epsilon)
                        heat_map=f.Map(location=[df_cluster["Latitude"].mean(),df_cluster["Longitude"].mean()],zoom_start=9)
                        max_heat=df_cluster["cluster"].max()
                        min_heat=df_cluster["cluster"].min()
                        heatmap_data_max=[
                            [row["Latitude"],row["Longitude"],int(max_heat)] for index,row in df_cluster.iterrows()
                                    ]
                        heatmap_data_min=[
                            [row["Latitude"],row["Longitude"],int(min_heat)] for index,row in df_cluster.iterrows()
                                        ]
                        heatmap_max=HeatMap(heatmap_data_max,name="Eleve")
                        heatmap_min=HeatMap(heatmap_data_min,name="Faible")
                        heatmap_max.add_to(heat_map)
                        heatmap_min.add_to(heat_map)
                        #f.TileLayer('cartodbdark_matter').add_to(heat_map)
                        f.LayerControl().add_to(heat_map)
                        legend_html =f"""
                            <div style='
                                    position: fixed; 
                                    bottom: 100px; right: 40px; width: 260px; height: 350px; 
                                    background-color: white; 
                                    border:2px solid grey;
                                    right:60px;
                                    z-index:9999; 
                                    font-size:14px;
                            '>
                                    &nbsp;<b style='margin-bottom:250px'>Légende : Carte de chaleurs</b>
                                    <div style="margin-left:30px;margin-top:20px">
                                        <p>Du {df.tail(1)["Date_Enregistrement"].values[0]} au {df.head(1)["Date_Enregistrement"].values[0]}
                                    </div>
                                    <div style='display:flex;margin-bottom:10px'>
                                        <div style='width:40px;heigth:10px;background:#4B7946;border:1px solid white;'>
                                           <p></p>
                                        </div>
                                        &nbsp; Forêt classée
                                    </div>
                                    <div style='display:flex;margin-bottom:10px'>
                                        <div style='width:40px;heigth:10px;background:#ACE5F3;border:1px solid white;'>
                                           <p></p>
                                        </div>
                                        &nbsp; Plan d'eaux
                                    </div>
                                    &nbsp;<b style='margin-bottom:250px'>Aire de Présence</b>
                                    <div>
                                        <img src="data:image/png;base64,{base64.b64encode(open('image/aire_presence.png', 'rb').read()).decode('utf-8')}" width="190" height="20">
                                        <div style='display:flex'>
                                            <p style='margin-right:120px'>Faible</p>
                                            <p>Eleve</p>
                                        </div>
                                    </div>
                                    <div style='display:flex;'>
                                        <img src="data:image/png;base64,{base64.b64encode(open('image/elephant_marker.png', 'rb').read()).decode('utf-8')}" width="20" height="20">
                                        <b style='margin-left:20px'>{st.session_state["nom_elephant"]}</b>
                                    </div>
                                    <div style='display:flex;justify-content:center'>
                                        <img src="data:image/png;base64,{base64.b64encode(open('image/minef.png', 'rb').read()).decode('utf-8')}" width="60" height="60">
                                        <b  style='margin-top:15px'>DFRC</b>
                                    </div>
                            </div>"""
                        heat_map.get_root().html.add_child(f.Element(legend_html))
                        heat_map.save("heat_map_mode_claire.html")
                        map_html = heat_map._repr_html_()
                        st.components.v1.html(map_html, height=1500)
                        #st_folium(heat_map,width=1000)
                        #heat_map.save('carte_de_chaleur_claire.html')
                        #file_name='carte_de_chaleur_claire.html'
                        #nom_elephant=st.session_state['nom_elephant']
                        #generate_and_download_image_heatmap(file_name,nom_elephant)
                    else:
                        file_path=os.path.abspath("heat_map_mode_claire.html")
                        if st.button("Telecharger la carte des chaleurs"):
                            generate_and_download_image_heatmap(file_path,"heat_map_mode_claire.png")
                        df_cluster=make_cluster(df,0.02)
                        df_cluster['Latitude']=df_cluster['Latitude'].astype(float)
                        df_cluster['Longitude']=df_cluster['Longitude'].astype(float)
                        df['cluster']=df_cluster['cluster'].astype(int)
                        heat_map=f.Map(location=[df_cluster["Latitude"].mean(),df_cluster["Longitude"].mean()],zoom_start=9)
                        max_heat=df_cluster["cluster"].max().astype(int)
                        min_heat=df_cluster["cluster"].min().astype(int)
                        heatmap_data_max=[
                            [row["Latitude"],row["Longitude"],int(max_heat)] for index,row in df_cluster.iterrows()
                        ]
                        heatmap_data_min=[
                            [row["Latitude"],row["Longitude"],int(min_heat)] for index,row in df_cluster.iterrows()
                        ]
                        gradient_map=defaultdict(dict)
                        heatmap_max=HeatMap(heatmap_data_max,name="Eleve")
                        heatmap_min=HeatMap(heatmap_data_min,name="Faible")
                        heatmap_max.add_to(heat_map)
                        heatmap_min.add_to(heat_map)
                        f.LayerControl().add_to(heat_map)
                        legend_html =f"""
                            <div style='
                                    position: fixed; 
                                    bottom: 100px; width: 260px; height: 350px; 
                                    background-color: white; 
                                    border:2px solid grey;
                                    z-index:9999; 
                                    font-size:14px;
                            '>
                                    &nbsp;<b style='margin-bottom:250px'>Légende : Carte de chaleurs</b>
                                    <div style="margin-left:30px;margin-top:20px">
                                        <p>Du {df.tail(1)["Date_Enregistrement"].values[0]} au {df.head(1)["Date_Enregistrement"].values[0]}
                                    </div>
                                    <div style='display:flex;margin-bottom:10px'>
                                        <div style='width:40px;heigth:10px;background:#4B7946;border:1px solid white;'>
                                           <p></p>
                                        </div>
                                        &nbsp; Forêt classée
                                    </div>
                                    <div style='display:flex;margin-bottom:10px'>
                                        <div style='width:40px;heigth:10px;background:#ACE5F3;border:1px solid white;'>
                                           <p></p>
                                        </div>
                                        &nbsp; Plan d'eaux
                                    </div>
                                    &nbsp;<b style='margin-bottom:250px'>Aire de Présence</b>
                                    <div>
                                        <img src="data:image/png;base64,{base64.b64encode(open('image/aire_presence.png', 'rb').read()).decode('utf-8')}" width="190" height="20">
                                        <div style='display:flex'>
                                            <p style='margin-right:120px'>Faible</p>
                                            <p>Eleve</p>
                                        </div>
                                    </div>
                                    <div style='display:flex;'>
                                        <img src="data:image/png;base64,{base64.b64encode(open('image/elephant_marker.png', 'rb').read()).decode('utf-8')}" width="20" height="20">
                                        <b style='margin-left:20px'>{st.session_state["nom_elephant"]}</b>
                                    </div>
                                    <div style='display:flex;justify-content:center'>
                                        <img src="data:image/png;base64,{base64.b64encode(open('image/minef.png', 'rb').read()).decode('utf-8')}" width="60" height="60">
                                        <b  style='margin-top:15px'>DFRC</b>
                                    </div>
                            </div>"""
                        heat_map.get_root().html.add_child(f.Element(legend_html))
                        heat_map.save("heat_map_mode_claire.html")
                        map_html = heat_map._repr_html_()
                        st.components.v1.html(map_html, height=1500)
                        #st_folium(heat_map,width=1000)
                        #heat_map.save('carte_de_chaleur_claire.html')
                        #file_name='carte_de_chaleur_claire.html'
                        #nom_elephant=st.session_state['nom_elephant']
                        #generate_and_download_image_heatmap(file_name,nom_elephant)
            elif cart_chaleur_selected=="Mode sombre":
                    epsilon=distance_dbscan(df)
                    if epsilon!=0.0:
                        file_path=os.path.abspath("heat_map_mode_sombre.html")
                        if st.button("Télécharger la carte des chaleurs"):
                            generate_and_download_image_heatmap(file_path,"heat_map_mode_sombre")
                        df_cluster=make_cluster(df,epsilon)
                        heat_map=f.Map(location=[df_cluster["Latitude"].mean(),df_cluster["Longitude"].mean()],tiles='cartodbdark_matter',zoom_start=9)
                        max_heat=df_cluster["cluster"].max()
                        min_heat=df_cluster["cluster"].min()
                        heatmap_data_max=[
                            [row["Latitude"],row["Longitude"],int(max_heat)] for index,row in df_cluster.iterrows()
                                    ]
                        heatmap_data_min=[
                            [row["Latitude"],row["Longitude"],int(min_heat)] for index,row in df_cluster.iterrows()
                                        ]
                        heatmap_max=HeatMap(heatmap_data_max,name="Eleve")
                        heatmap_min=HeatMap(heatmap_data_min,name="Faible")
                        heatmap_max.add_to(heat_map)
                        heatmap_min.add_to(heat_map)
                        f.LayerControl().add_to(heat_map)
                        legend_html =f"""
                            <div style='
                                    position: fixed; 
                                    bottom: 100px; width: 260px; height: 350px; 
                                    background-color: white; 
                                    border:2px solid grey;
                                    z-index:9999; 
                                    font-size:14px;
                            '>
                                    &nbsp;<b style='margin-bottom:250px'>Légende : Carte de chaleurs</b>
                                    <div style="margin-left:30px;margin-top:20px">
                                        <p>Du {df.tail(1)["Date_Enregistrement"].values[0]} au {df.head(1)["Date_Enregistrement"].values[0]}
                                    </div>
                                    <div style='display:flex;margin-bottom:10px'>
                                        <div style='width:40px;heigth:10px;background:#4B7946;border:1px solid white;'>
                                           <p></p>
                                        </div>
                                        &nbsp; Forêt classée
                                    </div>
                                    <div style='display:flex;margin-bottom:10px'>
                                        <div style='width:40px;heigth:10px;background:#ACE5F3;border:1px solid white;'>
                                           <p></p>
                                        </div>
                                        &nbsp; Plan d'eaux
                                    </div>
                                    &nbsp;<b style='margin-bottom:250px'>Aire de Présence</b>
                                    <div>
                                        <img src="data:image/png;base64,{base64.b64encode(open('image/aire_presence.png', 'rb').read()).decode('utf-8')}" width="190" height="20">
                                        <div style='display:flex'>
                                            <p style='margin-right:120px'>Faible</p>
                                            <p>Eleve</p>
                                        </div>
                                    </div>
                                    <div style='display:flex;'>
                                        <img src="data:image/png;base64,{base64.b64encode(open('image/elephant_marker.png', 'rb').read()).decode('utf-8')}" width="20" height="20">
                                        <b style='margin-left:20px'>{st.session_state["nom_elephant"]}</b>
                                    </div>
                                    <div style='display:flex;justify-content:center'>
                                        <img src="data:image/png;base64,{base64.b64encode(open('image/minef.png', 'rb').read()).decode('utf-8')}" width="60" height="60">
                                        <b  style='margin-top:15px'>DFRC</b>
                                    </div>
                            </div>"""
                        heat_map.get_root().html.add_child(f.Element(legend_html))
                        heat_map.save("heat_map_mode_sombre.html")
                        map_html = heat_map._repr_html_()
                        st.components.v1.html(map_html, height=1500)
                        #st_folium(heat_map,width=1000)
                        #heat_map.save('carte_de_chaleur_sombre.html')
                        #file_name='carte_de_chaleur_sombre.html'
                        #nom_elephant=st.session_state['nom_elephant']
                        #generate_and_download_image_heatmap(file_name,nom_elephant)
                    else:
                        file_path=os.path.abspath("heat_map_mode_sombre.html")
                        if st.button("Telecharger la carte des chaleurs"):
                            generate_and_download_image_heatmap(file_path,"heatmap_mode_sombre")
                        df_cluster=make_cluster(df,0.02)
                        df_cluster['Latitude']=df_cluster['Latitude'].astype(float)
                        df_cluster['Longitude']=df_cluster['Longitude'].astype(float)
                        df['cluster']=df_cluster['cluster'].astype(int)
                        heat_map=f.Map(location=[df_cluster["Latitude"].mean(),df_cluster["Longitude"].mean()],tiles='cartodbdark_matter',zoom_start=9)
                        max_heat=df_cluster["cluster"].max().astype(int)
                        min_heat=df_cluster["cluster"].min().astype(int)
                        heatmap_data_max=[
                            [row["Latitude"],row["Longitude"],int(max_heat)] for index,row in df_cluster.iterrows()
                        ]
                        heatmap_data_min=[
                            [row["Latitude"],row["Longitude"],int(min_heat)] for index,row in df_cluster.iterrows()
                        ]
                        gradient_map=defaultdict(dict)
                        heatmap_max=HeatMap(heatmap_data_max,name="Eleve")
                        heatmap_min=HeatMap(heatmap_data_min,name="Faible")
                        heatmap_max.add_to(heat_map)
                        heatmap_min.add_to(heat_map)
                        f.LayerControl().add_to(heat_map)
                        legend_html =f"""
                            <div style='
                                    position: fixed; 
                                    bottom: 100px;width: 260px; height: 350px; 
                                    background-color: white; 
                                    border:2px solid grey;
                                    z-index:9999; 
                                    font-size:14px;
                            '>
                                    &nbsp;<b style='margin-bottom:250px'>Légende : Carte de chaleurs</b>
                                    <div style="margin-left:30px;margin-top:20px">
                                        <p>Du {df.tail(1)["Date_Enregistrement"].values[0]} au {df.head(1)["Date_Enregistrement"].values[0]}
                                    </div>
                                    <div style='display:flex;margin-bottom:10px'>
                                        <div style='width:40px;heigth:10px;background:#4B7946;border:1px solid white;'>
                                           <p></p>
                                        </div>
                                        &nbsp; Forêt classée
                                    </div>
                                    <div style='display:flex;margin-bottom:10px'>
                                        <div style='width:40px;heigth:10px;background:#ACE5F3;border:1px solid white;'>
                                           <p></p>
                                        </div>
                                        &nbsp; Plan d'eaux
                                    </div>
                                    &nbsp;<b style='margin-bottom:250px'>Aire de Présence</b>
                                    <div>
                                        <img src="data:image/png;base64,{base64.b64encode(open('image/aire_presence.png', 'rb').read()).decode('utf-8')}" width="190" height="20">
                                        <div style='display:flex'>
                                            <p style='margin-right:120px'>Faible</p>
                                            <p>Eleve</p>
                                        </div>
                                    </div>
                                    <div style='display:flex;'>
                                        <img src="data:image/png;base64,{base64.b64encode(open('image/elephant_marker.png', 'rb').read()).decode('utf-8')}" width="20" height="20">
                                        <b style='margin-left:20px'>{st.session_state["nom_elephant"]}</b>
                                    </div>
                                    <div style='display:flex;justify-content:center'>
                                        <img src="data:image/png;base64,{base64.b64encode(open('image/minef.png', 'rb').read()).decode('utf-8')}" width="60" height="60">
                                        <b  style='margin-top:15px'>DFRC</b>
                                    </div>
                            </div>"""
                        heat_map.get_root().html.add_child(f.Element(legend_html))
                        heat_map.save("heat_map_mode_sombre.html")
                        map_html = heat_map._repr_html_()
                        st.components.v1.html(map_html, height=1800)
                        #st_folium(heat_map,width=1000)
                        #heat_map.save('carte_de_chaleur_sombre.html')
                        #file_name='carte_de_chaleur_sombre.html'
                        #nom_elephant=st.session_state['nom_elephant']
                        #generate_and_download_image_heatmap(file_name,nom_elephant)
        elif carte_selected=="liste des Points":
            data_display=df[["Longitude","Latitude","Date_Enregistrement","Heure_Enregistrement","temps"]]
            st.subheader("Données cartographiques")
            st.text(f"Nom Elephant:{st.session_state['nom_elephant']}")
            st.text(f"Nombre de Position géographique: {len(df)}")
            st.text(f"Date debut: {df.tail(1)['Date_Enregistrement'].values[0]}")
            st.text(f"Date Fin: {df.head(1)['Date_Enregistrement'].values[0]}")
            st.dataframe(data_display)
            col1,col2=st.columns(2)
            data_for_distance=dist_group_temps(df)
            dict_group_for_distance={name:group for name,group in data_for_distance}
            dataframe_nuit=dict_group_for_distance.get(("Nuit",))
            dataframe_jour=dict_group_for_distance.get(("Jour",))
            distance_nuit=distance(dataframe_nuit)
            distance_jour=distance(dataframe_jour)
            distance_total_parcourue=distance_total(df)
            distance_par_jour_nuit= distance_total_jour_nuit(df)
            with col1:

                st.write("Distance Totale en Km")
                df_distance=pd.DataFrame({"Distance_total":[f"{distance_total_parcourue} Km"]})
                st.dataframe(df_distance)
            with col2:
                st.write("Distance de Nuit et Jour en Km")
                data_n_j=pd.DataFrame({"Distance Nuit":[f"{distance_nuit} Km"],"Distance Jour":[f"{distance_jour} Km"]})
                st.dataframe(distance_par_jour_nuit)
            col4,col5,col6,col7=st.columns(4)
            with col5:
                dist_nuit=distance_par_jour_nuit["Distance_Nuit"].iloc[0]
                dist_jour=distance_par_jour_nuit["Distance_Jour"].iloc[0]
                data_sector={"Distance":[dist_nuit,dist_jour],"Type":["Nuit","Jour"]}
                df_sector=pd.DataFrame(data_sector)
                form=px.pie(df_sector,names="Type",values="Distance",title=f"Distance Parcourue Jours et Nuits {st.session_state['nom_elephant']}",width=400,height=400,color_discrete_sequence=["#6F00FF","#17B169"])
                st.plotly_chart(form)
                #ON EST ICI
            options_map=["Afficher tous les déplacements","Affichage par période","afficher les deplacements par date","Surface occupée"]
            map_selected=st.radio("",options_map,horizontal=True)
            if map_selected=="Afficher tous les déplacements":
                file_path=os.path.abspath("deplacement_total.html")
                contenue_fichier=""
                if st.button("Cliquez ici pour telecharger la carte"):
                    generate_and_download_image_heatmap(file_path,"deplacement_total")
                map=f.Map(location=[df["Latitude"].astype(float).mean(),df["Longitude"].astype(float).mean()],zoom_start=9)
                latitude=df["Latitude"].astype(float)
                longitude=df["Longitude"].astype(float)
                first_lat=df["Latitude"].head(1).values[0]
                first_long=df["Longitude"].head(1).values[0]
                last_lat=df["Latitude"].tail(1).values[0]
                last_long=df["Longitude"].tail(1).values[0]
                data=list(zip(latitude,longitude))
                icon=f.CustomIcon("image/elephant_marker.png",icon_size=(11,11))
                f.Marker([first_lat,first_long],icon=icon,popup="Point de Depart").add_to(map)
                icon2=f.CustomIcon("image/elephant_marker.png",icon_size=(11,11))
                f.Marker([last_lat,last_long],icon=icon2,popup="Point d'arrivé").add_to(map)
                AntPath(data,delay=400,weight=3,color="red",pulse_color="blue",dash_array=[50,60],reverse=True).add_to(map)
                legend_html =f"""
                    <div style='
                            position: fixed; 
                            bottom: 100px; right: 40px; width: 260px; height: 250px; 
                            background-color: white; 
                            border:2px solid grey;
                            right:60px;
                            z-index:9999; 
                            font-size:14px;
                    '>
                    &nbsp;<b style='margin-bottom:250px'>Légende:</b>
                    <div style='display:flex;'>
                        <p style='color:purple'>---------------</p>
                        <p>Trajet de l'éléphant</p>
                    </div>
                    <div style="margin-left:30px">
                        <p>Du {df.tail(1)["Date_Enregistrement"].values[0]} au {df.head(1)["Date_Enregistrement"].values[0]}
                    </div>
                    <div style='display:flex;margin-bottom:10px'>
                        <div style='width:40px;heigth:10px;background:#4B7946;border:1px solid white;'>
                           <p></p>
                        </div>
                        &nbsp; Forêt classée
                    </div>
                    <div style='display:flex'>
                        <div style='width:40px;heigth:10px;background:#ACE5F3;border:1px solid white;'>
                           <p></p>
                        </div>
                        &nbsp; Plan d'eaux
                    </div>
                    <p>Distance Total:<b> {round(distance_total_parcourue,5)} Km</b></p>
                    <div style='display:flex;'>
                        <img src="data:image/png;base64,{base64.b64encode(open('image/elephant_marker.png', 'rb').read()).decode('utf-8')}" width="20" height="20">
                        <b style='margin-left:20px'>{st.session_state["nom_elephant"]}</b>
                    </div>
                    <div style='display:flex;justify-content:center'>
                        <img src="data:image/png;base64,{base64.b64encode(open('image/minef.png', 'rb').read()).decode('utf-8')}" width="60" height="60">
                       
                    </div>
                 </div>"""
                map.get_root().html.add_child(f.Element(legend_html))
                map.save("deplacement_total.html")
                map_html = map._repr_html_()
                st.components.v1.html(map_html, height=1500)

                map.get_root().html.add_child(f.Element(legend_html))
                map.save("deplacement_jour_nuit.html")
                map_html = map._repr_html_()
                st.components.v1.html(map_html, height=1500)
            elif map_selected=="Affichage par période":
                dfPeriode=df.copy()
                col1,col2,col3=st.columns(3)
                with col1:
                    periode1=st.date_input("Entrer la premiere date",value=df.tail(1)["Date_Enregistrement"].values[0],min_value=df.tail(1)["Date_Enregistrement"].values[0],max_value=df.head(1)["Date_Enregistrement"].values[0])
                with col3:
                    periode2=st.date_input("Entrer la deuxieme date",value=df.head(1)["Date_Enregistrement"].values[0],min_value=df.tail(1)["Date_Enregistrement"].values[0],max_value=df.head(1)["Date_Enregistrement"].values[0])
                if periode1<periode2:
                    st.text(f"Periode : {periode1} au {periode2}")
                    col1,col2,col3=st.columns([15,30,15])
                    df_periode_afficher=df.copy()
                    df_periode_afficher=df_periode_afficher.set_index("Date_Enregistrement",drop=False)
                    df_periode_filter=df_periode_afficher[(df_periode_afficher["Date_Enregistrement"]>=periode1) & (df_periode_afficher["Date_Enregistrement"]<=periode2)]
                    distance_periode=df_periode_filter.groupby(level="Date_Enregistrement",axis=0).apply(distance).sum()
                    distance_serie_filter=df_periode_filter.groupby(level="Date_Enregistrement",axis=0).apply(distance)
                    distance_dataframe_filter=distance_serie_filter.to_frame()
                    distance_dataframe_filter.index.name="Date"
                    distance_dataframe_filter.columns=["Distance_En_Km"]
                    distance_dataframe_for_graphique= distance_dataframe_filter.reset_index(drop=False)
                    fig=px.line(distance_dataframe_for_graphique,x="Date",y="Distance_En_Km",width=1000,height=500,title=f"Distance Parcourue {st.session_state['nom_elephant']} dans la Periode du {df_periode_filter.tail(1)['Date_Enregistrement'].values[0]} au {df_periode_filter.head(1)['Date_Enregistrement'].values[0]}")
                    st.plotly_chart(fig,selection_mode="points")
                    st.write("Sur la carte, Cliquer sur l' Icône pour plus d'informations ")
                    st.image("image/elephant_marker.png",width=20)
                    #Icone arrivé
                    icone_arrivee=f.CustomIcon("image/elephant_marker.png",icon_size=(16,16))
                    html=f"""
                        <div style="font-size:13px"> 
                            <em>Point d'arrivée</em> 
                            <h5>Date:{df_periode_filter.head(1)["Date_Enregistrement"].values[0]}</h5>
                            <p>Longitude: {float(df_periode_filter.head(1)["Longitude"])}</p>
                            <p>Latitude: {float(df_periode_filter.head(1)["Latitude"])}</p>
                            <p>Distance: {distance_periode}  Km</p>
                        <div/>
                        """ 
                    map=f.Map(location=[df.head(1)["Latitude"].values[0],df["Longitude"].astype(float).mean()],zoom_start=9)
                    html_display=iframe=f.IFrame(html,width=200,height=200)
                    popup=f.Popup(html=html_display,max_width=160)
                    f.Marker(location=list((float(df_periode_filter.head(1)["Latitude"].values[0]),float(df_periode_filter.head(1)["Longitude"].values[0]))),icon=icone_arrivee,popup=popup).add_to(map)
                    #Icone arrivé

                    #Instruction 
                    icone_depart=f.CustomIcon("image/elephant_marker.png",icon_size=(16,16))
                    html=f"""
                        <div style="font-size:13px">
                            <em>Point départ</em> 
                            <h5>Date:{df_periode_filter.tail(1)["Date_Enregistrement"].values[0]}</h5>
                            <p>Longitude: {float(df_periode_filter.tail(1)["Longitude"])}</p>
                            <p>Latitude: {float(df_periode_filter.tail(1)["Latitude"])}</p>
                        <div/>
                        """ 
                    #Instruction 
                    html_display=iframe=f.IFrame(html,width=200,height=200)
                    popup=f.Popup(html=html_display,max_width=160)
                    f.Marker(location=list((float(df_periode_filter.tail(1)["Latitude"].values[0]),float(df_periode_filter.tail(1)["Longitude"].values[0]))),icon=icone_depart,popup=popup).add_to(map)
                    longitudes=df_periode_filter["Longitude"].astype(float)
                    latitudes=df_periode_filter["Latitude"].astype(float)
                    data_filter=list(zip(latitudes,longitudes))
                    AntPath(data_filter,delay=1000,weight=3,color="red",pulse_color="blue",dash_array=[10,10],reverse=True).add_to(map)
                    legend_html =f"""
                            <div style='
                                    position: fixed; 
                                    bottom: 100px; right: 40px; width: 300px; height: 300px; 
                                    background-color: white; 
                                    border:2px solid grey;
                                    right:60px;
                                    z-index:9999; 
                                    font-size:14px;
                            '>
                            &nbsp;<b style='margin-bottom:250px'>Légende: {st.session_state["nom_elephant"]}</b><br>
                            <p style='margin-left:30px'>{df_periode_filter.tail(1)["Date_Enregistrement"].values[0]} au {df_periode_filter.head(1)["Date_Enregistrement"].values[0]}</p><br>
                            <div style='display:flex;margin-bottom:10px'>
                                <div style='width:40px;heigth:10px;background:#4B7946;border:1px solid white;'>
                                   <p></p>
                                </div>
                                &nbsp; Forêt classée
                            </div>
                            <div style='display:flex'>
                                <div style='width:40px;heigth:10px;background:#ACE5F3;border:1px solid white;'>
                                   <p></p>
                                </div>
                                &nbsp; Plan d'eaux
                            </div><br>
                            <div style='display:flex;'>
                                <img src="data:image/png;base64,{base64.b64encode(open('image/elephant_marker.png', 'rb').read()).decode('utf-8')}" width="20" height="20">
                                <b style='margin-left:20px'>Positions de l'éléphant</b>
                            </div>
                            <div style='display:flex;justify-content:center'>
                                <img src="data:image/png;base64,{base64.b64encode(open('image/minef.png', 'rb').read()).decode('utf-8')}" width="60" height="60">
                            </div>
                            <div style='display:inline-block;margin-left:70px'>
                                <p>Distance effectuée <strong>{distance_periode}</strong>  Km</p>
                            </div>
                    
                        </div>"""
                    map.get_root().html.add_child(f.Element(legend_html))
                    map.save("deplacement_total.html")
                    map_html = map._repr_html_()
                    st.components.v1.html(map_html, height=1500)
                else:
                    st.write("Veuillez saisir une periode valable")
            elif map_selected=="afficher les deplacements par date":
                date_selected=[]
                df_for_date_route=df.copy()
                df_unique=df_for_date_route.drop_duplicates(subset="Date_Enregistrement")
                #st.dataframe(df_unique)
                df_unique=df_unique.set_index("Date_Enregistrement",drop=False)
                for index,row in df_unique.iterrows():
                    date_selected.append(index)
                col1,col2,col3=st.columns([1,2,1])
                with col2:
                    date=st.selectbox("Choisir une Date",options=date_selected)
                st.write("Pour plus d'information cliquez sur l'icone de léléphant qui est situer sur la carte")
                st.image("image/elephant_marker.png",width=20)
                df_display=df_for_date_route[df_for_date_route["Date_Enregistrement"]==date]
                df_display_info=df_display[["Longitude","Latitude","Heure_Enregistrement","temps"]]
                df_display_info=df_display_info.sort_values(by="Heure_Enregistrement",ascending=True)
                col3,col4,col5=st.columns([1,5,1])
                latitudes=df_display_info["Latitude"].astype(float)
                longitudes=df_display_info["Longitude"].astype(float)
                data_line=list(zip(latitudes,longitudes))
                st.write("")
                map=f.Map(location=[df_display_info.tail(1)["Latitude"].values[0],df_display_info.tail(1)["Longitude"].values[0]],zoom_start=9)
                data_example=df_display_info.reset_index(drop=True)
                dist=[0]
                heures=[]
                for i in range(0,len(data_example)):
                  heures.append(data_example.loc[i,"Heure_Enregistrement"])
                time_delta=[0.00000001]
                for i in range(0,len(heures)):
                        if i+1<len(heures):
                            datetime1 = datetime.datetime.combine(datetime.datetime.today(),heures[i+1])
                            datetime2 = datetime.datetime.combine(datetime.datetime.today(), heures[i])
                            difference = datetime1 - datetime2
                            time_delta.append((difference.total_seconds()))
                for i in range(0,len(data_example)):
                  if i+1<len(data_example):
                    point1=(data_example.loc[i,"Latitude"],data_example.loc[i,"Longitude"])
                    point2=(data_example.loc[i+1,"Latitude"],data_example.loc[i+1,"Longitude"])
                    dist.append(geodesic(point1,point2).km)
                for index,rows in data_example.iterrows():
                    distance_m_s=(dist[index]*1000)/(time_delta[index])
                    distance_km_h=distance_m_s*3.6
                    if rows["temps"]=="Nuit":
                        html=f"""
                        <div style="font-size:14px;height:20">
                            <p>Latitude: {rows["Latitude"]}</p>
                            <p>Longitude: {rows["Longitude"]}</p>
                            <p>Distance :{dist[index]} </p>
                            <p>Vitesse: {round(distance_m_s,4)} m/s</p>
                        <div/>
                        """ 
                        #Instruction 
                        html_display=iframe=f.IFrame(html,width=300,height=100)
                        popup=f.Popup(html=html_display)
                        icon1=f.CustomIcon("image/elephant_marke_red.png",icon_size=(16,16))
                        f.Marker(location=[float(rows["Latitude"]),float(rows["Longitude"])],icon=icon1,tooltip=f"Heure: {rows['Heure_Enregistrement']}",popup=popup).add_to(map)
                        AntPath(data_line,delay=1000,weight=3,color="yellow",pulse_color="blue",dash_array=[10,10],reverse=False).add_to(map)
                    elif rows["temps"]=="Jour" :
                        html=f"""
                        <div style="font-size:14px">
                            <p>Latitude: {rows["Latitude"]}</p>
                            <p>Longitude: {rows["Longitude"]}</p>
                            <p>Distance :{dist[index]} </p>
                            <p>Vitesse: {round(distance_m_s,4)} m/s</p>
                        <div/>
                        """ 
                        #Instruction
                        html_display=iframe=f.IFrame(html,width=300,height=100)
                        popup=f.Popup(html=html_display)
                        icon1=f.CustomIcon("image/elephant_marker.png",icon_size=(16,16))
                        f.Marker(location=[rows["Latitude"],rows["Longitude"]],icon=icon1,tooltip=f" Heure: {rows['Heure_Enregistrement']}",popup=popup).add_to(map)
                legend_html =f"""
                    <div style='
                            position: fixed; 
                            bottom: 100px; right: 40px; width: 300px; height: 300px; 
                            background-color: white; 
                            border:2px solid grey;
                            right:60px;
                            z-index:9999; 
                            font-size:14px;
                    '>
                    &nbsp;<b style='margin-bottom:250px'>Légende:Positions de {st.session_state["nom_elephant"]}</b><br>
                    
                    <div style='display:flex;margin-bottom:10px'>
                        <div style='width:40px;heigth:10px;background:#4B7946;border:1px solid white;'>
                           <p></p>
                        </div>
                        &nbsp; Forêt classée
                    </div>
                    <div style='display:flex'>
                        <div style='width:40px;heigth:10px;background:#ACE5F3;border:1px solid white;'>
                           <p></p>
                        </div>
                        &nbsp; Plan d'eaux
                    </div><br>
                    <div style='display:flex;'>
                        <img src="data:image/png;base64,{base64.b64encode(open('image/elephant_marker.png', 'rb').read()).decode('utf-8')}" width="20" height="20">
                        <b style='margin-left:20px'>Position de Jour</b>
                    </div><br>
                    <div style='display:flex;'>
                        <img src="data:image/png;base64,{base64.b64encode(open('image/elephant_marke_red.png', 'rb').read()).decode('utf-8')}" width="20" height="20">
                        <b style='margin-left:20px'>Position de Nuit</b>
                    </div>
                    <div style='display:flex;justify-content:center'>
                        <img src="data:image/png;base64,{base64.b64encode(open('image/minef.png', 'rb').read()).decode('utf-8')}" width="60" height="60">
                    </div>
                    <div style='display:inline-block;margin-left:70px'>
                        <p>Distance effectuée <strong>{distance_periode_jour(dist)}</strong>  Km</p>
                    </div>
                    
                 </div>"""
                map.get_root().html.add_child(f.Element(legend_html))
                map.save("deplacement_total.html")
                map_html = map._repr_html_()
                st.components.v1.html(map_html, height=1500)
            elif map_selected=="Surface occupée":
                tableauChoix=["Surface total","Surface Par Période"]
                choix=st.radio("",tableauChoix,horizontal=True)
                dfSurface=df.copy()
                if choix=="Surface total":
                    locations=[]
                    latitudePosition=float(dfSurface.head(1)["Latitude"].values[0])
                    longitudePosition=float(dfSurface.head(1)["Longitude"].values[0])
                    map=f.Map((latitudePosition,longitudePosition),zoom_start=9)
                    #Draw polygon on folium
                    for index, row in dfSurface.iterrows():
                        latitude=float(row["Latitude"])
                        longitude=float(row["Longitude"])
                        cordonnées=[latitude,longitude]
                        locations.append(cordonnées)
                    html=f"""
                    <div style="font-size:14px;height:5">
                        <p>Surface occupée par {st.session_state["nom_elephant"]}</p>
                        <p>Dans la période du </p>
                        
                    <div/>
                    """ 
                    #Instruction
                    cordonnées=[[float(lat),float(long)] for lat,long in list(zip(df["Latitude"],df["Longitude"]))]
                    polygon=Polygon(cordonnées)
                    gdf=gpd.GeoDataFrame(index=[0],crs="EPSG:4326",geometry=[polygon])
                    surfaceMetreCaree=gdf.area[0]
                    html_display=iframe=f.IFrame(html,width=300,height=100)
                    popup=f.Popup(html=html_display)
                    f.Polygon(locations=locations,color="Blue",
                            weight=1,
                            fill_color="Blue",
                            fill_opacity=0.4,
                            fill=True,tooltip="Surface"
                            ).add_to(map)
                    legend_html =f"""
                            <div style='
                                    position: fixed; 
                                    bottom: 100px; right: 40px; width: 300px; height: 300px; 
                                    background-color: white; 
                                    border:2px solid grey;
                                    right:60px;
                                    z-index:9999; 
                                    font-size:14px;
                            '>
                            &nbsp;<b style='margin-bottom:250px'>Légende: {st.session_state["nom_elephant"]}</b><br>
                            <p style='margin-left:30px'></p><br>
                            <div style='display:flex;margin-bottom:10px'>
                                <div style='width:40px;heigth:10px;background:#4B7946;border:1px solid white;'>
                                   <p></p>
                                </div>
                                &nbsp; Forêt classée
                            </div>
                            <div style='display:flex'>
                                <div style='width:40px;heigth:10px;background:#ACE5F3;border:1px solid white;'>
                                   <p></p>
                                </div>
                                &nbsp; Plan d'eaux
                            </div><br>
                            <div style='display:flex'>
                                <div style='width:40px;heigth:10px;background: #0000FF;border:1px solid white;'>
                                   <p></p>
                                </div>
                                &nbsp; Surface Occupée
                            </div><br>
                            <div style='display:flex;justify-content:center'>
                                <img src="data:image/png;base64,{base64.b64encode(open('image/minef.png', 'rb').read()).decode('utf-8')}" width="60" height="60">
                            </div>
                            
                             <p style='margin-left:70px'>Surface: {surfaceMetreCaree:0.6f} m²</p>
                        </div>"""
                    map.get_root().html.add_child(f.Element(legend_html))
                    map.save("deplacement_total.html")
                    map_html = map._repr_html_()
                    st.components.v1.html(map_html,height=1500)
                elif choix=="Surface Par Période":
                    cordonnées=[]
                    col1,col2,col3=st.columns([5,10,5])
                    with col1:
                        periode1=st.date_input("Entrer la Premiere date",value=dfSurface.tail(1)["Date_Enregistrement"].values[0],min_value=dfSurface.tail(1)["Date_Enregistrement"].values[0],max_value=dfSurface.head(1)["Date_Enregistrement"].values[0])
                    with col3:
                        periode2=st.date_input("Entrer la Deuxieme date",value=dfSurface.head(1)["Date_Enregistrement"].values[0],min_value=dfSurface.tail(1)["Date_Enregistrement"].values[0],max_value=dfSurface.head(1)["Date_Enregistrement"].values[0])
                    dfForPeriode=dfSurface.set_index("Date_Enregistrement",drop=False)
                    dfForPeriode1=dfForPeriode[(dfForPeriode["Date_Enregistrement"]>=periode1) & (dfForPeriode["Date_Enregistrement"]<=periode2)]
                    cordonnées=[[float(lat),float(long)] for lat,long in list(zip(dfForPeriode1["Latitude"],dfForPeriode1["Longitude"]))]
                    polygon=Polygon(cordonnées)
                    gdf=gpd.GeoDataFrame(index=[0],crs="EPSG:4326",geometry=[polygon])
                    surfaceMetreCaree=gdf.area[0]
                    html=f"""
                        <div style="font-size:13px"> 
                            <h5>Surface occupé par :{st.session_state["nom_elephant"]}</h5>
                            <p>Surface : {surfaceMetreCaree}</p>
                        <div/>
                        """ 
                    html_display=iframe=f.IFrame(html,width=200,height=200)
                    popup=f.Popup(html=html_display,max_width=160)
                    map=f.Map(location=[dfForPeriode1.head(1)["Latitude"].values[0],dfForPeriode1.head(1)["Longitude"].values[0]],zoom_start=9)
                    f.Polygon(locations=cordonnées,color="Blue",
                            weight=1,
                            fill_color="Blue",
                            fill_opacity=0.4,
                            fill=True,tooltip="Surface").add_to(map)
                    legend_html =f"""
                            <div style='
                                    position: fixed; 
                                    bottom: 100px; right: 40px; width: 300px; height: 300px; 
                                    background-color: white; 
                                    border:2px solid grey;
                                    right:60px;
                                    z-index:9999; 
                                    font-size:14px;
                            '>
                            &nbsp;<b style='margin-bottom:250px'>Légende: {st.session_state["nom_elephant"]}</b><br>
                            <p style='margin-left:30px'></p><br>
                            <div style='display:flex;margin-bottom:10px'>
                                <div style='width:40px;heigth:10px;background:#4B7946;border:1px solid white;'>
                                   <p></p>
                                </div>
                                &nbsp; Forêt classée
                            </div>
                            <div style='display:flex'>
                                <div style='width:40px;heigth:10px;background:#ACE5F3;border:1px solid white;'>
                                   <p></p>
                                </div>
                                &nbsp; Plan d'eaux
                            </div><br>
                            <div style='display:flex'>
                                <div style='width:40px;heigth:10px;background: #0000FF;border:1px solid white;'>
                                   <p></p>
                                </div>
                                &nbsp; Surface Occupée
                            </div><br>
                            <div style='display:flex;justify-content:center'>
                                <img src="data:image/png;base64,{base64.b64encode(open('image/minef.png', 'rb').read()).decode('utf-8')}" width="60" height="60">
                            </div>
                            
                             <p style='margin-left:70px'>Surface: {surfaceMetreCaree:0.6f} m²</p>
                        </div>"""
                    map.get_root().html.add_child(f.Element(legend_html))
                    map.save("deplacement_total.html")
                    map_html = map._repr_html_()
                    st.components.v1.html(map_html,height=1500)

                        




            
                


