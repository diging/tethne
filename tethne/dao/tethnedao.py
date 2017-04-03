import warnings

try:
    import mysql.connector
except Exception:
    warnings.warn("Could not import psycopg2. Classes and functions in the tethne.dao module will not be available.", ImportWarning)


class DBConnection:
    """
    DBConnection class creates a connection to the TETHNE database.
    It initializes the cursor which can be used to execute  queries and
    fetch results.
    All methods to fetch data from the TETHNE database can be written in this
    class.

    Raises
    ------
    RuntimeError
        If the mysql Connector package is not present in the user's Project
        structure, RuntimeError will be raised.
    """

    config = {
        'user': 'root',
        'host': 'localhost',
        'database': 'tethne',
    }
    """ The connection details are for a LOCAL database.  """


    def __init__(self):
        try:
            self.conn=mysql.connector.connect(**DBConnection.config)
        except Exception:
            raise RuntimeError("Please ensure the following"
                               "1. DB server is up and running"
                               "2. Connection string details are correct")
        self.cursor = self.conn.cursor()



def getMaxAuthorID():
    """
    Gets maximum value of the primary key from the table "django-tethne_author".
    This is used to calculate the next id for primary key.

    Returns
    -------
    int
        Returns 0 if the table is empty.
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
    Get maximum value of primary key from the table "django-tethne_paper".
    This is used to calculate the next id for primary key.

    Returns
    -------
    int
        Returns 0 if the table is empty.
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
    Get maximum value of the primary key from the table "django-tethne_corpus".
    This is used to calculate the next id for primary key.

    Returns
    -------
    int
        Returns 0 if the table is empty.
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
    Get maximum value of the Primary key from the table
    "django-tethne_author_instance". This is used to calculate the next id for
    primary key.

    Returns
    -------
    int
        Returns 0 if the table is empty.

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
    Get maximum value of the Primary key from the table
    "django-tethne_citation".  This is used to calculate the next id for primary
    key.

    Returns
    -------
    int
        Returns 0 if the table is empty.
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
    Get maximum value of the primary key from the table
    "django-tethne_citation_instance". This is used to calculate the next id for
    primary key.

    Returns
    -------
    int
        Returns 0 if the table is empty.
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
    Get maximum value of the primary key from the table
    "django-tethne_author_instance". This is used to calculate the next id for
    primary key.

    Returns
    -------
    int
        Returns 0 if the table is empty.
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
    Get maximum value of the primary key from the table
    "django-tethne_institution_instance". This is used to calculate the next id
    for primary key.

    Returns
    -------
    int
        Returns 0 if the table is empty.
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
    Get maximum value of the primary key from the table
    "django-tethne_affiliation". This is used to calculate the next id for
    primary key.

    Returns
    -------
    int
        Returns 0 if the table is empty.
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
    Get maximum value of the primary key from the table
    "django-tethne_affiliation_instance". This is used to calculate the next id
    for primary key.

    Returns
    -------
    int
        Returns 0 if the table is empty.
    """
    dbconnectionhanlder = DBConnection()
    dbconnectionhanlder.cursor.execute("SELECT max(id) from `django-tethne_affiliation_instance`")
    rows = dbconnectionhanlder.cursor.fetchall()
    dbconnectionhanlder.conn.close()
    if rows[0][0] is None:
        return 0
    else:
        return rows[0][0]
