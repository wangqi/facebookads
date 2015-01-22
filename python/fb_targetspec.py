import sys, os, traceback, time
import json
import argparse
import fb_config
from facebookads.api import FacebookAdsApi
from facebookads import objects

"""
	Util used to retrive given country's target spec
	Default policy is splitted a country by gender, age(5) and region
"""
class FBTargetSpec:

	config = None
	api = None
	interval = 1

	class TargetSpec:
		GENDER_MALE = 1
		GENDER_FEMALE = 2

		countries = []
		regions = []
		region_names = []
		genders = [GENDER_MALE]
		age_min = 13
		age_max = 65

		def __init__(self, countries=[], region_names=[], regions=[], genders=[GENDER_MALE], age_min=13, age_max=65):
			self.countries = countries
			self.region_names = region_names
			self.regions = regions
			self.genders = genders
			self.age_min = age_min
			self.age_max = age_max

		def __repr__(self):
			#return "{{'geo_locations':{{'countries': {countries}, 'regions': {regions} }}, 'age_min':{age_min}, 'age_max':{age_max}, 'genders':{genders} }} ".format(
			return "{{'geo_locations':{{'regions': {regions} }}, 'age_min':{age_min}, 'age_max':{age_max}, 'genders':{genders} }} ".format(
				#countries=self.countries,
				regions=self.regions,
				age_min=self.age_min,
				age_max=self.age_max,
				genders=self.genders
				)

		def tostring(self):
			return "{countries}\t{region_names}\t{age_min}\t{age_max}\t{genders}".format(
				countries=','.join(str(x) for x in self.countries),
				region_names=','.join(str(x) for x in self.region_names),
				genders=','.join(str(x) for x in self.genders),
				age_max=self.age_max,
				age_min=self.age_min
				)

		def name(self):
			region_names = []
			for region in self.region_names:
				region = region.replace(', ', '-')
				region_names.append(region)
			return "{countries}_{region_names}_{age_min}_{age_max}_{genders}".format(
				countries=','.join(str(x) for x in self.countries),
				region_names=','.join(str(x) for x in region_names),
				genders=','.join(str(x) for x in self.genders),
				age_max=self.age_max,
				age_min=self.age_min
				)
			
	class ReachEstimateResult:
		targeting_spec = None
		users = 0,
		cpa_max = 0.0,
		cpa_median = 0.0,
		cpa_min = 0.0,
		cpc_max = 0.0,
		cpc_median = 0.0,
		cpc_min = 0.0,
		cpm_max = 0.0,
		cpm_median = 0.0,
		cpm_min = 0.0,
		estimate_ready = True

		def __init__(self, spec):
			self.targeting_spec = spec

		def __repr__(self):
			return "{users:.0f}\t{cpa_max:0.2f}\t{cpa_min:0.2f}\t{cpa_median:0.2f}\t{cpc_max:0.2f}\t{cpc_min:0.2f}\t{cpc_median:0.2f}\t{cpm_max:0.2f}\t{cpm_min:0.2f}\t{cpm_median:0.2f}".format(
				users=self.users,cpa_max=self.cpa_max,cpa_min=self.cpa_min,cpa_median=self.cpa_median,
				cpc_max=self.cpc_max, cpc_min=self.cpc_min, cpc_median=self.cpc_median, cpm_max=self.cpm_max, 
				cpm_min=self.cpm_min, cpm_median=self.cpm_median)

	def __init__(self, config=None):
		self.config = fb_config.FBConfig(config).config
		self.interval = float(self.config.get('Defaults', 'call_interval'))
		self.account_id = 'act_' + self.config.get('Defaults', 'ad_account')
		auth_info = (
		    self.config.get('Authentication', 'app_id'),
		    self.config.get('Authentication', 'app_secret'),
		    self.config.get('Authentication', 'access_token')
		    )
		FacebookAdsApi.init(*auth_info)

	"""
		Search all regions in a given country.
		Example
			"data": [{
				"key": "1883",
				"name": "Aichi, Japan",
				"type": "region",
				"country_code": "JP",
				"supports_region": true,
				"supports_city": true
			}, {
				"key": "1884",
				"name": "Akita, Japan",
				"type": "region",
				"country_code": "JP",
				"supports_region": true,
				"supports_city": true
			}, {
	"""
	def searchRegionByCountry(self, country, genders=[TargetSpec.GENDER_MALE], age_min=13, age_max=65, age_step=5, file='targetspec.txt'):
		#print(age_step)
		search = objects.TargetingSearch.searchRegionByCountry(
			type = 'adgeolocation',
			country = country
			)
		response = json.loads(search._body)
		specs = []
		data = response.get('data')
		for d in data:
			key = d.get('key')
			supports_region = d.get('supports_region')
			name = d.get('name')
			country_code = d.get('country_code')
			# countries=[], regions=[], genders=[GENDER_MALE], age_min=13, age_max=65
			for age in range(age_min, age_max, age_step):
				max = age + age_step
				if max > age_max:
					max = age_max
				#countries=[], region_names=[], regions=[], genders=[GENDER_MALE], age_min=13, age_max=65):
				spec = self.TargetSpec(countries=[country], region_names=[name], regions=[{'key': key}], genders=genders, age_min=age, age_max=max)
				specs.append(spec)
		
		with open(file, 'w') as outfile:
			for spec in specs:
				estimates = self.reachEstimate(spec)
				if len(estimates)>0:
					estimate = estimates[0]
				print(spec.name(), spec.__repr__(), estimate, sep='\t')
				print(spec.name(), spec.__repr__(), estimate, sep='\t', file=outfile)

		ret = []

	"""
		Search the targeting spec and return the estimated value
		by Facebook.
		Example:
			targeting_spec: {'geo_locations':{'countries': ['JP']}}
			result:
				{
				    "bid_estimations": [
				        {
				            "cpa_max": 1567,
				            "cpa_median": 1130,
				            "cpa_min": 551,
				            "cpc_max": 53,
				            "cpc_median": 39,
				            "cpc_min": 22,
				            "cpm_max": 620,
				            "cpm_median": 420,
				            "cpm_min": 103,
				            "location": 3,
				            "unsupported": false
				        }
				    ],
				    "estimate_ready": true,
				    "users": 22000000
				}
	"""
	def reachEstimate(self, spec):
		my_account = objects.AdAccount(self.account_id)
		reachEstimates = my_account.get_reach_estimate(
			params={
			'currency': 'USD',
			'targeting_spec': spec
			})
		ret = []
		for re in reachEstimates:
			users = re.get('users')
			bid_estimation = re.get('bid_estimations')
			if len(bid_estimation) > 0:
				bid_estimation = bid_estimation[0]
			estimate_ready = re.get('estimate_ready')
			result = FBTargetSpec.ReachEstimateResult(spec)
			result.users = users
			result.cpa_max = bid_estimation.get('cpa_max')/100
			result.cpa_min = bid_estimation.get('cpa_min')/100
			result.cpa_median = bid_estimation.get('cpa_median')/100
			result.cpc_max = bid_estimation.get('cpc_max')/100
			result.cpc_min = bid_estimation.get('cpc_min')/100
			result.cpc_median = bid_estimation.get('cpc_median')/100
			result.cpm_max = bid_estimation.get('cpm_max')/100
			result.cpm_min = bid_estimation.get('cpm_min')/100
			result.cpm_median = bid_estimation.get('cpm_median')/100
			ret.append(result)
			time.sleep(self.interval)
		#print(ret)
		return ret


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Facebook Targetting Spec Tool')
	parser.add_argument('-c', '--config', help="The absoluate path to configuration file.")
	
	#extgroup = parser.add_mutually_exclusive_group(required=True)
	#extgroup.add_parser('query', help="tst")
	#extgroup.add_argument('-q', '--query', action='store_true', help='Query and output the specified countries\' spec and reach estimate data.')
	#extgroup.add_argument('-i', '--import', action='store_true', help='Import the targeting_spec generated by "query" command and created audience groups')

	subparsers = parser.add_subparsers(help="Supported commands", dest="command")
	parser_query = subparsers.add_parser("query", help="Query and output the specified countries\' spec and reach estimate data.")
	parser_query.add_argument('-f', '--file', default='targetspec.txt', help='The tab separated file that will be exported')
	parser_query.add_argument('-ct', '--country', default='JP', help="The country code for example JP for Japan.")
	parser_query.add_argument('-ef', '--exclude-female', default=True, action='store_true', help="All females will be exluded by default")
	parser_query.add_argument('--age-min', default=13, action='store', type=int, help="The minimal age")
	parser_query.add_argument('--age-max', default=65, action='store', type=int, help="The maximum age")
	parser_query.add_argument('--age-step', default=5, action='store', type=int, help="The step between age_min and age_max")

	parser_import = subparsers.add_parser("import", help="Import the targeting_spec generated by 'query' command and created audience groups")
	parser_import.add_argument('-f', '--file', help='The tab separated file that will be imported')


	args = parser.parse_args()
	target = None
	if args.config:
		configfile = args.config
		print('configfile:', configfile)
		target = FBTargetSpec(configfile)
	else:
		target = FBTargetSpec()
	
	if args.command == 'query':
		#print(args)
		genders = [target.TargetSpec.GENDER_MALE]
		if not args.exclude_female:
			genders.append(target.TargetSpec.GENDER_FEMALE)
		target.searchRegionByCountry(country=args.country, genders=genders, age_min=args.age_min, 
			age_max=args.age_max, age_step=args.age_step, file=args.file)
	elif args.command == 'import':
		#target.reachEstimate({'geo_locations':{'countries': ['JP'], 'regions': [] }, 'age_min':13, 'age_max':65, 'genders':[1] })
		target.reachEstimate({'geo_locations': {'regions': [{'key':'1929'}] }, 'age_min':61, 'age_max':65, 'genders':[1] })
	
	
	#t = target.TargetSpec(countries=['JP'], genders=[FBTargetSpec.TargetSpec.GENDER_MALE])
	#print(t)

