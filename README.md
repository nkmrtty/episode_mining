# episode_mining
An inplementation of sequential patterm mining method [1].

## How to use
1. Set event sequence and episodes

    ```python
    sequence = sorted([
        (31, 'E'), (32, 'D'), (33, 'F'), (35, 'A'), (37, 'B'), (38, 'C'), (39, 'E'),
        (40, 'F'), (42, 'C'), (44, 'D'), (46, 'B'), (47, 'A'), (48, 'D'), (50, 'C'),
        (53, 'E'), (54, 'F'), (55, 'C'), (57, 'B'), (58, 'E'), (59, 'A'), (60, 'E'),
        (61, 'C'), (62, 'F'), (65, 'A'), (67, 'D'),
    ], key=lambda x:x[0])

    epi = sorted(['A', 'B', 'C', 'D', 'E', 'F', 'AA', 'AB', 'EF', 'CD',])
    ```

2. Initialize WINEPI class

    ```python
    >>> from episode_mining.winepi import WINEPI
    >>> w = WINEPI(sequence, episodes, 'parallel')
    # to mine serial episodes, set 'serial' insted of 'parallel'
    ```

3. Discover frequent (parallel) episodes

    ```python
    # discover_frequent_episodes(t_s, t_e, win, min_fr):
    #    t_s    : start time of target sequence
    #    t_e    : end time of target sequence
    #    win    : window size
    #    min_fr : threshold of frequency of episodes
    >>> w.discover_frequent_episodes(29, 68, 5, 0.1)
    [<ParallelEpisode: A / 0.46511627907>,
     <ParallelEpisode: B / 0.348837209302>,
     <ParallelEpisode: C / 0.558139534884>,
     <ParallelEpisode: D / 0.441860465116>,
     <ParallelEpisode: E / 0.511627906977>,
     <ParallelEpisode: F / 0.46511627907>,
     <ParallelEpisode: A B / 0.232558139535>,
     <ParallelEpisode: C D / 0.139534883721>,
     <ParallelEpisode: E F / 0.348837209302>]
    ```

4. Generate rules

    ```python
    # generate_rules(t_s, t_e, win, min_fr, min_conf)
    #    t_s      : start time of target sequence
    #    t_e      : end time of target sequence
    #    win      : window size
    #    min_fr   : threshold of frequency of episodes
    #    min_conf : threshold of confidence of rules
    >>> w.generate_rules(29, 68, 5, 0.1, 0.1)
    [<Rule: A -> A B / 0.5>,
     <Rule: B -> A B / 0.666666666667>,
     <Rule: C -> C D / 0.25>,
     <Rule: D -> C D / 0.315789473684>,
     <Rule: E -> E F / 0.681818181818>,
     <Rule: F -> E F / 0.75>]
    ```

## TODO
* Implement MINEPI method

# Reference
1. H. Mannila, H. Toivonen, and A. I. Verkamo, “Discovery of Frequent Episodes in Event Sequences,” Data Min. Knowl. Discov., vol. 1, no. 3, pp. 259–289, 1997.
