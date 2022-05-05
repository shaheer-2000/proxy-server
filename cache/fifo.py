import collections

class FIFO:
	def __init__(self, max_size=10):
		self.cache = collections.OrderedDict()
		self.size = 0
		self.max_size = max_size
	
	def put(self, key, value):
		if key in self.cache:
			self.cache[key] = value
		else:			
			if self.size >= self.max_size:
				self.evict()

			self.cache[key] = value
			self.size += 1

	def get(self, key):
		if key in self.cache:
			return self.cache[key]
		
		return None

	def evict(self):
		self.cache.popitem(last=False)
		self.size -= 1
