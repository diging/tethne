try:
    import mysql.connector
except Exception:
    raise RuntimeError("mysql.connector for Python not found. Please install the same")


class DBConnection:
    """
    DBConnection class creates a connection to the TETHNE database.
    It initializes the cursor which can be used to execute  queries and
    fetch results.
    All methods to fetch data from the TETHNE database can be written in this class.

    AS-IS ->
    The connection details are for a LOCAL database.


    """
    config = {
        'user': 'root',
        'host': 'localhost',
        'database': 'tethne',
    }

    def __init__(self):
        """
        Initializes the connection string details
        And creates a connection to the Tethne DB.

        It initializes the cursor which can be used to execute  queries and
        fetch results.

        Returns
        -------


        EXCEPTIONS ->
        if the mysql Connector package is not present in the user's Project structure, RuntimeError
        will be raised.

        """
        try:
            self.conn=mysql.connector.connect(**DBConnection.config)
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
    dbconnectionhanlder.cursor.execute(" SELECT max(id) from `django-tethne_author` ")
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
    dbconnectionhanlder.cursor.execute("SELECT max(id) from `django-tethne_paper` ")
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
    dbconnectionhanlder.cursor.execute(" SELECT max(id) from `django-tethne_corpus` ")
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
    dbconnectionhanlder.cursor.execute("SELECT max(id) from `django-tethne_author_instance`")
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]


def getMaxCitationID():
    """

    Returns
    -------
    maximum value of the Primary key from the table "django-tethne_citation"
    This is used to calculate the next id for primary key.

    if the table is empty, 0 is returned

    """
    dbconnectionhanlder = DBConnection()
    dbconnectionhanlder.cursor.execute("SELECT max(id) from `django-tethne_citation`")
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]

def getMaxCitationInstanceID():
    """

    Returns
    -------
    maximum value of the Primary key from the table "django-tethne_citation_instance"
    This is used to calculate the next id for primary key.

    if the table is empty, 0 is returned

    """
    dbconnectionhanlder = DBConnection()
    dbconnectionhanlder.cursor.execute("SELECT max(id) from `django-tethne_citation_instance`")
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]


def getMaxInstitutionID():
    """

    Returns
    -------
    maximum value of the Primary key from the table "django-tethne_author_instance"
    This is used to calculate the next id for primary key.

    if the table is empty, 0 is returned

    """
    dbconnectionhanlder = DBConnection()
    dbconnectionhanlder.cursor.execute("SELECT max(id) from `django-tethne_institution`")
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]


def getMaxInstitutionInstanceID():
    """

    Returns
    -------
    maximum value of the Primary key from the table "django-tethne_institution_instance"
    This is used to calculate the next id for primary key.

    if the table is empty, 0 is returned

    """
    dbconnectionhanlder = DBConnection()
    dbconnectionhanlder.cursor.execute("SELECT max(id) from `django-tethne_institution_instance`")
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]


def getMaxAffiliationID():
    """

    Returns
    -------
    maximum value of the Primary key from the table "django-tethne_affiliation"
    This is used to calculate the next id for primary key.

    if the table is empty, 0 is returned

    """
    dbconnectionhanlder = DBConnection()
    dbconnectionhanlder.cursor.execute("SELECT max(id) from `django-tethne_affiliation`")
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]



def getMaxAffiliationInstanceID():
    """

    Returns
    -------
    maximum value of the Primary key from the table "django-tethne_affiliation_instance"
    This is used to calculate the next id for primary key.

    if the table is empty, 0 is returned

    """
    dbconnectionhanlder = DBConnection()
    dbconnectionhanlder.cursor.execute("SELECT max(id) from `django-tethne_affiliation_instance`")
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]









