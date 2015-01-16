import sys, os, configparser, tempfile
import fb_config
import json

"""
	Util used to store and retrieve data during every starting
"""
class FBStore:

	config = None
	jsonobj = {"placeholder":1}

	def __init__(self, config):
		FBStore.config = config
		if FBStore.config.has_section('JSONStore'):
			self.json_filename = os.path.join(tempfile.gettempdir(), 'fb_store_json.json')
			print('temp store file: ', self.json_filename)
			if os.path.isfile(self.json_filename):
				self.load()
			else:
				self.store()

	def load(self):
		if os.path.isfile(self.json_filename):
			with open(self.json_filename, 'r') as json_file:
				self.jsonobj = json.load(json_file)

	def store(self):
		with open(self.json_filename, 'w') as json_file:
			json.dump(self.jsonobj, json_file)

	def getProperty(self, key):
		if ( key in self.jsonobj):
			return self.jsonobj[key]
		else:
			return None

	def setProperty(self, key, value):
		self.jsonobj[key] = value


if __name__ == '__main__':
	store = FBStore()
