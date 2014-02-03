__author__ = 'ashish'

from providers.yelp import search as yelp_search
import optparse
import json
import yaml

def search():
	pass

if __name__ == '__main__':
	# yelp engine init
	yelp_cfg = yaml.load(file('yelp_cfg'))
	host = yelp_cfg['api']['host']
	path = yelp_cfg['api']['path']['search']
	s = yelp_search.Search()

	# search settings
	provider = 'yelp'
	s.location = 'chicago'

	s.term = 'vora'
	response = yelp_search.request(host=host, path=path, url_params=s.get_url_params(), consumer_key=yelp_cfg['consumer']['key'],
						consumer_secret=yelp_cfg['consumer']['secret'], token=yelp_cfg['token']['key'],
						token_secret=yelp_cfg['token']['secret'])

	print("{0} matches found for {1}".format(len(response['businesses']), s.term))


	print(response)