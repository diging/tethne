from tethne.classes.corpus import Corpus

import cPickle as pickle
import os


# TODO: persist the index and data.

class StreamingIndex(object):
    def __init__(self, name='index', base_path='.', serializer=pickle):
        """

        Parameters
        ----------
        basepath : str
            Location of the disk cache.
        """
        if not os.path.exists(base_path):
            raise IOError('No such directory')

        self.base_path = base_path
        self.index_path = os.path.join(base_path, name)

        if not os.path.exists(self.index_path):
            os.mkdir(self.index_path)

        self.key_file_map = {}

        self.serializer = serializer

    def __len__(self):
        return len(self.key_file_map)

    def items(self):
        keys = self.key_file_map.keys()
        while keys:
            key = keys.pop()
            yield key, self[key]

    def iteritems(self):
        return self.items()

    def _friendly_filename(self, name):
        return "".join([c for c in name if c.isalnum()])

    def _build_path(self, name):
        return os.path.join(self.index_path, name)

    def __setitem__(self, key, paper):
        fname = self._friendly_filename(key)
        fpath = self._build_path(fname)
        with open(fpath, 'w') as f:
            self.serializer.dump(paper, f)

        self.key_file_map[key] = fname

    def __contains__(self, key):
        return key in self.key_file_map

    def keys(self):
        return self.key_file_map.keys()

    def values(self):
        raise NotImplementedError('values() is not available in StreamingIndex')

    def update(self, data):
        for key, paper in data.iteritems():
            self.__setitem__(key, paper)

    def __getitem__(self, key):
        if key not in self.key_file_map:
            raise KeyError('No such key')

        fpath = self._build_path(self.key_file_map[key])
        with open(fpath, 'r') as f:
            paper = self.serializer.load(f)
        return paper


class StreamingCorpus(Corpus):
    """
    Provides memory-friendly access to large collections of metadata.
    """

    index_class = StreamingIndex

    @property
    def papers(self):
        class PList(object):
            def __init__(self, parent):
                self.parent = parent
            def __getitem__(self, key):
                return self.parent.indexed_papers[self.parent.indexed_papers.keys()[key]]

            def __iter__(self):
                keys = self.parent.indexed_papers.keys()
                while keys:
                    key = keys.pop()
                    yield self.parent.indexed_papers[key]

        return PList(self)

    def __init__(self, *args, **kwargs):
        base_path = kwargs.get('base_path', '.tethne')
        serializer = kwargs.get('serializer', pickle)
        self.index_kwargs.update({
            'base_path': base_path,
            'serializer':serializer
        })

        if not os.path.exists(base_path):
            os.mkdir(base_path)

        super(StreamingCorpus, self).__init__(*args, **kwargs)
