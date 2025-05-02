import pandas as pd
from config import CSV_STATIONS, CSV_VOCAB

def load_stations():
    df = pd.read_csv(CSV_STATIONS, sep=';', header=0, encoding='utf-8-sig')
    stations = []
    for _, row in df.iterrows():
        try:
            lat = float(row['Latitude']) / 10000
            lon = float(row['Longitude']) / 10000
            stations.append({
                "name": str(row['Station']),
                "lat": lat, "lon": lon
            })
        except Exception:
            continue
    return stations

def load_vocab_levels():
    df = pd.read_csv(CSV_VOCAB, sep=';', usecols=[0,1], header=0, encoding='utf-8-sig')
    pairs = list(zip(df.iloc[:,0].astype(str), df.iloc[:,1].astype(str)))
    blocks = len(pairs) // 7
    return [pairs[i*7:(i+1)*7] for i in range(blocks)]
