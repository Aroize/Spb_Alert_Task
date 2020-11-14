import pandas as pd
import time
to_timestamp = lambda strdate: time.mktime(time.strptime(str(strdate), '%Y-%m-%d %H:%M:%S'))
from flask import Flask, request, jsonify
app = Flask(__name__)

from models.models import ClusteringModel, CheckEmergencyModel
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
# dfs = {0: {'df': pd.read_excel('../../data/raw/Датасет3_Дтп.xlsx', 
#                                index_col='Время регистрации')}}
# for event_type in dfs.keys():
#     df = dfs[event_type]['df']
#     df['timestamp'] = list(map(to_timestamp, df['Время регистрации']))
#     df['lat'] = df['Широта']
#     df['lon'] = df['Долгота']
#     df = df.drop('Время регистрации	Категория	Идентификатор Еас адреса	Идентификатор Еас здания	Широта	Долгота	Район'.split('\t'), axis=1)
#     df.set_index('timestamp')
#     dfs[event_type]['df'] = df
    
# print(dfs[0]['df'])

    
    
def parse_events(json_events):
    events = []
    events_type = json_events[0]['event']
    for item in json_events:
        event = Event(item['lat'], item['lon'], item['ts'])
        events.append(event)
    return events, events_type


@app.route('/calc_clusters', methods=['GET'])
def calc_clusters():
    json_events = request.get_json()
    events, events_type = parse_events(json_events)
    
    config = clustering_configs[events_type]
    model = ClusteringModel(**config)
        
    events_labels = model.predict(events)
    labled_events = []
    for event, label in events_labels:
        obj = {'lat': event.lat,
               'lone': event.lon,
               'ts': event.time,
               'event': events_type,
               'cid': label}
        labled_events.append(obj)
    return jsonify(labled_events)


@app.route('/is_cluster_emergency', methods=['GET'])
def check_emergency():
    cluster = request.get_json() # list of events
    print(cluster)
    events, events_type = parse_events(cluster)
    max_ts = max(list(map(lambda ev: ev.time, events)))
#     subdf = 
    
    config = is_emergency_configs[events_type]
    model = CheckEmergencyModel(**config)
    
    status = model(events)
    return jsonify({'status': status})
    
    

if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=5000)