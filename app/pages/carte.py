import streamlit as st
import folium as f
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
import datetime
import requests
import plotly.express as px
import pandas as pd
from fonctionnalite.zone_frequentation import distance_dbscan,make_cluster,find_location,number_in_index,color,generate_and_download_image,generate_and_download_image_heatmap
from fonctionnalite.distance import distance,dist_jour_nuit,distance_jour_km,dist_group_temps
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
if "df" not in st.session_state:
    st.write("Veuillez Charger un fichier avant de continuer")
else:
    df=st.session_state["df"]
    df=df.sort_values(by="Date_Enregistrement",ascending=False)
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
            distance_total=distance_nuit+distance_jour
            with col1:
                st.write("Distance Totale en Km")
                df_distance=pd.DataFrame({"Distance_total":[f"{distance_total} Km"]})
                st.dataframe(df_distance)
            with col2:
                st.write("Distance de Nuit et Jour en Km")
                data_n_j=pd.DataFrame({"Distance Nuit":[f"{distance_nuit} Km"],"Distance Jour":[f"{distance_jour} Km"]})
                st.dataframe(data_n_j)
            col4,col5,col6,col7=st.columns(4)
            with col5:
                data_sector={"Distance":[distance_nuit,distance_jour],"Type":["Nuit","Jour"]}
                df_sector=pd.DataFrame(data_sector)
                form=px.pie(df_sector,names="Type",values="Distance",title=f"Distance Parcourue Jours et Nuits {st.session_state['nom_elephant']}",width=400,height=400,color_discrete_sequence=["#6F00FF","#17B169"])
                st.plotly_chart(form)
            options_map=["Afficher tous les déplacements","Afficher les déplacements de Nuit et Jour"]
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
                    <p>Distance Total:<b> {round(distance_total,5)} Km</b></p>
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
            else:
                map=f.Map(location=[df["Latitude"].astype(float).mean(),df["Longitude"].astype(float).mean()],zoom_start=10)
                latitude=df["Latitude"].astype(float)
                longitude=df["Longitude"].astype(float)
                first_lat=df["Latitude"].head(1).values[0]
                first_long=df["Longitude"].head(1).values[0]
                last_lat=df["Latitude"].tail(1).values[0]
                last_long=df["Longitude"].tail(1).values[0]
                icon1=f.CustomIcon("image/elephant_marker.png",icon_size=(11,11))
                icon2=f.CustomIcon("image/elephant_marker.png",icon_size=(11,11))
                data_nuit_jour =dist_group_temps(df)
                dict_group_nuit_jour={name:group for name,group in data_nuit_jour}
                option_nuit_jour=["Nuit","Jour","Nuit et Jour"]
                option_nuit_jour_select=st.radio("",option_nuit_jour,horizontal=True)
                if option_nuit_jour_select=="Jour":
                    file_name=os.path.abspath("deplacement_de_jour.html")
                    if st.button("Telecharger la carte"):
                        generate_and_download_image_heatmap(file_name,"deplacement_de_jour")
                    dict_jour=dict_group_nuit_jour.get(("Jour",))
                    f.Marker([dict_jour.head(1)["Latitude"].values[0],dict_jour.head(1)["Longitude"].values[0]],icon=icon1).add_to(map)
                    f.Marker([dict_jour.tail(1)["Latitude"].values[0],dict_jour.tail(1)["Longitude"].values[0]],icon=icon2).add_to(map)
                    data_jour=list(zip(dict_jour["Latitude"].astype(float),dict_jour["Longitude"].astype(float)))
                    AntPath(data_jour,delay=1000,weight=3,color="white",dash_array=[10,20],pulse_color="green",reverse=True).add_to(map)
                    legend_html =f"""
                    <div style='
                                position: fixed; 
                                bottom: 100px; right: 20px; width: 260px; height: 250px; 
                                background-color: white; +
                                right:60px;
                                z-index:9999; 
                                font-size:14px;
                        '>
                        &nbsp;<b style='margin-bottom:250px'>Légende</b>
                        <div style='display:flex;'>
                            <p style='color:green'>---------------</p>
                            <p>Trajet de Jour</p>
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
                        <p>Distance total de Jour:<b> {round(distance_jour,5)} Km</b></p>
                        <div style='display:flex;'>
                            <img src="data:image/png;base64,{base64.b64encode(open('image/elephant_marker.png', 'rb').read()).decode('utf-8')}" width="20" height="20">
                            <b style='margin-left:20px'>{st.session_state["nom_elephant"]}</b>
                        </div>
                        <div style='display:flex;justify-content:center'>
                            <img src="data:image/png;base64,{base64.b64encode(open('image/minef.png', 'rb').read()).decode('utf-8')}" width="60" height="60">
                        </div>
                 </div>"""
                    map.get_root().html.add_child(f.Element(legend_html))
                    map.save("deplacement_de_jour.html")
                    map_html=map._repr_html_()
                    st.components.v1.html(map_html, height=1500)
                    #st_folium(map,width=1000)
                elif option_nuit_jour_select=="Nuit":
                    file_path=os.path.abspath('deplacement_nuit.html')
                    if st.button("Telecharger la carte"):
                        generate_and_download_image_heatmap(file_path,"deplacement de Nuit")
                    dict_nuit=dict_group_nuit_jour.get(("Nuit",))
                    f.Marker([dict_nuit.head(1)["Latitude"].values[0],dict_nuit.head(1)["Longitude"].values[0]],icon=icon1,popup="Point départ").add_to(map)
                    f.Marker([dict_nuit.tail(1)["Latitude"].values[0],dict_nuit.tail(1)["Longitude"].values[0]],icon=icon2,popup="Point d'arrivée").add_to(map)
                    data_nuit=list(zip(dict_nuit["Latitude"].astype(float),dict_nuit["Longitude"].astype(float)))
                    AntPath(data_nuit,delay=1000,weight=3,color="white",dash_array=[10,20],pulse_color="blue",reverse=True).add_to(map)
                    legend_html =f"""
                    <div style='
                            position: fixed; 
                                bottom: 100px; width: 260px; height: 250px; 
                                background-color: white; 
                                border:2px solid grey;
                                right:40px;
                                z-index:9999; 
                                font-size:14px;
                        '>
                        &nbsp;<b style='margin-bottom:250px'>Légende</b>
                        <div style='display:flex;'>
                            <p style='color:blue'>---------------</p>
                            <p>Trajet de nuit</p>
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
                        <p>Distance total de Nuit:<b> {round(distance_nuit,5)} Km</b></p>
                        <div style='display:flex;'>
                            <img src="data:image/png;base64,{base64.b64encode(open('image/elephant_marker.png', 'rb').read()).decode('utf-8')}" width="20" height="20">
                            <b style='margin-left:20px'>{st.session_state["nom_elephant"]}</b>
                        </div>
                        <div style='display:flex;justify-content:center'>
                            <img src="data:image/png;base64,{base64.b64encode(open('image/minef.png', 'rb').read()).decode('utf-8')}" width="60" height="60">   
                        </div>

                 </div>"""
                    map.get_root().html.add_child(f.Element(legend_html))
                    map.save("deplacement_nuit.html")
                    map_html=map._repr_html_()
                    st.components.v1.html(map_html, height=1500)
                else:
                    file_path=os.path.abspath("deplacement_jour_nuit.html")
                    if st.button("Telecharger la carte"):
                        generate_and_download_image_heatmap(file_path,"deplacement_jour_nuit")
                    dict_jour=dict_group_nuit_jour.get(("Jour",))
                    data_jour=list(zip(dict_jour["Latitude"].astype(float),dict_jour["Longitude"].astype(float)))
                    dict_nuit=dict_group_nuit_jour.get(("Nuit",))
                    data_nuit=list(zip(dict_nuit["Latitude"].astype(float),dict_nuit["Longitude"].astype(float)))
                    icon=f.CustomIcon("image/elephant_marker.png",icon_size=(11,11))
                    f.Marker([first_lat,first_long],icon=icon,popup="Point départ").add_to(map)
                    icon1=f.CustomIcon("image/elephant_marker.png",icon_size=(11,11))
                    f.Marker([last_lat,last_long],icon=icon1,popup="Point d'arrivé ").add_to(map)
                    AntPath(data_jour,delay=1100,weight=3,color="white",dash_array=[20,30],pulse_color="green",reverse=True).add_to(map)
                    AntPath(data_nuit,delay=1100,weight=3,color="white",dash_array=[20,30],pulse_color="blue",reverse=True).add_to(map)
                    legend_html =f"""
                    <div style='
                            position: fixed; 
                            bottom: 100px; width: 260px; height: 350px; 
                            background-color: white; 
                            border:2px solid grey;
                            right:20px;
                            z-index:9999; 
                            font-size:14px;
                    '>
                    &nbsp;<b style='margin-bottom:250px'>Légende</b>
                    <div style='display:flex;'>
                        <p style='color:blue'>---------------</p>
                        <p>Trajet de nuit</p>
                    </div>
                    <div style='display:flex;'>
                        <p style='color:green'>---------------</p>
                        <p>Trajet de Jour</p>
                    </div>
                    <div style="margin-left:30px">
                        <p>Du {df.tail(1)['Date_Enregistrement'].values[0]} au {df.head(1)['Date_Enregistrement'].values[0]}
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
                    <p>Distance total de Jour:<b> {round(distance_jour,5)} Km</b></p>
                    <p>Distance total de Nuit:<b> {round(distance_nuit,5)} Km</b></p>
                    <p>Distance Total:<b> {round(distance_total,5)} Km</b></p>
                    <div style='display:flex;'>
                        <img src="data:image/png;base64,{base64.b64encode(open('image/elephant_marker.png', 'rb').read()).decode('utf-8')}" width="20" height="20">
                        <b style='margin-left:20px'>{st.session_state["nom_elephant"]}</b>
                    </div>
                    <div style='display:flex;justify-content:center'>
                            <img src="data:image/png;base64,{base64.b64encode(open('image/minef.png', 'rb').read()).decode('utf-8')}" width="60" height="60">   
                        </div>
                 </div>"""
                map.get_root().html.add_child(f.Element(legend_html))
                map.save("deplacement_jour_nuit.html")
                map_html = map._repr_html_()
                st.components.v1.html(map_html, height=1500)
            



        
                       
                        




            
                


