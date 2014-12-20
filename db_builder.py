import urllib
import ujson as json
from db_manager import *

__author__ = 'jessebostic'

MAX_PAGES = 200
YEAR = '2012'
MIN_AMOUNT = 10000

create_tables()

# grab contributions
for i in xrange(1, MAX_PAGES + 1):

    print 'Contribution (Page {})'.format(i)
    result = urllib.urlopen('http://transparencydata.com/api/1.0/contributions.json?apikey=' +
                            '37fcf779b2674edba2ca46da7277c3be&page={}&cycle={}&amount=>|{}'.format(i, YEAR, MIN_AMOUNT))

    print 'Loading...'
    the_result_list = json.load(result)
    if len(the_result_list) == 0:
        break

    print 'Populating...'
    conn, cursor = open_conn()
    for contribution in the_result_list:
        insert_contribution((contribution['contributor_name'], contribution['recipient_name'],
                             float(contribution['amount'])), cursor)
    close_conn(conn, cursor)

# grab lobbies
for i in xrange(1, MAX_PAGES + 1):

    print 'Lobby (Page {})'.format(i)
    result = urllib.urlopen('http://transparencydata.com/api/1.0/lobbying.json?apikey=' +
                            '37fcf779b2674edba2ca46da7277c3be&page={}&year={}&amount=>|{}'.format(i, YEAR, MIN_AMOUNT))

    print 'Loading...'
    the_result_list = json.load(result)
    if len(the_result_list) == 0:
        break

    print 'Populating...'
    conn, cursor = open_conn()
    for lobby in the_result_list:
        insert_lobby((lobby['client_name'], [agency['agency_name'] for agency in lobby['agencies']],
                      float(lobby['amount'])), cursor)
    close_conn(conn, cursor)