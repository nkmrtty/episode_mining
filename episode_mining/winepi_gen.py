# coding: utf-8
from . import ParallelEpisode, SerialEpisode, FrequentEpisodes, Rule
from .winepi import WINEPI


class WINEPIGen(WINEPI):
    """ Extended class for finding episodes automatically. """
    def __init__(self, sequence, episode_type):
        WINEPI.__init__(self, sequence)

        if episode_type == 'serial':
            self.Episode = SerialEpisode
            self.recognize_candidate = self.recognize_candidate_serial
            self.candidate_generation = self.candidate_generation_serial
        elif episode_type == 'parallel':
            self.Episode = ParallelEpisode
            self.recognize_candidate = self.recognize_candidate_parallel
            self.candidate_generation = self.candidate_generation_parallel

    def generate_rules(self, t_s, t_e, win, min_fr, min_conf, max_size):
        F = self.discover_frequent_episodes(t_s, t_e, win, min_fr, max_size)
        rules = []
        for epi in F:
            for super_epi in epi.superepisodes:
                conf = super_epi.score / epi.score
                if conf >= min_conf:
                    rules.append(Rule(epi, super_epi, conf))
        return rules

    def discover_frequent_episodes(self, t_s, t_e, win, min_fr, max_size):
        C = {}
        F = []
        size = 1
        C[size] = [self.Episode(e) for e in
                   sorted(set([e for _, e in self.sequence]))]
        while len(C[size]) > 0 and size <= max_size:
            print size
            candidates = self.recognize_candidate(
                C[size], t_s, t_e, win, min_fr
            )
            F.extend(candidates)

            C[size+1] = self.candidate_generation(
                FrequentEpisodes(candidates, size)
            )
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

                # Has episode A already checked? skip it.
                if len([e for e in next_size_episodes if e == episode_a]) != 0:
                    continue

                # epusode A is a superepisode of B
                for idx in tested_episodes:
                    frequent_episodes[idx].superepisodes.append(episode_a)

                # all subepisodes are in F, store episode A as candidate
                next_size_episodes.append(episode_a)
                next_size_episodes.block_start.append(current_block_start)
                k += 1
        return next_size_episodes
