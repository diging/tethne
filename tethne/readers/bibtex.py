import tethne.resources.bib as bb
import tethne.data as ds

def parse_bib(filename):
    """
    Parameters
    ----------
    filename : string
        Path to BibTex file.

    Returns
    -------
    bib_list : list
        A list of :class:`.Paper` instances.

    Notes
    -----
    tethne.resources. bib has been known to make errors in parsing bib files.

    FIXME: structure the bibtex translator in the data_struct folder along with
    the others.
    """

    #load file into bib.py readable format
    data = ""
    with open(filename,'r') as f:
        for line in f:
            line = util.strip_non_ascii(line.rstrip())
            data += line + "\n"

    # Parse the bibtex file into a dict (article) of dicts (article meta)
    #data = bb.clear_comments(data)
    bib = bb.Bibparser(data)
    bib.parse()

    #convert data into a list of tethne Papers
    translator = {'doi':'doi',
                  'author':'aulast',
                  'title':'atitle',
                  'journal':'jtitle',
                  'volume':'volume',
                  'issued':'date'}
    bib_list = []
    for record in bib.records.itervalues():
        meta_dict = ds.Paper()
#        meta_dict['file'] = filename
        for key, value in record.iteritems():
            translator_keys = translator.keys()
            if key in translator_keys:
                meta_key = translator[key]
                meta_dict[meta_key] = value
        bib_list.append(meta_dict)

    #perform the non-simple convertions
    for meta_dict in bib_list:
        if meta_dict['aulast'] is not None:
            aulast = []
            auinit = []
            for name_dict in meta_dict['aulast']:
                aulast.append(name_dict['family'])
                if 'given' in name_dict.keys():
                    auinit.append(name_dict['given'][0].upper())
                else:
                    auinit.append('')
            meta_dict['aulast'] = aulast
            meta_dict['auinit'] = auinit
        else:
            print 'Parser failed at', meta_dict
        meta_dict['ayjid'] = create_ayjid(**meta_dict)

    return bib_list