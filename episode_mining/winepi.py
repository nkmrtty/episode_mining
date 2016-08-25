#coding: utf-8
from . import ParallelEpisode, SerialEpisode, FrequentEpisodes, Rule


class WINEPI(object):
    def __init__(self, sequence, episodes=None, episode_type=None):
        self.sequence = sequence
        if episodes and episode_type:
            self.set_episodes(episodes, episode_type)
        elif episodes and not episode_type or not episodes and episode_type:
            raise Exception(
                '`episodes` and `episode_type` must be defined at once.'
            )

    def set_episodes(self, episodes, episode_type):
        if episode_type not in ('serial', 'parallel'):
            raise Exception(
                '`episode_type` must be `serial` or `parallel`'
            )
        self.episode_type = episode_type
        self.episodes = []

        if episode_type == 'serial':
            self.Episode = SerialEpisode
            self.recognize_candidate = self.recognize_candidate_serial
            self.candidate_generation = self.candidate_generation_serial
        elif episode_type == 'parallel':
            self.Episode = ParallelEpisode
            self.recognize_candidate = self.recognize_candidate_parallel
            self.candidate_generation = self.candidate_generation_parallel

        for epi in sorted(episodes):
            self.episodes.append(self.Episode(epi))

    def generate_rules(self, t_s, t_e, win, min_fr, min_conf):
        F = self.discover_frequent_episodes(t_s, t_e, win, min_fr)
        rules = []
        for epi in F:
            for super_epi in epi.superepisodes:
                conf = super_epi.score / epi.score
                if conf >= min_conf:
                    rules.append(Rule(epi, super_epi, conf))
        return rules

    def discover_frequent_episodes(self, t_s, t_e, win, min_fr):
        C = {}
        F = []
        size = 1
        C[size] = [e for e in self.episodes if len(e) == size]
        while len(C[size]) > 0:
            candidates = self.recognize_candidate(
                C[size], t_s, t_e, win, min_fr)
            for epi in candidates:
                F.append(epi)
            C[size+1] = self.candidate_generation(
                FrequentEpisodes(candidates, size))
            size += 1
        return F

    def candidate_generation_serial(self, frequent_episodes):
        l = frequent_episodes.size
        next_size_episodes = FrequentEpisodes([], l+1)
        k = 0
        go_to_next = False
        if l == 1:
            for h in range(len(frequent_episodes)):
                frequent_episodes.block_start[h] = 1
        for i in range(len(frequent_episodes)):
            current_block_start = k + 1
            for j in range(frequent_episodes.block_start[i],
                           len(frequent_episodes)):
                if (frequent_episodes.block_start[j]
                        != frequent_episodes.block_start[i]):
                    break
                # F[j] and F[i] have l-1 first event types in common,
                # build a potential candidate episode A as their combination.
                events_a = [None] * (l+1)
                for x in range(l):
                    events_a[x] = frequent_episodes[i][x]
                events_a[l] = frequent_episodes[j][l-1]
                episode_a = self.Episode(events_a)
                # build and test subepisodes B that do not contain A[y]
                events_b = [None] * l
                tested_episodes = set()
                for y in range(l+1):
                    for x in range(0, y):
                        events_b[x] = events_a[x]
                    for x in range(y, l):
                        events_b[x] = events_a[x+1]
                    episode_b = self.Episode(events_b)
                    idx = frequent_episodes.index(episode_b)
                    if idx == -1:
                        go_to_next = True
                        break
                    tested_episodes.add(idx)
                if go_to_next:
                    go_to_next = False
                    continue

                # is episode A in given set of episodes?
                if len([e for e in self.episodes if
                        e.events == episode_a.events]) == 0:
                    continue

                # epusode A is a superepisode of B
                for idx in tested_episodes:
                    frequent_episodes[idx].superepisodes.append(episode_a)

                # all subepisodes are in F, store episode A as candidate
                next_size_episodes.append(episode_a)
                next_size_episodes.block_start.append(current_block_start)
                k += 1
        return next_size_episodes

    def candidate_generation_parallel(self, frequent_episodes):
        l = frequent_episodes.size
        next_size_episodes = FrequentEpisodes([], l+1)
        k = 0
        go_to_next = False
        if l == 1:
            for h in range(len(frequent_episodes)):
                frequent_episodes.block_start[h] = 1
        for i in range(len(frequent_episodes)):
            current_block_start = k + 1
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
                episode_a = self.Episode(events_a)
                # build and test subepisodes B that do not contain A[y]
                events_b = [None] * l
                tested_episodes = set()
                for y in range(l+1):
                    for x in range(0, y):
                        events_b[x] = events_a[x]
                    for x in range(y, l):
                        events_b[x] = events_a[x+1]
                    episode_b = self.Episode(events_b)
                    idx = frequent_episodes.index(episode_b)
                    if idx == -1:
                        go_to_next = True
                        break
                    tested_episodes.add(idx)
                if go_to_next:
                    go_to_next = False
                    continue

                # is episode A in given set of episodes?
                if len([e for e in self.episodes if
                        e.events == episode_a.events]) == 0:
                    continue

                # epusode A is a superepisode of B
                for idx in tested_episodes:
                    frequent_episodes[idx].superepisodes.append(episode_a)

                # all subepisodes are in F, store episode A as candidate
                next_size_episodes.append(episode_a)
                next_size_episodes.block_start.append(current_block_start)
                k += 1
        return next_size_episodes

    def recognize_candidate_serial(self, episodes, t_s, t_e,
                                   win, min_fr):
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
        sequence = [s for s in self.sequence if t_s <= s[0] < t_e]
        for start in range(t_s-win+1, t_e+1):
            # bring in new events to the window
            t = start + win - 1
            beginsat[t] = set()
            transisions = set()
            new_events = [s[1] for s in sequence if s[0] == t]
            for e in new_events:
                if e not in waits:
                    continue
                for epi, j in sorted(waits[e], key=lambda x: x[0].events):
                    if j == len(epi) and epi.initialized[j-1] == 0:
                        epi.inwindow = start
                    if j == 1:
                        transisions.add((epi, 1, t))
                        if len(epi) == 1:
                            beginsat[epi.initialized[j-1]].discard((epi, j))
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
                    epi.inwindow_ids.extend(range(epi.inwindow, start))
                else:
                    waits[epi[l]].discard((epi, l+1))
                epi.initialized[l-1] = 0

       # output
        candidetes = []
        for epi in episodes:
            epi.score = float(epi.freq_count) / (t_e - t_s + win - 1)
            if epi.score >= min_fr:
                candidetes.append(epi)
        return candidetes

    def recognize_candidate_parallel(self, episodes, t_s, t_e,
                                     win, min_fr):
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
        sequence = [s for s in self.sequence if t_s <= s[0] < t_e]
        for start in range(t_s-win+1, t_e+1):
            # bring in new events to the window
            t = start + win - 1
            new_events = [s[1] for s in sequence if s[0] == t]
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
            old_events = [s[1] for s in sequence if s[0] == t]
            for e in old_events:
                try:
                    for epi in contains[(e, cnt_event[e])]:
                        if epi.event_count == len(epi):
                            epi.freq_count += start - epi.inwindow
                            epi.inwindow_ids.extend(range(epi.inwindow, start))
                        epi.event_count -= cnt_event[e]
                except KeyError:
                    pass
                try:
                    cnt_event[e] -= 1
                except KeyError:
                    pass

        # output
        candidetes = []
        for epi in episodes:
            epi.score = float(epi.freq_count) / (t_e - t_s + win - 1)
            if epi.score >= min_fr:
                candidetes.append(epi)
        return candidetes
