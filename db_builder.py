import urllib
import ujson as json
import db_manager

__author__ = 'jessebostic'

MAX_PAGES = 200
YEAR = '2012'
MIN_AMOUNT = 10000


def get_contributions(page, year, per_page=1000, min_amount=0):
    result = urllib.urlopen('http://transparencydata.com/api/1.0/contributions.json?apikey=' +
                            '37fcf779b2674edba2ca46da7277c3be&page={}&per_page={}&cycle={}&amount=>|{}'
                            .format(page, per_page, year, min_amount))
    result_list = json.load(result)
    return result_list

def get_lobbies(page, year, per_page=100, min_amount=0):
    result = urllib.urlopen('http://transparencydata.com/api/1.0/lobbying.json?apikey=' +
                            '37fcf779b2674edba2ca46da7277c3be&page={}&per_page={}&year={}&amount=>|{}'
                            .format(page, per_page, year, min_amount))
    the_result_list = json.load(result)
    return the_result_list

if __name__ == "__main__":
    db_manager.create_tables()

    # grab contributions
    for i in xrange(1, MAX_PAGES + 1):

        print 'Contribution (Page {})'.format(i)
        result_list = get_contributions(i, YEAR, min_amount=MIN_AMOUNT)
        # result = urllib.urlopen('http://transparencydata.com/api/1.0/contributions.json?apikey=' +
        #                         '37fcf779b2674edba2ca46da7277c3be&page={}&cycle={}&amount=>|{}'.format(i, YEAR, MIN_AMOUNT))
        #
        # print 'Loading...'
        # the_result_list = json.load(result)

        if len(result_list) == 0:
            break

        print 'Populating...'
        conn, cursor = db_manager.open_conn()
        for contribution in result_list:
            db_manager.insert_contribution((contribution['contributor_name'], contribution['recipient_name'],
                                 float(contribution['amount'])), cursor)
        db_manager.close_conn(conn, cursor)

    # grab lobbies
    for i in xrange(1, MAX_PAGES + 1):

        print 'Lobby (Page {})'.format(i)
        result_list = get_lobbies(i, YEAR, min_amount=MIN_AMOUNT)
        # result = urllib.urlopen('http://transparencydata.com/api/1.0/lobbying.json?apikey=' +
        #                         '37fcf779b2674edba2ca46da7277c3be&page={}&year={}&amount=>|{}'.format(i, YEAR, MIN_AMOUNT))
        #
        # print 'Loading...'
        # the_result_list = json.load(result)
        if len(result_list) == 0:
            break

        print 'Populating...'
        conn, cursor = db_manager.open_conn()
        for lobby in result_list:
            db_manager.insert_lobby((lobby['client_name'], [agency['agency_name'] for agency in lobby['agencies']],
                          float(lobby['amount'])), cursor)
        db_manager.close_conn(conn, cursor)