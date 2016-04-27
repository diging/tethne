import psycopg2


class DBConnection:
    def __init__(self):
        self.dbname = 'tethne'
        self.user = 'tethneuser'
        self.password ='password'
        self.host='localhost'
        self.conn=psycopg2.connect(database=self.dbname,
                                     user=self.user,
                                     host=self.host,
                                     password=self.password)
        self.cursor = self.conn.cursor()



def getMaxAuthorID():
    dbconnectionhanlder = DBConnection()
    dbconnectionhanlder.cursor.execute(""" SELECT max(id) from "django-tethne_author" """ )
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]


def getMaxPaperID():
    dbconnectionhanlder = DBConnection()
    dbconnectionhanlder.cursor.execute(""" SELECT max(id) from "django-tethne_paper" """ )
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]

def getMaxCorpusID():
    dbconnectionhanlder = DBConnection()
    dbconnectionhanlder.cursor.execute(""" SELECT max(id) from "django-tethne_corpus" """ )
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]

def getMaxAuthorInstanceID():
    dbconnectionhanlder = DBConnection()
    dbconnectionhanlder.cursor.execute(""" SELECT max(id) from "django-tethne_author_instance" """ )
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]






