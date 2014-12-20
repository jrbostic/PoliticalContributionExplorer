import sqlite3

__author__ = 'jessebostic'


def open_conn():
    conn = sqlite3.connect('influence.db')
    cursor = conn.cursor()
    return conn, cursor


def close_conn(conn, cursor):
    conn.commit()
    cursor.close()
    conn.close()


def create_tables():
    conn, cursor = open_conn()
    cursor.execute('CREATE TABLE CONTRIBUTORS (contributor_name text, contribution_total real, lobby_total real)')
    cursor.execute('CREATE TABLE CONTRIBUTIONS (contributor_name text, recipient_name text, contribution_amount real)')
    cursor.execute('CREATE TABLE LOBBIES (contributor_name text, recipient_name text)')
    close_conn(conn, cursor)


def insert_contribution(values, cursor):
    """Inserts or updates entries in CONTRIBUTOR and CONTRIBUTIONS tables"""

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
    """Inserts, updates, or replaces entries in CONTRIBUTOR and LOBBIES tables"""

    # update CONTRIBUTORS table (only adding $ once since multiple target agencies possible in single lobby)
    contributor_entry = cursor.execute('SELECT * FROM CONTRIBUTORS '
                                       'WHERE contributor_name = ? LIMIT 1', (values[0],)).fetchone()
    if contributor_entry:
        cursor.execute('UPDATE CONTRIBUTORS SET lobby_total = ? WHERE contributor_name = ?',
                       (values[2]+contributor_entry[2], values[0]))
    else:
        cursor.execute('INSERT INTO CONTRIBUTORS VALUES (?,0.0,?)', (values[0], values[2]))

    # update LOBBIES table
    for i in xrange(len(values[1])):
        lobby_entry = cursor.execute('SELECT * FROM LOBBIES WHERE contributor_name = ? AND recipient_name = ? LIMIT 1',
                                     (values[0], values[1][i])).fetchone()
        if lobby_entry is None:
            cursor.execute('INSERT INTO LOBBIES VALUES (?,?)', (values[0], values[1][i]))


def get_contributor_names(like):
    conn, cursor = open_conn()
    cursor.execute('SELECT contributor_name FROM CONTRIBUTORS '
                   'WHERE contributor_name LIKE ("%"||?||"%") ORDER BY contributor_name', (like,))
    name_list = cursor.fetchall()
    close_conn(conn, cursor)
    return [entry[0] for entry in name_list]


def get_contributor(name):
    conn, cursor = open_conn()
    cursor.execute('SELECT * FROM CONTRIBUTORS WHERE contributor_name = ?', (name,))
    contributor = cursor.fetchone()
    close_conn(conn, cursor)
    return contributor


def get_contributions(name):
    conn, cursor = open_conn()
    cursor.execute('SELECT recipient_name, contribution_amount FROM CONTRIBUTIONS '
                   'WHERE contributor_name = ? ORDER BY recipient_name', (name,))
    contributions = cursor.fetchall()
    close_conn(conn, cursor)
    return contributions


def get_lobbies(name):
    conn, cursor = open_conn()
    cursor.execute('SELECT recipient_name FROM LOBBIES WHERE contributor_name = ? ORDER BY recipient_name', (name,))
    lobbies = cursor.fetchall()
    close_conn(conn, cursor)
    return lobbies



# conn, cursor = open_conn()
# cursor.execute('SELECT COUNT(*) FROM CONTRIBUTORS')
# print cursor.fetchall()
# cursor.execute('SELECT COUNT(*) FROM CONTRIBUTIONS')
# print cursor.fetchall()
# cursor.execute('SELECT COUNT(*) FROM LOBBIES')
# print cursor.fetchall()
# cursor.execute('SELECT * FROM LOBBIES WHERE contributor_name like "%Dairy Farmers of America%"')
# for each in cursor.fetchall():
#     print each
# get_contributor_names('')
# close_conn(conn, cursor)


