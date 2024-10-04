import pandas as pd
from geopy.distance import geodesic
"""Permet de definir les differentes distances parcourues par l'éléphant
"""
def dist_group_temps(dt):
    data=dt.groupby(["temps"])
    return data
def dist_jour_nuit(dt):
    data=dt.groupby(["Date_Enregistrement","temps"]).apply(distance)
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
        dist_total=dist_total+distance
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
        dist_total=dist_total+distance
    return dist_total

#Fin de la fonction

def distance_jour_km(df):
    dk=df.reset_index()
    indexes=[]
    dt=dk.set_index("Date_Enregistrement",drop=False)
    dt_unique=dt.drop_duplicates(subset="Date_Enregistrement")
    for index,row in dt_unique.iterrows():
        indexes.append(index)
    dict={"Date":[],"Distance":[]}
    for i in range(0,len(indexes)):
       dict["Date"].append(indexes[i])
       dist=(dt[dt["Date_Enregistrement"]==indexes[i]])
       #dict["Distance"].append(distance)
       d=distance(dist)
       dict["Distance"].append(d)
    dataframe=pd.DataFrame(dict)
    return dataframe
#fin de la fonction

#distance par jour et nuit en kilometre retourne un dataframe multi-index
def distance_par_nuit_jour_km(dt):
    dt.sort_values(by="Date_Enregistrement",ascending=False,inplace=True)
    dt1=dt.groupby(by=["Date_Enregistrement","temps"]).apply(distance)
    dt1=pd.DataFrame(dt1)
    dt1.rename(columns={0:"Distance_parcourue_km"},inplace=True)
    return dt1
#fin de la fonction

#distance par jour et nuit en metre
def distance_par_nuit_jour_m(dt):
    dt1=dt.groupby(by=["Date_Enregistrement","temps"]).apply(distance_par_jour_m)
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
           distance1=distance(row)
           distances.append(distance1)
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
           distance=distance_par_jour_m(row)
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
           distance=distance_par_jour_m(row)
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
           distance1=distance(row)
           distances.append(distance1)
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
           distance1=distance(row)
           distances.append(distance1)
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
           distance=distance_par_jour_m(row)
           distances.append(distance)
           date.append(index)
    dataframe=pd.DataFrame({"Date":date,"distance":distances})
    return dataframe
#fin de la fonction
def distance_periode_jour(list):
    distance=sum(list)
    return distance
def distance_total(df):
    periode1=df.tail(1)["Date_Enregistrement"].values[0]
    periode2=df.head(1)["Date_Enregistrement"].values[0]
    df_periode_afficher=df.copy()
    df_periode_afficher=df_periode_afficher.set_index("Date_Enregistrement",drop=False)
    df_periode_afficher.index=pd.to_datetime(df_periode_afficher.index)
    df_periode_filter=df_periode_afficher[(df_periode_afficher["Date_Enregistrement"]>=periode1) & (df_periode_afficher["Date_Enregistrement"]<=periode2)]
    distance_periode=df_periode_filter.groupby(pd.Grouper(level="Date_Enregistrement",freq="D")).apply(distance).sum()
    return distance_periode
def distance_total_jour_nuit(df):

    dataframe_nuit_jour=pd.DataFrame(columns=["Distance_Nuit","Distance_Jour"])
    element_retrancher=0
    periode1=df.tail(1)["Date_Enregistrement"].values[0]
    periode2=df.head(1)["Date_Enregistrement"].values[0]
    df_periode_afficher=df.copy()
    df_periode_afficher=df_periode_afficher.set_index("Date_Enregistrement",drop=False)
    df_periode_afficher.index=pd.to_datetime(df_periode_afficher.index)
    df_periode_filter=df_periode_afficher[(df_periode_afficher["Date_Enregistrement"]>=periode1) & (df_periode_afficher["Date_Enregistrement"]<=periode2)]
    df_periode_filter.reset_index(drop=True,inplace=True)
    distance_periode=df_periode_filter.groupby(["Date_Enregistrement","temps"]).apply(distance)
    dist_total_jour=distance_periode.unstack(level="temps")["Jour"].sum()
    dist_total_nuit=distance_periode.unstack(level="temps")["Nuit"].sum()
    dist_total_nuit_jour=dist_total_jour+dist_total_nuit
    distance_totale=distance_total(df)
    if dist_total_nuit_jour>distance_totale:
        reste=dist_total_nuit_jour-distance_totale
        if dist_total_nuit>dist_total_jour:
            element_retrancher=dist_total_nuit-reste
            dataframe_nuit_jour.loc[0]=[element_retrancher,dist_total_jour]
        else:
            element_retrancher=dist_total_jour-reste
            dataframe_nuit_jour.loc[0]=[dist_total_nuit,element_retrancher]
    else:
        reste=distance_totale-dist_total_nuit_jour
        if dist_total_nuit>dist_total_jour:
            element_ajouter=dist_total_jour+reste
            dataframe_nuit_jour.loc[0]=[dist_total_nuit,element_ajouter]
        else:
            element_ajouter=dist_total_nuit+reste
            dataframe_nuit_jour.loc[0]=[element_ajouter,dist_total_jour]
    return  dataframe_nuit_jour
def distance_Mois(df):
    periode1=df.tail(1)["Date_Enregistrement"].values[0]
    periode2=df.head(1)["Date_Enregistrement"].values[0]
    dt=df.set_index("Date_Enregistrement",drop=False)
    dt.index=pd.to_datetime(dt.index)
    distance_Mois=dt.groupby(pd.Grouper(level="Date_Enregistrement",freq="ME")).apply(distance).sum()
    return distance_Mois