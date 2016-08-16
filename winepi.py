# coding: utf-8
class Episode(object):
    def __init__(self, events):
        self.events = events
        self.event_count = 0
        self.freq_count = 0
        self.inwindow = 0
        self.initialized = [0] * len(events)
        self.score = 0

    def __iter__(self):
        for e in self.events:
            yield e

    def __len__(self):
        return len(self.events)

    def __repr__(self):
        return '<{}: {}, {}, {}>'.format(
            type(self).__name__, self.events, self.freq_count, self.score)

    def __getitem__(self, key):
        return self.events[key]

    def count(self, label):
        return self.events.count(label)


class FrequentEpisodes(object):
    def __init__(self, episodes, size, episode_type):
        self.episodes = episodes
        self.size = size
        self.episode_type = episode_type
        self.block_start = [0] * len(episodes)

    def __len__(self):
        return len(self.episodes)

    def __getitem__(self, key):
        return self.episodes[key]

    def __contains__(self, episode):
        r = [e for e in self.episodes if e.events == episode.events]
        return len(r) > 0

    def append(self, episode):
        self.episodes.append(episode)


# Algorithm 1
def generate_rules(episodes, event_sequence, win, min_fr, min_conf,
                   episode_type):
    F = discover_frequent_episodes(
        episodes, event_sequence, win, min_fr, episode_type)



# Algorithm 2
def discover_frequent_episodes(episodes, event_sequence, win, min_fr,
                               episode_type):
    C = {}
    F = {}
    size = 1
    C[size] = [e for e in episodes if len(e) == size]
    while len(C[size]) > 0:
        if episode_type == 'parallel':
            F[size] = recognize_candidate_parallel_episodes(
                episodes, event_sequence, size, win, min_fr)
            size += 1
            C[size] = candidate_generation_parallel(F[size-1])
        elif episode_type == 'serial':
            F[size] = recognize_candidate_serial_episodes(
                episodes, event_sequence, size, win, min_fr)
            size += 1
            C[size] = candidate_generation_serial(F[size-1])
    return F


# Algorithm 3
def candidate_generation_parallel(frequent_episodes):
    l = frequent_episodes.size
    next_size_episodes = FrequentEpisodes(
        [], l+1, frequent_episodes.episode_type)
    k = 0
    go_to_next = False
    if l == 1:
        for h in range(len(frequent_episodes)):
            frequent_episodes.block_start[h] = 1
    for i in range(len(frequent_episodes)):
        current_block_start = k + 1
        j = i
        for j in range(i, len(frequent_episodes)):
            if (frequent_episodes.block_start[j]
                    != frequent_episodes.block_start[i]):
                break
            # F[j] and F[i] have l-1 first event types in common,
            # build a potential candidate episode A as their combination.
            events_a = [None] * (l+1)
            for x in range(l):
                events_a[x] = frequent_episodes[i][x]
            events_a[l] = frequent_episodes[j][l-1]
            episode_a = Episode(events_a)
            print episode_a
            # build and test subepisodes B that do not contain A[y]
            events_b = [None] * (l+1)
            for y in range(1, l):
                for x in range(1, y):
                    events_b[x] = events_a[x]
                for x in range(y, l+1):
                    events_b[x] = events_a[x+1]
                episode_b = Episode(events_b)
                if episode_b not in frequent_episodes:
                    go_to_next = True
                    break
            if go_to_next:
                go_to_next = False
                continue
            # all subepisodes are in F, store episode A as candidate
            next_size_episodes.append(episode_a)
            next_size_episodes.block_start.append(current_block_start)
            k += 1
    return next_size_episodes


def candidate_generation_serial(frequent_episodes):
    pass


# Algorithm 4
def recognize_candidate_parallel_episodes(episodes, event_sequence,
                                          size, win, min_fr):
    # unpack
    sequence, t_s, t_e = event_sequence

    # initialize
    cnt_event = {}
    contains = {}
    for epi in episodes:
        for event in epi:
            cnt_event[event] = 0
            for i in range(1, len(epi)+1):
                contains[(event, i)] = set()
    for epi in episodes:
        for event in epi:
            num = epi.count(event)
            contains[(event, num)].add(epi)
        epi.event_count = 0
        epi.freq_count = 0
    # recognition
    for start in range(t_s-win+1, t_e+1):
        # bring in new events to the window
        t = start + win - 1
        new_events = [s[0] for s in sequence if s[1] == t]
        for e in new_events:
            if e not in cnt_event:
                continue
            cnt_event[e] += 1
            try:
                for epi in contains[(e, cnt_event[e])]:
                    epi.event_count += cnt_event[e]
                    if epi.event_count == len(epi):
                        epi.inwindow = start
            except KeyError:
                pass
        # drop out old events from the window
        t = start - 1
        old_events = [s[0] for s in sequence if s[1] == t]
        for e in old_events:
            try:
                for epi in contains[(e, cnt_event[e])]:
                    if epi.event_count == len(epi):
                        epi.freq_count += start - epi.inwindow
                    epi.event_count -= cnt_event[e]
            except KeyError:
                pass
            cnt_event[e] -= 1

    # output
    candidetes = []
    for epi in episodes:
        epi.score = float(epi.freq_count) / (t_e - t_s + win - 1)
        if epi.score >= min_fr:
            candidetes.append(epi)
    return FrequentEpisodes(candidetes, size, 'parallel')


# Algorithm 5
def recognize_candidate_serial_episodes(episodes, event_sequence,
                                        size, win, min_fr):
    # unpack
    sequence, t_s, t_e = event_sequence

    # initialize
    waits = {}
    beginsat = {}
    for epi in episodes:
        for i in range(len(epi)):
            epi.initialized[i] = 0
            waits[epi[i]] = set()
    for epi in episodes:
        waits[epi[0]].add((epi, 1))
        epi.freq_count = 0
    for t in range(t_s-win, t_s+1):
        beginsat[t] = set()

    # recognition
    for start in range(t_s-win+1, t_e+1):
        # bring in new events to the window
        t = start + win - 1
        beginsat[t] = set()
        transisions = set()
        new_events = [s[0] for s in sequence if s[1] == t]
        for e in new_events:
            if e not in waits:
                continue
            for epi, j in sorted(waits[e], key=lambda x: x[0].events):
                if j == len(epi) and epi.initialized[j-1] == 0:
                    epi.inwindow = start
                if j == 1:
                    transisions.add((epi, 1, t))
                else:
                    transisions.add((epi, j, epi.initialized[j-2]))
                    beginsat[epi.initialized[j-2]].discard((epi, j-1))
                    epi.initialized[j-2] = 0
                    waits[e].discard((epi, j))

        for epi, j, t in transisions:
            epi.initialized[j-1] = t
            beginsat[t].add((epi, j))
            if j < len(epi):
                waits[epi[j]].add((epi, j+1))
        # drop out old events from the window
        for epi, l in beginsat[start-1]:
            if l == len(epi):
                epi.freq_count += start - epi.inwindow
            else:
                waits[epi[l]].discard((epi, l+1))
            epi.initialized[l-1] = 0

   # output
    candidetes = []
    for epi in episodes:
        epi.score = float(epi.freq_count) / (t_e - t_s + win - 1)
        if epi.score >= min_fr:
            candidetes.append(epi)
    return FrequentEpisodes(candidetes, size, 'serial')
