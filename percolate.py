import itertools
import numpy as np
import random

import WeightedPathCompression as UF


def simulate_system(_n):
    """
    :param _n: The number of nodes in the system, should be large
    :return:
    """
    grid = _n**2
    # Trick: add top and bottom nodes
    grid += 2
    index_list = range(_n**2)
    vacant_list = range(_n**2)
    open_sites = []
    head = _n**2
    tail = _n**2 + 1
    state = UF.WPC(grid)
    # Connect top components
    for k in index_list[0:_n]:
        state.union(head, k)
    for k in index_list[-_n:]:
        state.union(tail, k)

    while not state.connected(head, tail):
        c = sample_no_replace(index_list)
        open_sites.append(c)
        try:
            vacant_list.remove(c)
        except ValueError:
            pass
        o = grid_connection_rules(c, _n)
        for pt in o:
            if pt in open_sites:
                if not state.connected(head, tail):
                    state.union(pt, c)
                    try:
                        vacant_list.remove(pt)
                    except ValueError:
                        pass

    return float(len(open_sites))/(_n**2)


def sample_no_replace(_lst):
    choice = random.sample(_lst, 1)[0]
    _lst.remove(choice)
    return choice


def grid_connection_rules(_p, _n):
    """
    :param _p: The selected node to connect
    :param _n: The number of nodes in the grid
    :return: The adjacent open sites
    """
    # Need to fix this to connect to only neighboring open sites
    index_list = range(_n**2)
    top_edge = range(0, _n-1)
    bottom_edge = range((_n**2)-_n, _n**2)
    left_edge = np.arange(0, _n**2, _n)
    right_edge = left_edge + (_n-1)
    el = [top_edge, bottom_edge, left_edge, right_edge]
    edges = [i for i in itertools.chain.from_iterable(el)]
    center_points = [x for x in index_list if x not in edges]
    if _p in center_points:
        out = [_p+1, _p-1, _p+_n, _p-_n]
    elif (_p in left_edge) & (_p not in top_edge) & (_p not in bottom_edge):
        out = [_p+_n, _p-_n, _p+1]
    elif (_p in right_edge) & (_p not in top_edge) & (_p not in bottom_edge):
        out = [_p+_n, _p-_n, _p-1]
    elif (_p in left_edge) & (_p in top_edge):
        out = [_p+_n, _p+1]
    elif (_p in left_edge) & (_p in bottom_edge):
        out = [_p-_n, _p+1]
    elif (_p in right_edge) & (_p in top_edge):
        out = [_p+_n, _p-1]
    elif (_p in right_edge) & (_p in bottom_edge):
        out = [_p-_n, _p-1]
    elif (_p in top_edge) & (_p not in right_edge) & (_p not in left_edge):
        out = [_p+1, _p-1, _p+_n]
    elif (_p in bottom_edge) & (_p not in right_edge) & (_p not in left_edge):
        out = [_p+1, _p-1, _p-_n]
    return out


def monte_carlo_system(_ntrials, _size): 
    res = []
    while _ntrials > 0:
        res.append(simulate_system(_size))
        _ntrials -= 1

    p_star = float(sum(res))/len(res)
    print('The value of p-star is %f ' % p_star)
    return res
