import pandas as pd
#calcule l'angle à partir des latitudes et longitude
def calcul_angle(lat1,lon1,lat2,lon2):
    import math
    diff_lon = lon2 - lon1
    diff_lat = lat2 - lat1
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    azimuth = math.atan2(diff_lon * math.cos(lat1_rad), diff_lat)
    azimuth_deg = math.degrees(azimuth)
    if azimuth_deg < 0:
        azimuth_deg += 360
    return azimuth_deg
#Fin de la fonction
#calcule de la direction par second
def direction_par_semaine(dataframe):
    coordonnes={"date":[],"point_depart":[],"point_arrive":[],"Angle":[],"direction":[]}
    b=pd.DataFrame(dataframe.copy()[["Date_Enregistrement","Heure_Enregistrement","Longitude","Latitude"]]).reset_index(drop=True)
    b.set_index('Date_Enregistrement',drop=False,inplace=True)
    b.index=pd.to_datetime(b.index)
    c=b.groupby(pd.Grouper(level="Date_Enregistrement",freq="W"))
    for date,rows in c:
       if not rows.empty:
           premier_element=rows.iloc[0]
           dernier_element=rows.iloc[-1]
           long1=float(premier_element.get("Longitude"))
           lat1=float(premier_element.get("Latitude"))
           lat2=float(dernier_element.get("Latitude"))
           long2=float(dernier_element.get("Longitude"))
           angle=calcul_angle(lat1,long1,lat2,long2)
           point_depart=(lat1,long1)
           point_arrive=(lat2,long2)
           coordonnes["point_depart"].append(point_depart)
           coordonnes["point_arrive"].append(point_arrive)
           coordonnes["Angle"].append(round(angle,2))
           coordonnes["date"].append(date)
           if(0<angle<90):
                 coordonnes["direction"].append("Nord-Est")
           elif(90<angle<180):
                coordonnes["direction"].append("Sud-Est")
           elif(180<angle<270):
                coordonnes["direction"].append("Sud-Ouest")
           else:
                coordonnes["direction"].append("Nord-Ouest")
    coordonnes=pd.DataFrame(coordonnes)
    return coordonnes
#fin de la fonction

#direction chaque heure
def direction_par_heure(dataframe):
    coordonnes={"date":[],"point_depart":[],"point_arrive":[],"Angle":[],"direction":[]}
    b=pd.DataFrame(dataframe.copy()[["Date_Enregistrement","Heure_Enregistrement","Longitude","Latitude"]]).reset_index(drop=True)
    c=b.groupby(pd.Grouper(key="Date_Enregistrement",sort=False))
    for date_group, group_data in c:
        dernier_element = group_data.iloc[-1]# Dernier élément du groupe
        premier_element = group_data.iloc[0]# Premier élément du groupe
        lat2=float(dernier_element.get('Latitude'))
        lon2=float(dernier_element.get('Longitude'))
        lat1=float(premier_element.get('Latitude'))
        lon1=float(premier_element.get('Longitude'))
        angle=calcul_angle(lat1,lon1,lat2,lon2)
    #Determination de point
        point_depart=(float(premier_element.get('Latitude')),float(premier_element.get('Longitude')))
        point_arrive=(float(dernier_element.get('Latitude')),float(dernier_element.get('Longitude')))
    #Les coordonees contiennent un seul élément
        coordonnes["point_depart"].append(point_depart)
        coordonnes["point_arrive"].append(point_arrive)
        coordonnes["Angle"].append(round(angle,2))
        coordonnes["date"].append(date_group)
        if(0<angle<90):
             coordonnes["direction"].append("Nord-Est")
        elif(90<angle<180):
            coordonnes["direction"].append("Sud-Est")
        elif(180<angle<270):
            coordonnes["direction"].append("Sud-Ouest")
        else:
            coordonnes["direction"].append("Nord-Ouest")
    coordonnes=pd.DataFrame(coordonnes)
    return coordonnes
#fin de la direction
#mettre la longitude en Dégré-minute-second
def put_long_to_DMS(long):
    long=float(long)
    degre_decimal=long
    degre=int(degre_decimal)
    minute_decimal=(degre_decimal-degre)*60
    minute=int(minute_decimal)
    second_decimal=(minute_decimal-minute)*60
    second=int(second_decimal)
    if(long>0):
        cardinal_point="EST"
        result=f"{degre}°{minute}'{second} {cardinal_point}"
    else:
        cardinal_point="OUEST"
        degre=abs(degre)
        minute=abs(minute)
        second=abs(second)
        result=f"{degre}°{minute}'{second} {cardinal_point}"
    return result
#fin de la fonction

#mettre la lattitude en Dégré-Minute-Seconde
def put_lat_to_DMS(lat):
    lat=float(lat)
    degre_decimal=lat
    degre=int(degre_decimal)
    minute_decimal=(degre_decimal-degre)*60
    minute=int(minute_decimal)
    second_decimal=(minute_decimal-minute)*60
    second=int(second_decimal)
    if(lat>0):
        cardinal_point="NORD"
        result=f"{degre}°{minute}'{second} {cardinal_point}"
    else:
        cardinal_point="SUD"
        degre=abs(degre)
        minute=abs(minute)
        second=abs(second)
        result=f"{degre}°{minute}'{second} {cardinal_point}"
    return result
#fin de la fonction

#convertir les cordonnées en DMS
def convert_to_DMS(df):
    df_dms=pd.DataFrame(df.copy()[["Date_Enregistrement","Heure_Enregistrement","Latitude","Longitude"]])
    for index,row in df_dms.iterrows():     
        lat_dms=put_lat_to_DMS(row["Latitude"])
        long_dms=put_long_to_DMS(row["Longitude"])
        df_dms.loc[index,"Latitude_DMS"]=lat_dms
        df_dms.loc[index,"Longitude_DMS"]=long_dms
        #df_dms["Latitude_DMS"]=lat_dms
        #df_dms["Longitude_DMS"]=long_dms
    return df_dms
#fin de la fonction
