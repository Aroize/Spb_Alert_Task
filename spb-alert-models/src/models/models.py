from .cdbscan import Event, ContinuosDBSCAN, ContinuosCluster


class ClusteringModel(ContinuosDBSCAN):
    def __init__(self, eps, min_samples, continuos_time, **kwargs):
        super(ClusteringModel, self).__init__(eps, min_samples, continuos_time)
        
    
    def predict(self, events):
        assert all(list(map(lambda ev: isinstance(ev, Event), events)))
        
        labels = self.fit(events)
        result = list(zip(events, labels))
        return result
    
    
class EmergencyModel():
    def __init__(self, events_df, **kwargs):
        self.df = events_df
        
    def predict_is_emergency(self, events):
        reasons = self._get_cluster_emergency_reasons(events)
        top_importance = 0
        for key in reasons.keys():
            if reasons[key]['importance'] > top_importance:
                top_importance = reasons[key]['importance']
        return int(top_importance > 2.5)
    
    def predict_emergency_reasons(self, events):
        reasons = self._get_cluster_emergency_reasons(events)
        return reasons
                
        
    def _get_cluster_emergency_reasons(self, events):
        # measures prob of given events (which belongs to one cluster) are emergency
        mean = lambda arr: sum(arr)/len(arr) if len(arr) else 0
        # gather data
        curr_points = len(events)
        centroid_lat = mean(list(map(lambda ev: ev.lat, events)))
        centroid_lon = mean(list(map(lambda ev: ev.lon, events)))
        min_ts = min(list(map(lambda ev: ev.time, events)))
        max_ts = max(list(map(lambda ev: ev.time, events)))
        
        historical_clusters_in_local_area = self._calc_local_area_clusters(centroid_lat, centroid_lon, 0.1)
        historical_clusters_in_curr_time = self._calc_curr_time_clusters(min_ts, max_ts)
        # TODO add external data
        
        # featuring
        reasons = {}
        
        # unusual activity for area
        get_avg_clusters_points = lambda clustrs: mean(list(map(lambda clust: len(clust.events))))
        f_historical_local_avg_points_in_cluster = mean(list(map(lambda clstrs: get_avg_clusters_points(clstrs), 
                                                                 historical_clusters_in_local_area)))
        diff = curr_points / max(1, f_historical_local_avg_points_in_cluster)
        reasons['unusual_high_activity'] = {'perc': diff,
                                            'importance': int(diff > 3.0)}

        # unusual weather
        week = 60*60*24*7
        avg_ts = (max_ts + min_ts) / 2
        temp_diff, pressure_diff, wetness_diff, visibility_diff = self._calc_weather_diffs(min_ts-week, min_ts, min_ts, max_ts)
        reasons['unusual_temperature'] = {'perc': temp_diff,
                                          'importance': int(temp_diff > 1.5)}
        reasons['unusual_pressure'] = {'perc': pressure_diff,
                                       'importance': int(pressure_diff > 1.2)}
        reasons['unusual_wetness'] = {'perc': wetness_diff,
                                      'importance': int(wetness_diff > 1.4)}
        reasons['unusual_visibility'] = {'perc': visibility_diff,
                                         'importance': int(visibility_diff > 1.25)}
        
        # unusual crashes
        
        
        return reasons
    
        
    def _build_events(self, events_data):
        events = []
        for (ts, lat, lon) in events_data:
            events.append(Event(lat, lon, ts))
        return events
    
    
    def _calc_weather_diffs(self, ts_past_from, ts_past_to, ts_from, ts_to):
        df = self.df.copy()
        subdf = df[(df.timestamp > ts_past_from) & (df.timestamp < ts_past_to)]
        past_means = subdf.mean()
        
        subdf = df[(df.timestamp > ts_from) & (df.timestamp < ts_to)]
        curr_means = subdf.mean()
        
        diff = abs(curr_means - past_means) / past_means
        temp_diff = diff['T'] or 1
        pressure_diff = diff['P'] or 1
        wetness_diff = diff['U'] or 1
        visibility_diff = diff['VV'] or 1
        
        return temp_diff, pressure_diff, wetness_diff, visibility_diff
        
        
    def _calc_local_area_clusters(self, lat, lon, eps):
        df = self.df.copy()
        
        df['dist'] = ((df.lat - lat)**2 + (df.lon - lon)**2)**0.5
        local_events = df[df.dist <= eps]
        local_events = self._build_events(local_events['timestamp lat lon'.split()].to_records(index=False))
        
        if len(local_events) < 2:
            return []
        
        # get clusters 
        model = ClusteringModel(0.01, 4, 60*10)
        labels = model.fit(local_events)
        clusters = [ContinuosCluster([]) for _ in range(max(0, max(labels)+1))]
        for i, event in enumerate(local_events):
            if labels[i] != -1:
                clusters[labels[i]].add(event)
    
        return clusters
    
    def _calc_curr_time_clusters(self, min_ts, max_ts):
        df = self.df.copy()
        
        local_events = df[(df.timestamp <= max_ts) & (df.timestamp > min_ts)]
        local_events = self._build_events(local_events['timestamp lat lon'.split()].to_records(index=False))
        
        if len(local_events) < 2:
            return []
        
        # get clusters 
        model = ClusteringModel(0.01, 4, 60*10)
        labels = model.fit(local_events)
        clusters = [ContinuosCluster([]) for _ in range(max(0, max(labels)+1))]
        for i, event in enumerate(local_events):
            if labels[i] != -1:
                clusters[labels[i]].add(event)
    
        return clusters