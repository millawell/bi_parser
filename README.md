# bi_parser
parsing the TEI files from berliner-intellektuelle.eu

# installation for developers
* clone repository
* `cd` to repository
* `python setup.py develop`

# usage
    import bi_parser
    data_dir = 'PATH/TO/THE/MANUSCRIPTS'
    spec = {
        'tei': 'http://www.tei-c.org/ns/1.0'
    }
    df = bi_parser.parse_corpus(data_dir, spec)
