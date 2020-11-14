from .cdbscan import Event, ContinuosDBSCAN


class ClusteringModel(ContinuosDBSCAN):
    def __init__(self, eps, min_samples, continuos_time, **kwargs):
        super(ClusteringModel, self).__init__(eps, min_samples, continuos_time)
        
    
    def predict(self, events):
        assert all(list(map(lambda ev: isinstance(ev, Event), events)))
        
        labels = self.fit(events)
        result = list(zip(events, labels))
        return result
    
    
class CheckEmergencyModel():
    def __init__(self, dataset_path):
        raise NotImplemented
        
    def predict(self, events, df):
        # measures prob of given events (which belongs to one cluster) are emergency
        raise NotImplemented
    
