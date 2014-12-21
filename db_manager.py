"""Basically a small library for interfacing with the database(s).

Next step would be to incorporate more of original data set and merge the
year-specific dbs together.  Duplicate entries across consecutive years in feed
is a problem.  Also, various contributor name spelling differences require
merging entries.  Would probably work well as a class...
"""

import sqlite3

__author__ = 'jessebostic'


def open_conn(db_year=None):
    """Opens a new database connection (or creates new database)
    and gives back tuple containing connection and cursor into db.

    :param db_year: year of records desired
    :return: db connection, cursor
    """

    db_name = 'influence.db'
    if db_year is not None:
        db_name = 'influence{}.db'.format(db_year)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    return conn, cursor


def close_conn(conn, cursor):
    """Commits any changes in cursor, then closes db cursor and connection

    :param conn: connection to close
    :param cursor: cursor to commit from and close
    """

    conn.commit()
    cursor.close()
    conn.close()


def create_tables():
    """Creates rudimentary schema in a small set of tables."""

    conn, cursor = open_conn()
    cursor.execute('CREATE TABLE CONTRIBUTORS (contributor_name text, contribution_total real, lobby_total real)')
    cursor.execute('CREATE TABLE CONTRIBUTIONS (contributor_name text, recipient_name text, contribution_amount real)')
    cursor.execute('CREATE TABLE LOBBIES (contributor_name text, recipient_name text)')
    close_conn(conn, cursor)


def insert_contribution(values, cursor):
    """Inserts or updates entries in CONTRIBUTORS and CONTRIBUTIONS tables.

    :param values: tuple of values to insert (contributor_name, recipient_name, amount)
    :param cursor: cursor into target db
    """

    # update CONTRIBUTORS table
    contributor_entry = cursor.execute('SELECT * FROM CONTRIBUTORS '
                                       'WHERE contributor_name = ? LIMIT 1', (values[0],)).fetchone()
    if contributor_entry:
        cursor.execute('UPDATE CONTRIBUTORS SET contribution_total = ? WHERE contributor_name = ?',
                       (values[2]+contributor_entry[1], values[0]))
    else:
        cursor.execute('INSERT INTO CONTRIBUTORS VALUES (?,?,0.0)', (values[0], values[2]))

    # update CONTRIBUTIONS table
    contribution_entry = cursor.execute('SELECT * FROM CONTRIBUTIONS '
                                        'WHERE contributor_name = ? AND recipient_name = ? LIMIT 1',
                                        (values[0], values[1])).fetchone()
    if contribution_entry:
        cursor.execute('UPDATE CONTRIBUTIONS SET contribution_amount = ? '
                       'WHERE contributor_name = ? AND recipient_name = ?',
                       (values[2]+contribution_entry[2], values[0], values[1]))
    else:
        cursor.execute('INSERT INTO CONTRIBUTIONS VALUES (?, ?, ?)', values)


def insert_lobby(values, cursor):
    """Inserts or updates entries in CONTRIBUTORS and LOBBIES tables

    :param values: tuple of values to insert (contributor_name, recipient_name, amount)
    :param cursor: cursor into target db
    """

    # update CONTRIBUTORS table (only adding $ once since multiple target agencies possible in single lobby)
    contributor_entry = cursor.execute('SELECT * FROM CONTRIBUTORS '
                                       'WHERE contributor_name = ? LIMIT 1', (values[0],)).fetchone()
    if contributor_entry:
        cursor.execute('UPDATE CONTRIBUTORS SET lobby_total = ? WHERE contributor_name = ?',
                       (values[2]+contributor_entry[2], values[0]))
    else:
        cursor.execute('INSERT INTO CONTRIBUTORS VALUES (?,0.0,?)', (values[0], values[2]))

    # update LOBBIES table with contributor and recipient of not existent
    for i in xrange(len(values[1])):
        lobby_entry = cursor.execute('SELECT * FROM LOBBIES WHERE contributor_name = ? AND recipient_name = ? LIMIT 1',
                                     (values[0], values[1][i])).fetchone()
        if lobby_entry is None:
            cursor.execute('INSERT INTO LOBBIES VALUES (?,?)', (values[0], values[1][i]))


def get_contributor_names(search_str, year):
    """Returns list of contributor names filtered against search string.

    :param search_str: string to look for in contributor names
    :param year: records year to search
    :return: list of contributor names matching search_str
    """

    conn, cursor = open_conn(year)
    cursor.execute('SELECT contributor_name FROM CONTRIBUTORS '
                   'WHERE contributor_name LIKE ("%"||?||"%") ORDER BY contributor_name', (search_str,))
    name_list = cursor.fetchall()
    close_conn(conn, cursor)

    return [entry[0] for entry in name_list]


def get_contributor(contributor_name, year):
    """Returns a specific contributor entry based on exact name and year.

    :param contributor_name: name (key) of contributor to return
    :param year: record year desired
    :return: single contributor row tuple (name, cont_total, lobby_total)
    """

    conn, cursor = open_conn(year)
    cursor.execute('SELECT * FROM CONTRIBUTORS WHERE contributor_name = ?', (contributor_name,))
    contributor = cursor.fetchone()
    close_conn(conn, cursor)

    return contributor


def get_contributions(contributor_name, year):
    """Returns a list of contributions, recipients and amounts, for the
    contributor name and year provided.

    :param contributor_name: contributor name to match
    :param year: record year desired
    :return: list of row tuples [(recipient, amount), ... ]
    """

    conn, cursor = open_conn(year)
    cursor.execute('SELECT recipient_name, contribution_amount FROM CONTRIBUTIONS '
                   'WHERE contributor_name = ? ORDER BY recipient_name', (contributor_name,))
    contributions = cursor.fetchall()
    close_conn(conn, cursor)

    return contributions


def get_lobbies(contributor_name, year):
    """Returns a list of lobbies originating from contributor in specified year.

    :param contributor_name: name of lobby contributor
    :param year: record year desired
    :return: list of single value tuples containing agency names
    """

    conn, cursor = open_conn(year)
    cursor.execute('SELECT recipient_name FROM LOBBIES '
                   'WHERE contributor_name = ? ORDER BY recipient_name', (contributor_name,))
    lobbies = cursor.fetchall()
    close_conn(conn, cursor)

    return lobbies
