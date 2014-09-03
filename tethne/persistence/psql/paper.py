import logging
logging.basicConfig(filename=None, format='%(asctime)-6s: %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

import psycopg2
import uuid
import re
from ...classes import Paper

PAPER_TABLE = """CREATE TABLE {0} (
                    id              serial      PRIMARY KEY,
                    aulast          text[],
                    auinit          text[],
                    auuri           text[],
                    atitle          text,
                    jtitle          text,
                    volume          text,
                    issue           text,
                    spage           text,
                    epage           text,
                    date            integer,
                    ayjid           text,
                    uri             text        UNIQUE,
                    doi             text        UNIQUE,
                    pmid            text        UNIQUE,
                    wosid           text        UNIQUE,
                    eid             text        UNIQUE,
                    abstract        text,
                    contents        text,
                    topics          text,
                    accession       text,
                    citations       integer[]
                );"""

class SQLPapers(list):
    """
    Container for :class:`.Paper` instances that behaves like a list, but
    uses a PostgresSQL backend. 
    
    The objective is to store and retrieve :class:`.Paper`\s without holding
    in main memory.
    
    Parameters
    ----------
    dbarams : dict
        Database connection parameters. See `libpq parameters 
        <http://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-PARAMKEYWORDS>`_.
    table : str
        Name of an existing table containing Papers. There should also be a
        corresponding table called ``[table]_citations``.

    """

    insert_pattern = """INSERT INTO {0} ({1}) VALUES ({2}) RETURNING id;"""

    def __init__(self, dbparams, table=None):
        self.dbparams = dbparams
        conn = self.__connect__()
        cur = conn.cursor()

        if table is None:
            # Create main table for Papers in the dataset.
            self.name = 'tethne_papers_' + str(uuid.uuid4()).replace('-', '_')
            logger.debug(
                'No table specified, creating Paper table with name {0}'
                .format(self.name)   )

            cur.execute(PAPER_TABLE.format(self.name))
            conn.commit()
            logger.debug(
                'Successfully created {0}'.format(self.name)    )

            # Create a secondary table for cited references (also Papers).
            logger.debug('Creating a citations table.')
            cur.execute(PAPER_TABLE.format(self.name + '_citations'))
            conn.commit()

        else:
            self.name = table

        # Get the names of all of the columns in the table. This allows us to
        #  change the structure of the Papers table down the road without
        #  rewriting code here.
        cur.execute("""SELECT * FROM information_schema.columns
                                WHERE table_name = %s;""", (self.name,))
        self.cols = [ col[3] for col in cur ]   # col[3] is the column name.

        cur.close()
        conn.close()

    def __connect__(self):

        dbargs = ' '.join(
                ['{0}={1}'.format(k,v) for k,v in self.dbparams.iteritems()]
                )
        conn = psycopg2.connect(dbargs)
        return conn

    def __getitem__(self, key):
        # Key is just a list index, which points to an id from the Papers table.
        id = list.__getitem__(self, key)
        return self.__get_by_id(id)

    def __get_by_id(self, id):
        paper = Paper()

        conn = self.__connect__()
        cur = conn.cursor()

        # Search the table for id.
        arg = """SELECT * FROM {0} WHERE id = %s;""".format(self.name)
        cur.execute(arg, (id,))     # This won't fail, even if no match.
        try:    # If there is no corresponding record, raise an error.
            data = cur.fetchone()
        except psycopg2.ProgrammingError:   # No matching record found!
            logger.debug('No Paper with id {0}'.format(id))
            raise KeyError('No Paper with that ID exists.')

        # Populate the Paper with values.
        for i in xrange(len(data)):
            key = self.cols[i]
            value = data[i]
            if key == 'citations' and value is not None:
                # value is a list of ids into the citations table, and what
                #  we want is a list of Papers. Since the citations table has
                #  the same structure as the Papers table, we can access it
                #  as a SQLPapers instance.
                citations = SQLPapers(  self.dbparams,
                                        table=self.name + '_citations'  )
                value = [ citations.__get_by_id(k) for k in value ]
            try:
                paper[key] = value
            except: # Ignore any fields from the table that don't have a
                    #  corresponding field in the Paper instance. This should
                    #  effectively just ignore the 'id' field.
                pass

        cur.close()
        conn.close()

        return paper    # A Paper instance.

    def __iadd__(self, other):
        """In-place addition should be equivalent to :meth:`.append`\."""

        if type(other) is Paper:
            self.append(other)  # Just pass through to .append()
        return self

    def append(self, obj):
        """
        Adds a new row to the table.
        """
        conn = self.__connect__()
        cur = conn.cursor()

        # Handle citations first. Each citation is stored in a citations table
        #  with precisel the same structure as the main table for Papers. That
        #  means that we can represent citations using SQLPapers later on.
        citations = obj['citations']
        cit_ids = []    # IDs from citations table.
        for citation in citations:
            vals = { k:v for k,v in citation.iteritems()
                        if k not in ['citations', 'institutions', 'country' ] }
            keys = ', '.join(vals.keys())
            vkeys = ', '.join( [ '%({0})s'.format(k) for k in vals.keys() ])
            arg = self.insert_pattern.format(
                                        self.name + '_citations', keys, vkeys  )

            try:    # Insert the citation into the citation table.
                cur.execute(arg, vals)
                id = cur.fetchone()[0]

            # This will frequently hit duplicates, which raises IntegrityError.
            except psycopg2.IntegrityError as E:
                conn.commit()   # Clear the error.

                # Search error message for the conflicting key.
                error = str(E)
                try:    # If this fails to match, then something else happened.
                    ckey = re.search('Key \((.*?)\)', error).group(1)
                except:
                    continue    # ...in that case, just ignore this citation.

                # Get the id of the existing citation.
                cname = self.name + '_citations'    # Name of citation table.
                arg = """SELECT id FROM {0} WHERE {1} = %s;""".format(  cname,
                                                                        ckey   )
                cval = vals[ckey]
                cur.execute(arg, (cval,))
                id = cur.fetchone()[0]  # Got it!

            cit_ids.append(id)  # This gets stored as a list of integers, below.

        # Then handle then Paper itself.
        vals = { k:v for k,v in obj.iteritems()
                    if k not in ['citations', 'institutions', 'country' ]   }
        vals['citations'] = cit_ids     # Store the list of citation ids, too.
        keys = ', '.join(vals.keys())
        vkeys = ', '.join( [ '%({0})s'.format(k) for k in vals.keys() ])

        arg = self.insert_pattern.format(self.name, keys, vkeys)

        try:
            cur.execute(arg, vals)
        except psycopg2.IntegrityError as E:    # Handle violations of UNIQUE
                                                #  constraint.
            raise ValueError('Paper already exists: {0}'.format(E))

        id = cur.fetchone()[0]
        list.append(self, id)   # Instead of a list of Papers, we have a list of
                                #  ids into the paper table. We can use these
                                #  to retrieve Papers later.

        conn.commit()
        cur.close()
        conn.close()