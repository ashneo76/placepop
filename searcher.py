__author__ = 'ashish'

from providers.yelp import search as yelp_search
import optparse
import json
import yaml
import codecs


def search():
	pass


def get_choice(msg, min, max):
	while True:
		choices_str = raw_input(msg)
		try:
			choices = choices_str.split(',')
			choices_list = []
			for choice in choices:
				choice_num = choice.strip()
				if choice_num == '':
					continue
				else:
					try:
						choice_num = int(choice_num)
					except ValueError:
						continue
				if(choice_num >= min and choice_num <= max):
					choices_list.append(choice_num)
					# continue # for now we only take into consideration the first choice
				elif choice_num == -1:
					choices_list = [-1]
				else:
					continue
				return choices_list
		except EOFError:
			return [-1]
		except BaseException as e:
			print('Invalid choice. Please try again. ' + e.message)


def pretty_address(address_list):
	pretty_add = ''
	sep = ', '
	for line in address_list:
		pretty_add += line + sep
	return pretty_add[0:-2]


def pretty_categories(category_list):
	pretty_cat = ''
	for category in category_list:
		pretty_cat += category[0] + ','
	return pretty_cat[0:-1]

if __name__ == '__main__':
	# yelp engine init
	yelp_cfg = yaml.load(file('yelp_cfg'))
	host = yelp_cfg['api']['host']
	path = yelp_cfg['api']['path']['search']
	s = yelp_search.Search()

	# file input
	places = yaml.load(file('inputplaces'))
	fout = codecs.open('outputplaces', 'w+', encoding="UTF-8")

	# search settings
	provider = 'yelp'
	s.location = 'chicago'

	for place in places:
		print('Looking up: {0}'.format(place))
		s.term = place
		response = yelp_search.request(host=host, path=path, url_params=s.get_url_params(), consumer_key=yelp_cfg['consumer']['key'],
						consumer_secret=yelp_cfg['consumer']['secret'], token=yelp_cfg['token']['key'],
						token_secret=yelp_cfg['token']['secret'])

		businesses = response['businesses']
		print("{0} matches found for {1}".format(len(businesses), s.term))
		i = 1
		for business in businesses:
			try:
				phone = business['display_phone']
			except KeyError:
				phone = 'N/A'
			print(u'{0}.\t{1}[{5}*]: \t{2} @ \t{3}. \t\tTYPE: {4}'.format(i, business['name'], phone,
										pretty_address(business['location']['display_address']),
										pretty_categories(business['categories']), business['rating']))
			i += 1
		choices = get_choice('Please choose one of the above: ', 1, len(businesses))
		if choices[0] == -1:
			break

		for choice in choices:
			business = businesses[int(choice)-1]
			try:
				phone = business['display_phone']
			except KeyError:
				phone = 'N/A'
			fout.write(u'{0}|{1}|{2}|{3}/5|{4}|{5}|{6}\n'.format(business['name'], phone,
								pretty_address(business['location']['display_address']), business['rating'],
								business['review_count'], business['is_closed'], pretty_categories(business['categories'])))

	fout.close()
	print('Done.')
