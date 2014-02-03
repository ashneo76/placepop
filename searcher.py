__author__ = 'ashish'

from providers.yelp import search as yelp_search
import optparse
import json
import yaml
import codecs


def handle_choices(choices_str, min_val, max_val):
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
				# skip in case of weird input
				continue

			if min_val <= choice_num <= max_val:
				choices_list.append(choice_num)
			elif choice_num == -1:
				choices_list = [-1]
				break

	return choices_list


def test_handle_choices():
	tests = ['3,4,5', '4,-1,6', 'a,5,6, -1', '4    , ,, 6', 'a,a, a ', '4,22, 9, 15']
	expected = [[3, 4, 5], [-1], [-1], [4, 6], [], [4, 9]]

	for i in xrange(0, len(tests)):
		actual = handle_choices(tests[i], 0, 10)
		if expected[i] == actual:
			print('Test {0} passed'.format(i))
			continue
		else:
			print('Failed at {0}. Actual is: {1}'.format(tests[i], actual))
			break


def get_choice(msg, min_val, max_val):
	while True:
		choices_str = raw_input(msg)
		try:
			status = handle_choices(choices_str, min_val, max_val)
			# if -1, then error occurred, retry, else return whatever was entered
			if status == -1:
				continue
			else:
				return status
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


def main():
	fout = None
	try:
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
				print(u'{0}.\t[{5}*] {1}:\t\t{2} @ \t{3}. \t\tTYPE: {4}'.format(i, business['name'], phone,
											pretty_address(business['location']['display_address']),
											pretty_categories(business['categories']), business['rating']))
				i += 1
			if len(businesses) > 0:
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
			else:
				fout.write(u'{0}|-1'.format(place))
	except KeyboardInterrupt:
		print('\n')
	finally:
		if fout is not None:
			fout.close()
		print('Done.')


if __name__ == '__main__':
	main()
	#test_handle_choices()