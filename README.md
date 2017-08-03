# Example usage of the parser

    import spacy

    import berliner_intellektuelle_preprocessing as bip

    data_dir = 'SOME/DIR'
    spec = {
        'tei': 'http://www.tei-c.org/ns/1.0'
    }

    nlp = spacy.load("de")


    parser = bip.parse_xml.Parser()

    corpus = parser.parse_corpus(data_dir, spec)

    versions = bip.extract_versions.extract_versions_from_corpus(nlp, corpus)
