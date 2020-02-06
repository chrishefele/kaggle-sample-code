import os.path
import cPickle as pickle

CACHE_PRINT_MOD = 10 # TODO increase? 


class Cache:

    def __init__(self, cache_file):
        self.cache_file = cache_file
        self.load_cache()

    def __getitem__(self, key):
        return self.cache[key]

    def __contains__(self, key):
        return key in self.cache

    def __setitem__(self, key, value):
        self.cache[key] = value

    def load_cache(self):
        if self.cache_file and os.path.isfile(self.cache_file):
            print "Loading cache from ", self.cache_file
            self.cache = pickle.load(open(self.cache_file, 'rb')) 
            print "Read cache with ", len(self.cache), "entries"
        elif self.cache_file and not os.path.isfile(self.cache_file):
            print self.cache_file, "Not found! Initializing cache and new cache file"
            self.clear_cache()
        else:
            print "No cache filename specified for loading. None loaded."
            self.cache = {}

    def clear_cache(self):
        print "Clearing cache"
        self.cache = {}
        self.save_cache()

    def save_cache(self):
        if self.cache_file:
            print "Saving cache to:", self.cache_file
            pickle.dump(self.cache, open(self.cache_file, "wb"))
            print "Saved cache contains", len(self.cache), "entries"
        else:
            print "No cache filename specified for saving. None saved."

    def print_cache_stats(self):
        # print periodic cache size updates as the cache grows 
        cache_size = len(self.cache)
        if cache_size % CACHE_PRINT_MOD == 0:
            print "FYI Cache size increased to", cache_size,
            print "for", self.cache_file

