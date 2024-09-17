def definir_periode_elephant(heure):
    import datetime
    if datetime.time(6)<(heure)<datetime.time(18):
        return "Jour"
    else:
        return "Nuit"