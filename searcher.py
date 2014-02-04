__author__ = 'ashish'

from providers.yelp import search as yelp_search
import optparse
import json
import yaml
import codecs
import geocode
import hashlib


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
            elif choice_num == 0:
                choices_list = [0]
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
        line = line.strip()
        if line.startswith('(') and line.endswith(')'):
            continue  # skip human readable addresses
        pretty_add += line + sep
    return pretty_add[0:-2]


def pretty_categories(category_list):
    pretty_cat = ''
    for category in category_list:
        pretty_cat += category[0] + ','
    return pretty_cat[0:-1]


def sanitize_yelp_business(buzinezz):
    business = {'name': buzinezz['name'], 'is_closed': buzinezz['is_closed']}
    if not 'location' in buzinezz or not 'display_address' in buzinezz['location']:
        business['display_address'] = ''
    else:
        business['display_address'] = pretty_address(buzinezz['location']['display_address'])
    if not 'display_phone' in buzinezz:
        business['display_phone'] = 'N/A'
    else:
        business['display_phone'] = buzinezz['display_phone']
    if not 'categories' in buzinezz:
        business['categories'] = []
    else:
        business['categories'] = pretty_categories(buzinezz['categories'])
    if not 'rating' in buzinezz:
        business['rating'] = 0
    else:
        business['rating'] = buzinezz['rating']
    if not 'review_count' in buzinezz:
        business['review_count'] = 0
    else:
        business['review_count'] = buzinezz['review_count']
    return business


def identify_business(business):
    h = hashlib.sha1()
    business['coords'] = geocode.geo_encode(business['display_address'])[0]['coords']
    h.update(business['coords'])
    business['uuid'] = h.hexdigest()


def main():
    parser = optparse.OptionParser('''
Google Geocode API Interface
        Geocodes an address or reverse geocodes a location using Google Maps API.
        Example: geocode -l <lat,long> OR geocode -a <address>''')
    parser.add_option("-i", "--input", dest="infile", 
                      help="YAML array list input file")
    parser.add_option("-o", "--output", dest="outfile", 
                      help="Output file")
    parser.add_option("-l", "--lookup", dest="search_terms", 
                      help="Search terms as CSV list")
    parser.add_option("-p", "--pretty", dest="pretty", action="store_true", default=False,
                      help="Pretty format or standard format")
    parser.add_option("-s", "--source", dest="source",
                      help="Business data provider")

    (options, args) = parser.parse_args()
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

        max_places = len(places)
        count = 0
        for place in places:
            count += 1
            print('[{1}/{2}] Looking up: {0}'.format(place, count, max_places))
            s.term = place
            response = yelp_search.request(host=host, path=path,
                            url_params=s.get_url_params(),
                            consumer_key=yelp_cfg['consumer']['key'],
                            consumer_secret=yelp_cfg['consumer']['secret'],
                            token=yelp_cfg['token']['key'],
                            token_secret=yelp_cfg['token']['secret'])

            businesses = response['businesses']
            print("{0} matches found for {1}".format(len(businesses), s.term))
            i = 1
            for buzinezz in businesses:
                business = sanitize_yelp_business(buzinezz)
                print(u'{0}.\t[{5}({6})]\t{1}:\t\t{2} @ \t{3}. \t\tTYPE: {4}'.format(i,
                                            business['name'],
                                            business['display_phone'],
                                            business['display_address'],
                                            business['categories'],
                                            business['rating'],
                                            business['review_count']))
                i += 1
            if len(businesses) > 0:
                choices = get_choice('Please choose from the above [0: Skip, -1: Save & quit]: ', 1, len(businesses))
                if choices[0] == -1:
                    break  # stop collecting stuff
                elif choices[0] == 0:
                    continue  # go to the next item

                for choice in choices:
                    buzinezz = businesses[int(choice)-1]
                    business = sanitize_yelp_business(buzinezz)
                    identify_business(business)
                    fout.write(u'{0}|{1}|{2}|{7}|{3}/5|{4}|{5}|{6}|{8}\n'.format(
                                        business['name'],
                                        business['display_phone'],
                                        business['display_address'],
                                        business['rating'],
                                        business['review_count'],
                                        business['is_closed'],
                                        business['categories'],
                                        business['coords'],
                                        business['uuid']))
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