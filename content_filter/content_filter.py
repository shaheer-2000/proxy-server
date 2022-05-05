"""
Global Content Filter
"""

import pickle
import pathlib

class ContentFilter:
	def __init__(self, database_path="./database", blacklisted_pages: list=[]):
		self.database_path = pathlib.Path(database_path).resolve()
		self.dump_path = self.database_path / "filtered_content.pickle"
		self.blacklisted_pages = blacklisted_pages

		self.load()

	def blacklist(self, page):
		if page in self.blacklisted_pages:
			return

		self.blacklisted_pages.append(page)

	def unblacklist(self, page):
		if page in self.blacklisted_pages:
			self.blacklisted_pages.remove(page)

	def get_blacklisted_pages(self):
		return self.blacklisted_pages

	def save(self):
		self.dump()

	def dump(self):
		if not self.database_path.exists():
			self.database_path.mkdir(parents=True, exist_ok=True)

		with open(self.dump_path, "wb") as f:
			pickle.dump(self.blacklisted_pages, f)

	def load(self):
		if self.dump_path.exists():
			with open(self.dump_path, "rb") as f:
				self.blacklisted_pages = pickle.load(f)
