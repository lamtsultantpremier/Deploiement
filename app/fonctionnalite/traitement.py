import pandas as pd
from fonctionnalite.periode import definir_periode_elephant
def traier_fichier(fichier):
    df=pd.read_csv(fichier)
    #Creation de la dataFrame à l'aide du fichier csv avec Pandas
#Fractionnement de la colonne Location en deux Colonne SCR(Systeme de coordonnée de référence) et de Position(Position Géographique)
    df[["SCR","Position"]]=df["location"].str.split(";",expand=True)
#suppresion de la colonne location
    df.drop(columns=["location"],axis=1,inplace=True)
#suppression de la chaine SRID= dans le champ SCR(Systeme de coordonnée de référence)
    df["SCR"]=df["SCR"].str.replace("SRID=","")
#Suppresion de de la chaine Point() dans le champ Position
    df["Position"]=df["Position"].str.replace("POINT (","").str.replace(")","")
#Fractionnement de la colonne Position en Deux colonnes (Longitude et Latitude)
    df[["Longitude","Latitude"]]=df["Position"].str.split(" ",expand=True)
#Supppresion de la colonne Position
    df.drop(columns=["Position"],axis=1,inplace=True)
#Changer le type de la colonne recorded_at au prealable oblet en DateTime(Date et Heure)
    df["recorded_at"]=pd.to_datetime(df["recorded_at"])
    df["Date_Enregistrement"]=df["recorded_at"].dt.date
    df["Heure_Enregistrement"]=df["recorded_at"].dt.time
#Suppresion de la colonne recorded_at
    df.drop(columns=["recorded_at",],axis=1,inplace=True)
#Suppression de la chaine de caractere (telonics-collars) contenu dans la colonne source
    df["source"]=df["source"].str.replace("(telonics-collars)","").str.replace(" ","")
    if df["source"].isin(['8056(elephantsci-awt)']).any():
         df["source"]=df["source"].str.replace("8056(elephantsci-awt)","8056")
#transformation de la colonne additionnal en dicttionnaire pour recuperer les elements à l'intérieur grace à eval
    df["additional"]=df["additional"].apply(eval)
#creer un dataFrame dont les éléments sont les differents éléments de la colonne additional
    additional_dict=pd.json_normalize(df["additional"])
    #Renommage des differentes colonnes 
    additional_dict.rename(columns={"frequency":"frequence","mortality":"etat_elephant","horizontal_error":"erreur_precision","satellite_count":"nbre_satelite","low_voltage":"etat_batterie"},inplace=True)
#Suppression de la colonne hdop qui represente la qualité de transmission du signal
    if hasattr(additional_dict,"hdop"):
        additional_dict.drop(["hdop"],axis=1,inplace=True)
#transformation du dataframe additional_dict en un dataFrame de Pandas
    additional_dict=pd.DataFrame(additional_dict)
#copie du DataFrame additional_disk
    infos_sup=additional_dict
    if hasattr(additional_dict,"etat_elephant"):
        infos_sup["etat_elephant"]=infos_sup["etat_elephant"].apply(lambda x: x if not pd.isnull(x) else "")
#suppression des valeurs NaN dans la DataFrame additional_dict
#1. colonne etat_elephant
        additional_dict["etat_elephant"]=additional_dict["etat_elephant"].apply(lambda x:x if not pd.isnull(x) else "")
#2. colonne etat_batterie
    if hasattr(additional_dict,"etat_batterie"):
        additional_dict["etat_batterie"]=additional_dict["etat_batterie"].apply(lambda x:x if not pd.isnull(x) else "")
#3. colonne erreur_precision 
    if hasattr(additional_dict,"erreur_precision"):
        additional_dict["erreur_precision"]=additional_dict["erreur_precision"].apply(lambda x:x if not pd.isnull(x) else "")
#4. colonne nbre_satelite
    if hasattr(additional_dict,"nbre_satelite"):
        additional_dict["nbre_satelite"]=additional_dict["nbre_satelite"].apply(lambda x:x if not pd.isnull(x) else "")
#concatenation de la DataFrame d'origine avec la DataFrame issu de additionnal
    df=pd.concat([df,additional_dict],axis=1)
#suppression du champ additionnal 
    df.drop(["additional"],axis=1,inplace=True)
    #Suppression du champs exclusion_flags
    df.drop(["exclusion_flags"],axis=1,inplace=True)
     #Suppression de la colonne created_at
    df.drop(["created_at"],axis=1,inplace=True)
    #Renommer le champ id en id_Position
    df.rename({"id":"id_Position"},axis=1,inplace=True)
#Transformer la colonne id_Position en index pour mieux manipuler les differentes Position
    df.set_index("id_Position",inplace=True)
    df.sort_values(by=["Date_Enregistrement","Heure_Enregistrement"],ascending=False,inplace=True)
    df["temps"]=df["Heure_Enregistrement"].apply( definir_periode_elephant)
    return df
