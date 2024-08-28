import pandas as pd
from geopy.distance import geodesic
"""Permet de definir les differentes distances parcourues par l'éléphant
"""
def dist_group_temps(dt):
    data=dt.groupby(["temps"])
    return data
def dist_jour_nuit(dt):
    data=dt.groupby(["Date_Enregistrement","temps"]).apply(distance_par_jour_km)
    return data
def distance(dataframe):
    #conversion du dataframe en numeric
    dist_total=0
    for i in range(1,len(dataframe)):
        prev_long=dataframe["Longitude"].iloc[i-1]
        prev_lati=dataframe["Latitude"].iloc[i-1]
        prev_pos=(prev_lati,prev_long)
        cur_long=dataframe["Longitude"].iloc[i]
        cur_lati=dataframe["Latitude"].iloc[i]
        cur_pos=(cur_lati,cur_long)
        distance=geodesic(prev_pos,cur_pos).km
        #distance total de chaque groupe
        dist_total+=distance
    return dist_total

def distance_par_jour_km(dataframe):
    #conversion du dataframe en numeric
    dist_total=0
    for i in range(1,len(dataframe)):
        prev_long=dataframe["Longitude"].iloc[i-1]
        prev_lati=dataframe["Latitude"].iloc[i-1]
        prev_pos=(prev_lati,prev_long)
        cur_long=dataframe["Longitude"].iloc[i]
        cur_lati=dataframe["Latitude"].iloc[i]
        cur_pos=(cur_lati,cur_long)
        distance=geodesic(prev_pos,cur_pos).km
        #distance total de chaque groupe
        dist_total+=distance
    return dist_total
#Fin de la fonction

def distance_par_jour_m(dataframe):
    #conversion du dataframe en numeric
    dist_total=0
    for i in range(1,len(dataframe)):
        prev_long=dataframe["Longitude"].iloc[i-1]
        prev_lati=dataframe["Latitude"].iloc[i-1]
        prev_pos=(prev_lati,prev_long)
        cur_long=dataframe["Longitude"].iloc[i]
        cur_lati=dataframe["Latitude"].iloc[i]
        cur_pos=(cur_lati,cur_long)
        distance=geodesic(prev_pos,cur_pos).m
        #distance total de chaque groupe
        dist_total+=distance
    return dist_total

def distance_par_jour_metre(dataframe):
    #conversion du dataframe en numeric
    dataframe["Longitude"]=pd.to_numeric(dataframe["Longitude"],errors='coerce')
    dataframe["Latitude"]=pd.to_numeric(dataframe["Latitude"],errors='coerce')
    distances=[]
    for i in range(1,len(dataframe)):
        prev_long=dataframe["Longitude"].iloc[i-1]
        prev_lati=dataframe["Latitude"].iloc[i-1]
        prev_pos=(prev_lati,prev_long)
        cur_long=dataframe["Longitude"].iloc[i]
        cur_lati=dataframe["Latitude"].iloc[i]
        cur_pos=(cur_lati,cur_long)
        distance=geodesic(prev_pos,cur_pos).m
        distances.append(distance)
    #distance total de chaque groupe
    dist_total=sum(distances)
    return dist_total
#Fin de la fonction

#permet de définir la distance par jour en metre en fonction des coordonnées
def distance_par_jour_m(dataframe):
    #conversion du dataframe en numeric
    dist_total=0
    for i in range(1,len(dataframe)):
        prev_long=dataframe["Longitude"].iloc[i-1]
        prev_lati=dataframe["Latitude"].iloc[i-1]
        prev_pos=(prev_lati,prev_long)
        cur_long=dataframe["Longitude"].iloc[i]
        cur_lati=dataframe["Latitude"].iloc[i]
        cur_pos=(cur_lati,cur_long)
        distance=geodesic(prev_pos,cur_pos).m
        #distance total de chaque groupe
        dist_total+=distance
    return dist_total

#distance Jour en Km
def distance_jour_km(dt):
    distances=[]
    date=[]
    dt=dt.copy().set_index("Date_Enregistrement",drop=False)
    dt.index=pd.to_datetime(dt.index)
    dt=dt[["Longitude","Latitude"]]
    dt2=dt.groupby(pd.Grouper(level="Date_Enregistrement",freq="1D",sort=True))
    for index,row in dt2:
        if not row.empty:
           distance=distance_par_jour_km(row)
           distances.append(distance)
           date.append(index)
    dataframe=pd.DataFrame({"Date":date,"distance":distances})
    return dataframe.sort_values(by="Date",ascending=False)
#fin de la fonction

