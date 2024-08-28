from geopy.distance import geodesic
import pandas as pd
from sklearn.cluster import DBSCAN
import requests
import random
from selenium import webdriver
import time
import os
import streamlit as st
#fonction to determine the min distance for epsilon of DBSCAN
def distance_dbscan(df):
    data=df.reset_index(drop=True)
    dataframe_list=[{"point1":[],"point2":[],"distance":[],"Date":[]}]
    for i in range(1,len(data)):
        coordonnee1=(data.loc[i-1,"Latitude"],data.loc[i-1,"Longitude"])
        coordonnee2=(data.loc[i,"Latitude"],data.loc[i,"Longitude"])
        distance=geodesic(coordonnee1,coordonnee2).km
        dataframe_list[0]["point1"].append(coordonnee1)
        dataframe_list[0]["point2"].append(coordonnee2)
        dataframe_list[0]["distance"].append(distance)
    dataframe=pd.DataFrame({"point1":dataframe_list[0]["point1"],"point2":dataframe_list[0]["point2"],"distance":dataframe_list[0]["distance"]})
    epsilon=round(dataframe["distance"].min(),10)
    return epsilon

#fonction to create cluster
def make_cluster(df,eps):
    dt=df[["Longitude","Latitude","Date_Enregistrement"]]
    dt.reset_index(drop=True,inplace=True)
    dt["Longitude"]=pd.to_numeric(dt["Longitude"],errors="coerce")
    dt["Latitude"]=pd.to_numeric(dt["Latitude"],errors="coerce")
    coordonnes=dt[["Latitude","Longitude"]].values
    dbscan=DBSCAN(eps=eps,min_samples=10)
    clusters=dbscan.fit(coordonnes)
    clusters_label=dbscan.labels_
    dt["cluster"]=clusters_label
    return dt
#find centoid location
def find_location(df_cluster):
    df_mean=df_cluster.groupby("cluster").agg({"Latitude":"mean","Longitude":"mean"})
    lieux=[{"region":[],"district":[],"village":[],"Latitude":[],"Longitude":[]}]
    for index,row in df_mean.iterrows():
        lon=row['Longitude']
        lat=row['Latitude']
        url=f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}"
        headers={
                    'USER-AGENT':"laminekone7818@gmail.com"
                }
        reponse=requests.get(url,headers=headers)
        if reponse.status_code==200:
            village=""
            district=""
            address=(reponse.json()["address"])
            if "village" in address:
                village=address["village"]
            if "state_district" in address:
                district=address["state_district"]
            region=address["state"]
            pays=address["country"]
            lieux[0]["region"].append(region)
            lieux[0]["district"].append(district)
            lieux[0]["village"].append(village)
            lieux[0]["Latitude"].append(lat)
            lieux[0]["Longitude"].append(lon)
    regions=lieux[0]["region"]
    districts=lieux[0]["district"]
    villages=lieux[0]["village"]
    latitudes=lieux[0]["Latitude"]
    longitudes=lieux[0]["Longitude"]
    df_lieux=pd.DataFrame({"region":regions,"district":districts,"village":villages,"Latitude":latitudes,"Longitude":longitudes})
    return df_lieux
def color(dt):
    colors =[
    "red",
    "green",
    "yellow",
    "orange"]
    color=[]
    df_group=dt.groupby("cluster").agg({"Longitude":"mean"})
    df_group["color"]=""
    for index in df_group.index:
        choice=random.choice(colors)
        if choice not in  df_group["color"]:
            df_group.loc[index,"color"]=choice
        else:
            choice=random.choice(colors)
    for index,row in df_group.iterrows():
        color.append({index:row["color"]})
    return color
def number_in_index(number, list_of_dicts):
    for d in list_of_dicts:
        if number in d:
            return(d[number])
def generate_and_download_image():
    file_name="zone_forte_concentration.html"
    options=webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver=webdriver.Chrome(options=options)
    file_path=os.path.abspath(file_name)
    driver.get('file://'+file_path)
    driver.implicitly_wait(15)
    driver.save_screenshot("zone_frequentation.png")
    driver.quit()
    image_path="zone_frequentation.png"
    with open(image_path,"rb") as file:
            btn=st.download_button(
                label="Telecharger la Carte",
                data=file,
                file_name="zone_frequentation.png",
                mime="image/png")
def generate_and_download_image_heatmap(nom_fichier,titre):
    file_name=nom_fichier
    options=webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver=webdriver.Chrome(options=options)
    file_path=os.path.abspath(file_name)
    driver.get('file://'+file_path)
    time.sleep(20)
    driver.save_screenshot("carte_de_chaleur.png")
    driver.quit()
    image_path="carte_de_chaleur.png"
    with open(image_path,"rb") as file:
            st.download_button(
                label="Telecharger",
                data=file,
                file_name=f"{titre}_heatMap.png",
                mime="image/png")
