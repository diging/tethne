"""
Copyright (C) 2011 by Panagiotis Tigkas <ptigas@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import fileinput
import re
import json
from pprint import pprint

def clear_comments(data):
    """Return the bibtex content without comments"""
    res = re.sub(r"(%.*\n)", '', data)
    res = re.sub(r"(comment [^\n]*\n)", '', res)
    return res

def log( f ):
    return f

class Bibparser() :
    """Main class for Bibtex parsing"""

    def tokenize(self) :
        """Returns a token iterator"""
        for item in self.token_re.finditer(self.data):
            i = item.group(0)
            if self.white.match(i) :
                if self.nl.match(i) :
                    self.line += 1
                continue
            else :
                yield i

    def __init__(self, data) :
        self.data = data
        self.token = None
        self.token_type = None
        self._next_token = self.tokenize().next
        self.hashtable = {}
        self.mode = None
        self.records = {}
        self.line = 1

        # compile some regexes
        self.white = re.compile(r"[\n|\s]+")
        self.nl = re.compile(r"[\n]")
        self.token_re = re.compile(r"([^\s\"#%'(){}@,=]+|\n|@|\"|{|}|=|,)")

    def parse(self) :
        """Parses self.data and stores the parsed bibtex to self.rec"""
        while True :
            try :
                self.next_token()
                while self.database() :
                    pass
            except StopIteration :
                break

    def next_token(self):
        """Returns next token"""
        self.token = self._next_token()
        #print self.line, self.token

    @log
    def database(self) :
        """Database"""
        if self.token == '@' :
            self.next_token()
            self.entry()

    @log
    def entry(self) :
        """Entry"""
        if self.token.lower() == 'string' :
            self.mode = 'string'
            self.string()
            self.mode = None
        else :
            self.mode = 'record'
            self.record()
            self.mode = None

    @log
    def string(self) :
        """String"""
        if self.token.lower() == "string" :
            self.next_token()
            if self.token == "{" :
                self.next_token()
                self.field()
                if self.token == "}" :
                    pass
                else :
                    raise NameError("} missing")

    @log
    def field(self) :
        """Field"""
        name = self.name()
        if self.token == '=' :
            self.next_token()
            value = self.value()
            if self.mode == 'string' :
                self.hashtable[name] = value
            return (name, value)

    @log
    def value(self) :
        """Value"""
        value = ""
        val = []

        while True :
            if self.token == '"' :
                while True:
                    self.next_token()
                    if self.token == '"' :
                        break
                    else :
                        val.append(self.token)
                if self.token == '"' :
                    self.next_token()
                else :
                    raise NameError("\" missing")
            elif self.token == '{' :
                brac_counter = 0
                while True:
                    self.next_token()
                    if self.token == '{' :
                        brac_counter += 1
                    if self.token == '}' :
                        brac_counter -= 1
                    if brac_counter < 0 :
                        break
                    else :
                        val.append(self.token)
                if self.token == '}' :
                    self.next_token()
                else :
                    raise NameError("} missing")
            elif self.token != "=" and re.match(r"\w|#|,", self.token) :
                value = self.query_hashtable(self.token)
                val.append(value)
                while True:
                    self.next_token()
                    # if token is in hashtable then replace
                    value = self.query_hashtable(self.token)
                    if re.match(r"[^\w#]|,|}|{", self.token) : #self.token == '' :
                        break
                    else :
                        val.append(value)

            elif self.token.isdigit() :
                value = self.token
                self.next_token()
            else :
                if self.token in self.hashtable :
                    value = self.hashtable[ self.token ]
                else :
                    value = self.token
                self.next_token()

            if re.match(r"}|,",self.token ) :
                break

        value = ' '.join(val)
        return value

    def query_hashtable( self, s ) :
        if s in self.hashtable :
            return self.hashtable[ self.token ]
        else :
            return s

    @log
    def name(self) :
        """Returns parsed Name"""
        name = self.token
        self.next_token()
        return name

    @log
    def key(self) :
        """Returns parsed Key"""
        key = self.token
        self.next_token()
        return key

    @log
    def record(self) :
        """Record"""
        if self.token not in ['comment', 'string', 'preamble'] :
            record_type = self.token
            self.next_token()
            if self.token == '{' :
                self.next_token()
                key = self.key()
                self.records[ key ] = {}
                self.records[ key ]['type'] = record_type
                self.records[ key ]['id'] = key
                if self.token == ',' :
                    while True:
                        self.next_token()
                        field = self.field()
                        if field :
                            k = field[0]
                            val = field[1]

                            if k == 'author' :
                                val = self.parse_authors(val)

                            if k == 'year' :
                                val = int(val)
                                k = 'issued'

                            if k == 'pages' :
                                val = val.replace('--', '-')
                                k = 'page'

                            if k == 'title' :
                                #   Preserve capitalization, as described in http://tex.stackexchange.com/questions/7288/preserving-capitalization-in-bibtex-titles
                                #   This will likely choke on nested curly-brackets, but that doesn't seem like an ordinary practice.
                                def capitalize(s):
                                    return s.group(1) + s.group(2).upper()
                                while val.find('{') > -1:
                                    caps = (val.find('{'), val.find('}'))
                                    val = val.replace(val[caps[0]:caps[1]+1], re.sub("(^|\s)(\S)", capitalize, val[caps[0]+1:caps[1]]).strip())

                            self.records[ key ][k] = val
                        if self.token != ',' :
                            break
                    if self.token == '}' :
                        pass
                    else :
                        # assume entity ended
                        if self.token == '@' :
                            pass
                        else :
                            raise NameError("@ missing")

    def parse_authors( self, authors ) :
        res = []
        authors = authors.split('and')
        for author in authors :
            _author = author.split(',')
            family = _author[0]
            family = family.replace("\\\\ { o }","o")
            family = family.replace("\\\\ { e }","e")
            family = family.replace("\\\\ { \\\\i } ", "i")
            family = family.replace("{","").replace("}","").replace("\\", "")
            family = family.replace('"','')
            family = family.replace('  ', '')
            family = family.strip().rstrip()

            rec = {'family':family}
            try :
                given = _author[1].strip().rstrip()
                rec['given'] = given
            except IndexError:
                pass
            res.append( rec )
        return res

    def json(self) :
        """Returns json formated records"""
        return json.dumps({'items':self.records.values()})

def post_request( j ) :
    import urllib
    import urllib2
    import json
    url = 'http://127.0.0.1:8085/\?bibliography\=1\&citations\=1\&linkwrap\=1\&responseformat\=json\&showoutput\=1'
    values = j
    req = urllib2.Request(url, values)
    response = urllib2.urlopen(req)
    the_page = response.read()
    data=json.loads(the_page)

    for i in xrange(len(data['bibliography'][1])) :
        print data['bibliography'][0]['entry_ids'][i]
        print data['bibliography'][1][i]
        print

def main() :
    """Main function"""

#    # TODO: Probably a solution with iterations will be better
#    data = ""
#    for line in fileinput.input():
#        line = line.rstrip()
#        data += line + "\n"
#
#    print 'loaded...'
#    data = clear_comments(data)
#    print 'cleared...'
#    bib = Bibparser(data)
#    bib.parse()
#    data = bib.json()
#    #post_request( data )
#    #print data
#    print type(bib.records)
#    for key, value in bib.records.iteritems():
#        print key
#        for key1, value1 in value.iteritems():
#            print key1, type(value1)
#    print 'done...'

    datapath = "/Users/erickpeirson/Downloads/EvoMed_Authors_v2.bib"
    data = ""
    with open(datapath,'r') as f:
        for line in f:
            line = line.rstrip()
            data += line + "\n"

    #data = clear_comments(data)
    bib = Bibparser(data)
    bib.parse()

if __name__ == "__main__" :
    main()
