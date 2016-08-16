# coding: utf-8
class Episode(object):
    def __init__(self, events):
        self.events = list(events)
        self.frequency = 0
        self.superepisodes = []
        self.score = 0.0

    def __iter__(self):
        for e in self.events:
            yield e

    def __len__(self):
        return len(self.events)

    def __repr__(self):
        return '<{}: {} / {}>'.format(
            type(self).__name__, ' '.join(self.events), self.score
        )

    def __getitem__(self, key):
        return self.events[key]


class ParallelEpisode(Episode):
    def __init__(self, events):
        Episode.__init__(self, events)
        self.event_count = 0
        self.freq_count = 0
        self.inwindow = 0

    def count(self, event_type):
        return self.events.count(event_type)


class SerialEpisode(Episode):
    def __init__(self, events):
        Episode.__init__(self, events)
        self.initialized = {}
        self.freq_count = 0
        self.inwindow = 0


class FrequentEpisodes(object):
    def __init__(self, episodes, size):
        self.episodes = episodes
        self.size = size
        self.block_start = [0] * len(episodes)

    def __len__(self):
        return len(self.episodes)

    def __iter__(self):
        for e in self.episodes:
            yield e

    def __getitem__(self, key):
        return self.episodes[key]

    def __contains__(self, episode):
        r = [e for e in self.episodes if e.events == episode.events]
        return len(r) > 0

    def append(self, episode):
        self.episodes.append(episode)

    def index(self, episode):
        for i, e in enumerate(self.episodes):
            if episode.events == e.events:
                return i
        return -1


class Rule(object):
    def __init__(self, antecedent, consequent, conf):
        self.antecedent = antecedent
        self.consequent = consequent
        self.conf = conf

    def __repr__(self):
        return '<{}: {} -> {} / {}>'.format(
            type(self).__name__, ' '.join(self.antecedent),
            ' '.join(self.consequent), self.conf
        )
