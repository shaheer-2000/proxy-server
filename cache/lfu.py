"""
Heap would perform better here, but left for future
"""

class CacheEntry:
	def __init__(self, value):
		self.value = value
		self.access_freq = 0

	def inc_access_freq(self):
		self.access_freq += 1

class LFU:
	def __init__(self, max_size=10):
		self.cache = {}
		self.size = 0
		self.max_size = max_size
	
	def put(self, key, value):
		if self.size >= self.max_size:
			self.evict()
		
		self.cache[key] = CacheEntry(value)
		self.size += 1

	def get(self, key):
		if key in self.cache:
			self.cache[key].inc_access_freq()
			return self.cache[key].value
		
		return None

	def evict(self):
		lfu_entry = min(self.cache.items(), key=lambda i: i[1].access_freq)
		del self.cache[lfu_entry[0]]
		self.size -= 1
