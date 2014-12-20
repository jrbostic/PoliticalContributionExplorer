"""This file should only be run as __main__ where no influence.db exists in project directory.
The constants defined at top of file are used by this process to determine what parameters will
be sent to api in the db creation script.

May be imported to gain access to json api call wrappers for retrieving political contributions and lobbies.
"""

import urllib
import ujson as json
import db_manager

__author__ = 'jessebostic'

# the api key to use while running script
API_KEY = '37fcf779b2674edba2ca46da7277c3be'

# upper bound for number of pages for script to run through
MAX_PAGES = 250

# the year for which results are desired
YEAR = '2013'

# the minimum contribution or lobby dollars relevant
MIN_AMOUNT = 10000


def get_contributions(api_key, page, year, per_page=1000, min_amount=0):
    """Returns list of dictionaries representing respective political contribution records.

    :param api_key: the api key to use on access
    :param page: the page number desired
    :param year: the year of record desired
    :param per_page: the number of results per page desired
    :param min_amount: the minimum dollar contribution desired
    :return: list of dicts representing individual political contributions
    """

    result = json.load(urllib.urlopen('http://transparencydata.com/api/1.0/contributions.json?apikey=' +
                                      '{}&page={}&per_page={}&cycle={}&amount=>|{}'
                                      .format(api_key, page, per_page, year, min_amount)))
    return result

def get_lobbies(api_key, page, year, per_page=100, min_amount=0):
    """Returns list of dictionaries representing respective political lobby records.

    :param api_key: the api key to use on access
    :param page: the page number desired
    :param year: the year of record desired
    :param per_page: the number of results per page desired
    :param min_amount: the minimum dollar lobby desired
    :return: list of dicts representing individual lobby instances
    """

    result = json.load(urllib.urlopen('http://transparencydata.com/api/1.0/lobbying.json?apikey=' +
                                      '{}&page={}&per_page={}&year={}&amount=>|{}'
                                      .format(api_key, page, per_page, year, min_amount)))
    return result

if __name__ == "__main__":

    db_manager.create_tables()

    # grab contributions and insert into db
    for i in xrange(1, MAX_PAGES + 1):

        print('Contribution (Page {})'.format(i))
        print('Retrieving and Loading...')
        result_list = get_contributions(API_KEY, i, YEAR, min_amount=MIN_AMOUNT)
        if len(result_list) == 0:
            break

        print('Populating...')
        conn, cursor = db_manager.open_conn()
        for contribution in result_list:
            db_manager.insert_contribution((contribution['contributor_name'], contribution['recipient_name'],
                                            float(contribution['amount'])), cursor)
        db_manager.close_conn(conn, cursor)

    # grab lobbies and insert into db
    for i in xrange(1, MAX_PAGES + 1):

        print('Lobby (Page {})'.format(i))
        print('Retrieving and Loading...')
        result_list = get_lobbies(API_KEY, i, YEAR, min_amount=MIN_AMOUNT)
        if len(result_list) == 0:
            break

        print('Populating...')
        conn, cursor = db_manager.open_conn()
        for lobby in result_list:
            db_manager.insert_lobby((lobby['client_name'], [agency['agency_name'] for agency in lobby['agencies']],
                                    float(lobby['amount'])), cursor)
        db_manager.close_conn(conn, cursor)