class WPC(object):

    def __init__(self, _n):
        """
        Initialization of the class
        :param _n: The number of nodes in the system
        :return: Initializes the index and tree size lists
        """
        self.id = range(_n)
        self.sz = [0] * _n

    def root(self, _i):
        """
        Function to retrieve the root of a node. Utilizes path compression to make lookups fast.
        :param _i: The node to get the root of
        :return: The root of the specified node
        """
        while _i != self.id[_i]:
            self.id[_i] = self.id[self.id[_i]]
            _i = self.id[_i]
        return _i

    def connected(self, _p, _q):
        """
        A function to determine if two nodes are connected
        :param _p: The first node to check
        :param _q: The second node to check
        :return: Boolean if the two inputs are in the same connected component
        """
        return self.root(_p) == self.root(_q)

    def union(self, _p, _q):
        """
        A function to connect two nodes. Uses a weighted methodology in connecting the trees
        to avoid creating trees that are too tall (guaranteed that tree depth is max. log(N)).
        :param _p: The first node to connect
        :param _q: The second rode to connect
        :return: Graph updates to have the specified connected component, tree sizes update
        """
        i = self.root(_p)
        j = self.root(_q)
        if i == j:
            pass
        if self.sz[i] < self.sz[j]:
            self.id[i] = j
            self.sz[j] += self.sz[i]
        else:
            self.id[j] = i
            self.sz[i] += self.sz[j]