#distance par jour et nuit en kilometre retourne un dataframe multi-index
def distance_par_nuit_jour_km(dt):
    dt.sort_values(by="Date_Enregistrement",ascending=False,inplace=True)
    dt1=dt.groupby(by=["Date_Enregistrement","temps"]).apply(distance_par_jour_km)
    dt1=pd.DataFrame(dt1)
    dt1.rename(columns={0:"Distance_parcourue_km"},inplace=True)
    return dt1
#fin de la fonction

#distance par jour et nuit en metre
def distance_par_nuit_jour_m(dt):
    dt1=dt.groupby(by=["Date_Enregistrement","temps"]).apply(distance_par_jour_metre)
    dt1=pd.DataFrame(dt1)
    dt1.rename(columns={0:"Distance_parcourue_m"},inplace=True)
    return dt1
#fin de la fonction

#distance par semaine en Km
def distance_par_semaine_km(dt):
    distances=[]
    date=[]
    dt=dt.copy().set_index("Date_Enregistrement",drop=False)
    dt.index=pd.to_datetime(dt.index)
    dt=dt[["Longitude","Latitude"]]
    dt2=dt.groupby(pd.Grouper(level="Date_Enregistrement",freq="W",sort=True))
    for index,row in dt2:
        if not row.empty:
           distance=distance_par_jour_km(row)
           distances.append(distance)
           date.append(index)
    dataframe=pd.DataFrame({"Date":date,"distance":distances})
    return dataframe
#fin de la fonction

#distance par semaine en mettre
def distance_par_semaine_metre(dt):
    distances=[]
    date=[]
    dt=dt.copy().set_index("Date_Enregistrement",drop=False)
    dt.index=pd.to_datetime(dt.index)
    dt=dt[["Longitude","Latitude"]]
    dt2=dt.groupby(pd.Grouper(level="Date_Enregistrement",freq="W",sort=True))
    for index,row in dt2:
        if not row.empty:
           distance=distance_par_jour_metre(row)
           distances.append(distance)
           date.append(index)
    dataframe=pd.DataFrame({"Date":date,"distance":distances})
    return dataframe
#fin de la fonction

#distance par mois en metre
def distance_par_mois_metre(dt):
    distances=[]
    date=[]
    dt=dt.copy().set_index("Date_Enregistrement",drop=False)
    dt.index=pd.to_datetime(dt.index)
    dt=dt[["Longitude","Latitude"]]
    dt2=dt.groupby(pd.Grouper(level="Date_Enregistrement",freq="M",sort=True))
    for index,row in dt2:
        if not row.empty:
           distance=distance_par_jour_metre(row)
           distances.append(distance)
           date.append(index)
    dataframe=pd.DataFrame({"Date":date,"distance":distances})
    return dataframe
#fin de la fonction

#distance par mois en km
def distance_par_mois_km(dt):
    distances=[]
    date=[]
    dt=dt.copy().set_index("Date_Enregistrement",drop=False)
    dt.index=pd.to_datetime(dt.index)
    dt=dt[["Longitude","Latitude"]]
    dt2=dt.groupby(pd.Grouper(level="Date_Enregistrement",freq="M",sort=True))
    for index,row in dt2:
        if not row.empty:
           distance=distance_par_jour_km(row)
           distances.append(distance)
           date.append(index)
    dataframe=pd.DataFrame({"Date":date,"distance":distances})
    return dataframe
#fin de la fonction

#distance parcourue par Annee en Kilometre
def distance_par_annee_km(dt):
    distances=[]
    date=[]
    dt=dt.copy().set_index("Date_Enregistrement",drop=False)
    dt.index=pd.to_datetime(dt.index)
    dt=dt[["Longitude","Latitude"]]
    dt2=dt.groupby(pd.Grouper(level="Date_Enregistrement",freq="YE",sort=True))
    for index,row in dt2:
        if not row.empty:
           distance=distance_par_jour_km(row)
           distances.append(distance)
           date.append(index)
    dataframe=pd.DataFrame({"Date":date,"distance":distances})
    return dataframe
#fin de la fonction

def distance_par_annee_metre(dt):
    distances=[]
    date=[]
    dt=dt.copy().set_index("Date_Enregistrement",drop=False)
    dt.index=pd.to_datetime(dt.index)
    dt=dt[["Longitude","Latitude"]]
    dt2=dt.groupby(pd.Grouper(level="Date_Enregistrement",freq="Y",sort=True))
    for index,row in dt2:
        if not row.empty:
           distance=distance_par_jour_metre(row)
           distances.append(distance)
           date.append(index)
    dataframe=pd.DataFrame({"Date":date,"distance":distances})
    return dataframe
#fin de la fonction

