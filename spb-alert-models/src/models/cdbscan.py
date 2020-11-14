class Event:
    def __init__(self, lat, lon, time):
        self.cluster_id = -1
        self.lat = lat
        self.lon = lon
        self.time= time


class ContinuosDBSCAN:
    def __init__(self, eps, min_samples, continuos_time):
        self.eps = eps
        self.min_samples = min_samples
        self.continuos_time = continuos_time
  
    def events_are_cluster(self, event1, event2):
        return self._in_continuos_time(event1, event2) and \
               self._in_eps_neighbourhood(event1, event2) 
    
    def _in_continuos_time(self, time1, time2):
        return abs(time1 - time2) < self.continuos_time
    
    def _in_eps_neighbourhood(self, event1, event2):
        return ((event1.lat - event2.lat)**2 + \
                (event1.lon - event2.lon)**2)**0.5 < self.eps

    def event_in_cluster(self, cluster, event):
        # If given event in eps-neighb with min_samples cluster events
        good_events = 0
        for ev in cluster.events:
            if self._in_eps_neighbourhood(ev, event):
                good_events += 1
        
        # if there is no any event in time-neighb, we cant merge event with cluster
        if not self._in_continuos_time(cluster.last_event_time(), event.time):
            return False
                
        # cluster havent gain min_events. Add if all elements are near. It matches time according to previous "if"
        if len(cluster.events) < self.min_samples and good_events == len(cluster.events):
            return True
        
        # Default adding rule
        if good_events >= self.min_samples:
            return True
        return False
    
    def events_are_cluster(self, event1, event2):
        return self._in_continuos_time(event1.time, event2.time) and self._in_eps_neighbourhood(event1, event2)
    
    
    def fit(self, events):
        # returns list of cluste
        assert all(list(map(lambda ev: isinstance(ev, Event), events)))
        assert len(events) > 1
        
        def add_to_clusters(clusters, events):
            for i, event in enumerate(events):
                for j, clust in enumerate(clusters):
                    if self.event_in_cluster(clust, event):
                        clust.add(event)
                        events[i] = None
                        break
            events = list(filter(lambda ev: ev is not None, events))
            return clusters, events
        
        def make_new_cluster(clusters, events):
            for i, event1 in enumerate(events):
                for j, event2 in enumerate(events):
                    if j>i and self.events_are_cluster(event1, event2):
                        clusters.append(ContinuosCluster([event1, event2]))
                        events[i] = None
                        events[j] = None
                        events = list(filter(lambda ev: ev is not None, events))
                        return clusters, events
            return None, None
        
        events = sorted(events, key=lambda ev: ev.time)
        clusters = []
        
        event_times = sorted(list(set(map(lambda ev: ev.time, events))))
        curr_events = list(filter(lambda ev: ev.time >= event_times[0] and \
                                             ev.time <= event_times[0]+self.continuos_time, events))
        prev_time_to = curr_events[-1].time
        for time_from in event_times:
            # delete outdated events
            for i, event in enumerate(curr_events):
                if event.time < time_from:
                    curr_events[i] = None
            curr_events = list(filter(lambda ev: ev is not None, curr_events))
            # add new events fitted to window
            for i, event in enumerate(events):
                if event.time > time_from + self.continuos_time:
                    break
                if event.time > prev_time_to:
                    curr_events.append(event)
            prev_time_to = curr_events[-1].time if len(curr_events) else prev_time_to
            
            # fit algorithm on current events
            while 1:
                # merge events to existing clusters
                clusters, curr_events = add_to_clusters(clusters, curr_events)
                # create new clusters
                new_clusters, new_curr_events = make_new_cluster(clusters, curr_events)
                if new_clusters is None:
                    break
                else:
                    clusters, curr_events = new_clusters, new_curr_events
            
        # delete clusters that hadnt gain enougth events
        for i, clust in enumerate(clusters):
            if len(clust.events) < self.min_samples:
                clusters[i] = None
        clusters = list(filter(lambda cl: cl is not None, clusters))
            
        # make labels for clusters
        for i in range(len(clusters)):
            clusters[i].id = i
        
        # mark events with its clusters labels
        for i, event in enumerate(events):
            for j, cluster in enumerate(clusters):
                if event in cluster.events:
                    events[i].cluster_id = cluster.id
        
        return list(map(lambda ev: ev.cluster_id, events))
            

class ContinuosCluster:
    def __init__(self, events):
        self.events = events
        self.id = None
        
    def last_event_time(self):
        return max(list(map(lambda e: e.time, self.events)))

    def add(self, event):
        self.events.append(event)        
        
if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    import time
    
    path = '../data/raw/'
    df = pd.read_excel(path + 'Датасет3_Дтп.xlsx', index_col='Время регистрации', parse_dates=True)
    # df['time'] = pd.to_datetime(df['Время регистрации'])
    df = df[(df['Широта']!=0) & (df['Долгота']!=0)]
    
    to_timestamp = lambda strdate: time.mktime(time.strptime(str(strdate), '%Y-%m-%d %H:%M:%S'))
    
    
    subdf = df.loc['2020-01-15':'2020-01-20']
    coords = np.array(list(zip(subdf['Долгота'].tolist(), subdf['Широта'].tolist())))
    times = list(map(to_timestamp, subdf.index.tolist()))
    events = list(map(lambda i: Event(coords[i][0], coords[i][1], times[i]), list(range(len(times)))))

    model = ContinuosDBSCAN(0.01, min_samples=4, continuos_time=3600)
    labels = np.array(model.fit(events))
    print(len(set(labels))-1, 'clusters found')
