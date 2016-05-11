try:
    import psycopg2
except Exception:
    raise RuntimeError("Import error while importing package psycopg2"
                       "Please ensure that the package psycopg2 is correctly installed")


class DBConnection:
    """
    DBConnection class creates a connection to the TETHNE database.
    It initializes the cursor which can be used to execute  queries and
    fetch results.
    All methods to fetch data from the TETHNE database can be written in this class.

    AS-IS ->
    The connection details are for a LOCAL database.

    TO-DO ->
    To make the connection-string details configurable in a properties file.
    The user should only update the properties file to reflect the DB he wants to connect to

        OR

    We can keep one central DB and the connection details can be fixed.
    ElephantSQL is an option.
    It gives an option for free DB hosting and data limit upto 20 MB.
    It also gives an option to take backups.
    So migrating to any other Postgres DB will be very easy.


    """
    def __init__(self):
        """
        Initializes the connection string details
        And creates a connection to the Tethne DB.

        It initializes the cursor which can be used to execute  queries and
        fetch results.

        Returns
        -------


        EXCEPTIONS ->
        if the psycopg2 package is not present in the user's Project structure, RuntimeError
        will be raised.

        """
        self.dbname = 'tethne'
        self.user = 'tethneuser'
        self.password ='password'
        self.host='localhost'
        try:
            self.conn=psycopg2.connect(database=self.dbname,
                                     user=self.user,
                                     host=self.host,
                                     password=self.password)
        except Exception:
            raise RuntimeError("Please ensure the following"
                               "1. DB server is up and running"
                               "2. Connection string details are correct")
        self.cursor = self.conn.cursor()



def getMaxAuthorID():
    """

    Returns
    -------
    maximum value of the Primary key from the table "django-tethne_author"
    This is used to calculate the next id for primary key.

    if the table is empty, 0 is returned

    """
    dbconnectionhanlder = DBConnection()
    dbconnectionhanlder.cursor.execute(""" SELECT max(id) from "django-tethne_author" """ )
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]


def getMaxPaperID():
    """

    Returns
    -------

    maximum value of Primary key from the table "django-tethne_paper".
    This is used to calculate the next id for primary key.

    if the table is empty, 0 is returned

    """
    dbconnectionhanlder = DBConnection()
    dbconnectionhanlder.cursor.execute(""" SELECT max(id) from "django-tethne_paper" """ )
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]

def getMaxCorpusID():
    """

    Returns
    -------
    maximum value of the Primary key from the table "django-tethne_corpus"
    This is used to calculate the next id for primary key.

    if the table is empty, 0 is returned

    """
    dbconnectionhanlder = DBConnection()
    dbconnectionhanlder.cursor.execute(""" SELECT max(id) from "django-tethne_corpus" """ )
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]

def getMaxAuthorInstanceID():
    """

    Returns
    -------
    maximum value of the Primary key from the table "django-tethne_author_instance"
    This is used to calculate the next id for primary key.

    if the table is empty, 0 is returned

    """
    dbconnectionhanlder = DBConnection()
    dbconnectionhanlder.cursor.execute(""" SELECT max(id) from "django-tethne_author_instance" """ )
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]






