import pandas as pd
import time
to_timestamp = lambda strdate: time.mktime(time.strptime(str(strdate), '%Y-%m-%d %H:%M:%S'))
from flask import Flask, request, jsonify
app = Flask(__name__)

from models.models import ClusteringModel, EmergencyModel
from models.cdbscan import Event

clustering_configs = {
    0: {'name': 'fire',
        'eps': 0.01,
        'min_samples': 4,
        'continuos_time': 60*10}
}
is_emergency_configs = {
    0: {'name': 'fire',}
}

# Read and format data
dfs = {0: {'df': pd.read_excel('../data/raw/new_Dataset3_Dtp.xlsx')}}
for event_type in dfs.keys():
    df = dfs[event_type]['df']
    df['timestamp'] = list(map(to_timestamp, df['Время регистрации']))
    df['lat'] = df['Широта']
    df['lon'] = df['Долгота']
    df = df['timestamp lat lon T P U VV'.split()]
    df = df[df.isna().sum(axis=1) == 0]
    dfs[event_type]['df'] = df
    

    
    
def parse_events(json_events):
    events = []
    events_type = json_events[0]['event']
    for item in json_events:
        event = Event(item['lat'], item['lon'], item['ts'])
        events.append(event)
    return events, events_type


@app.route('/processEvents', methods=['GET'])
def calc_clusters():
    json_events = request.get_json()
    events, events_type = parse_events(json_events)
    
    config = clustering_configs[events_type]
    model = ClusteringModel(**config)
        
    events_labels = model.predict(events)
    labled_events = []
    for event, label in events_labels:
        obj = {'lat': event.lat,
               'lon': event.lon,
               'ts': event.time,
               'event': events_type,
               'cid': label}
        labled_events.append(obj)
    return jsonify(labled_events)


@app.route('/isClusterEmergency', methods=['GET'])
def check_emergency():
    cluster = request.get_json() # list of events
    events, events_type = parse_events(cluster)
    
    # get df with all events until the latest of given
    max_ts = max(list(map(lambda ev: ev.time, events)))
    subdf = dfs[event_type]['df']
    subdf = subdf[subdf.timestamp <= max_ts]
    
    config = is_emergency_configs[events_type]
    model = EmergencyModel(subdf, **config)
    
    prob = model.predict_is_emergency(events)
    return jsonify({'prob': prob})
    
    
@app.route('/getClusterEmergencyReasons', methods=['GET'])
def check_emergency1():
    cluster = request.get_json() # list of events
    events, events_type = parse_events(cluster)
    
    # get df with all events until the latest of given
    max_ts = max(list(map(lambda ev: ev.time, events)))
    subdf = dfs[event_type]['df']
    subdf = subdf[subdf.timestamp <= max_ts]
    
    config = is_emergency_configs[events_type]
    model = EmergencyModel(subdf, **config)
    
    reasons = model.predict_emergency_reasons(events)
    return jsonify({'reasons': reasons})


    

if __name__ == "__main__":
#     emergency_models = {0: {'model': EmergencyModel(dfs[0]['df'])},
#                         1: {'model': EmergencyModel(dfs[1]['df'])}}
    app.run(host='0.0.0.0', port=5000)