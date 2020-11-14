

class ITrouble:
    def __init__(self, args):
        raise NotImplemented
        
    def group_events(self, events):
        labels = self.group_model.fit(events)
        return labels
    
    def 