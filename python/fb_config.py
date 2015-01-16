import sys, os, configparser

class FBConfig:

	config = None

	def __init__(self, config_filename=None):
		config_filename = ''
		if config_filename is None or config_filename == '':
			config_dir = os.getcwd()
			config_filename = os.path.join(config_dir, 'facebookad.cfg')

		FBConfig.config = configparser.RawConfigParser()
		print('debug configfile: ', config_filename)
		with open(config_filename, 'r') as config_file:
			FBConfig.config.readfp(config_file)
