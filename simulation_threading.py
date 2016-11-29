import getopt
import sys
import threading
import itertools
import Queue
import random

import numpy as np

import WeightedPathCompression as UF


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(StoppableThread, self).__init__(group, target, name,
                                              args, kwargs, verbose)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


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

    return res


def append_to_queue(nsamp, sz, _queue):
    r = monte_carlo_system(nsamp, sz)
    _queue.put(r)


def combine_results(_n_sims, _sz, _n_threads):
    split_work = _n_sims / _n_threads
    q = Queue.Queue()
    threads = []

    for i in range(_n_threads):
        t = StoppableThread(target=append_to_queue, args=(split_work, _sz, q))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    all_res = [q.get() for _ in xrange(split_work)]
    merged = list(itertools.chain.from_iterable(all_res))
    p_star = float(sum(merged))/len(merged)
    print('The value of p-star is %f ' % p_star)
    return merged


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:n:t:',
                                   ['simulations=', 'nodes=', 'threads='])
    except getopt.GetoptError, err:
        print(str(err))
        sys.exit(2)

    simulations = 1000
    nodes = 20
    threads = 1

    for opt, arg in opts:
        if opt in ('-s', '--simulations'):
            simulations = int(arg)
        elif opt in ('-n', '--nodes'):
            nodes = int(arg)
        elif opt in ('-t', '--threads'):
            threads = int(arg)

    combine_results(simulations, nodes, threads)
