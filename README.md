# ibiparser
parsing the TEI files from berliner-intellektuelle.eu

# installation for developers
* clone repository
* `cd` to repository
* `python setup.py develop`

# usage
    import ibiparser
    data_dir = '/Users/davidlassner/promotion/data/ibi/manuscripts'
    spec = {
        'tei': 'http://www.tei-c.org/ns/1.0'
    }
    df = ibiparser.parse_corpus(data_dir, spec)
