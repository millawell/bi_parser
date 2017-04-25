#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import listdir, path
from lxml import etree
import pandas as pd


def parse_file(file_, spec):

    def __init_body(tree):
        xpath = '//tei:text/tei:body'

        elems = tree.xpath(xpath, namespaces=spec)
        if len(elems) == 1:
            return elems[0]
        else:
            raise(ValueError("xpath of this etree ambiguous."))

    def __traverse(elem, parents=list()):
        yield (parents, elem)

        parents += [elem]

        for gen in elem:
            for child in __traverse(gen, parents):
                yield child

        del parents[parents.index(elem)]

    input_string = file_.read()

    tree = etree.fromstring(input_string)

    xmltree = __init_body(tree)

    content_slices_and_their_parents = []
    for parents, element in __traverse(xmltree):

        inner, tail = element.text, element.tail
        content_slices_and_their_parents.append({
            "content": inner if inner is not None else "",
            "parents": parents+[element],
            "filename": file_.name
        })

        content_slices_and_their_parents.append({
            "content": tail if tail is not None else "",
            "parents": parents,
            "filename": file_.name
        })

    return content_slices_and_their_parents


def parse_corpus(data_dir, spec):

    filenames = [filename for filename in listdir(data_dir) if filename[-3:] == 'xml']

    df = []
    for fin in filenames:
        df = df + parse_file(
            open(path.join(
                data_dir,
                fin)
            ),
            spec
        )

    return pd.DataFrame(df)
