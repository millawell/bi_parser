#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os import listdir, path
from lxml import etree
import ntpath

import numpy as np
import uuid
import difflib
import pandas as pd
from tqdm import tqdm
import ipdb
import re
import random

# own imports
from base import tei, Document, Group, Corpus, UniqeEtreeEl

bi_team_responsible = ["#???", "#anna.busch", "#anna_busch", "#anne.baillot", "#anne.baillot",
                       "#johanna.preusse", "#beatrice.haeusler", "#beschka.gloy", "#cecile.lambert",
                       "#eva.schneider", "#henrike.bobzien", "#janin.afken", "#janine.katins",
                       "#johanna.preusse", "#julia.theus", "#lena.ebert", "#nina.breher",
                       "#patricia.fritsch", "#sabine.seifert", "#sarah.helena.neuhaus",
                       "#selma.jahnke", "#sophia-zeil", "#sophia.zeik", "#sophia.zeil",
                       "#stefanie.hasler", "#stefanie_hasler", "anna-lisa.menck",
                       "anne.baillot", "beschka.gloy", "emmanuelle.chaze", "janine.katins",
                       "lena.ebert", "sabine.seifert", "selma.jahnke", "sophia.zeil",
                       "stefanie.hasler"]


class Parser(object):


    def parse_file(self, file_, spec):

        def __init_body(tree):
            xpath = '//tei:text/tei:body'

            elems = tree.xpath(xpath, namespaces=spec)

            if len(elems) == 1:
                return elems[0]
            else:
                raise(ValueError("xpath of this etree ambiguous."))

        tree = etree.parse(file_, parser=etree.XMLParser(remove_comments=True, remove_blank_text=True))

        # double parse to remove white spaces
        # removes some whitespaces
        xml_str = etree.tostring(tree)

        # removes line breaks
        xml_str = re.sub(r'\n\s+', ' ', xml_str)

        tree = etree.fromstring(xml_str)

        xmltree = __init_body(tree)

        ommitted_tags = [tei("fw"), tei("abbr"), tei("stamp")]

        d = Document(ntpath.basename(file_.name))

        def __handle_line_breaks(element, parents):
            # handle line break
            if element.tag == tei("p"):
                if "rend" in element.attrib and element.attrib["rend"] == "nolb":
                    # paragraph with no line break
                    pass
                else:
                    # lb with new word: insert space
                    __add_content_to_doc(" ", parents)

            if element.tag == tei("lb"):
                if "break" in element.attrib:
                    if element.attrib["break"].lower() in ["no", "none"]:
                        # lb with same word: insert nothing
                        pass
                    else:
                        ipdb.set_trace()
                else:
                    # lb with new word: insert space
                    __add_content_to_doc(" ", parents)

            if element.tag == tei("pb"):
                # page break
                __add_content_to_doc(" ", parents)

            if element.tag == tei("space"):
                __add_content_to_doc(" ", parents)

        def __add_content_to_doc(content, parents):

            begin = len(d.content)
            d.content += content
            end = len(d.content)

            adds_dels = filter(lambda p: p.el.tag == tei("add") or p.el.tag == tei("del") or p.el.tag == tei("note"), parents)

            max_sequence = 0
            for ad in adds_dels:
                if "seq" in ad.el.attrib:
                    max_sequence = max(int(ad.el.attrib["seq"]), max_sequence)


            for default_priority, parent in enumerate(parents):

                # there are special cases where the prio is not determined by the nesting.
                # this is denoted by the attribte `seq`
                if "seq" in parent.el.attrib:
                    if parent.el.attrib["seq"] == "0":
                        priority = np.inf
                    else:
                        priority = max_sequence - int(parent.el.attrib["seq"])
                else:
                    priority = default_priority

                hand = None
                if "hand" in parent.el.attrib:
                    hand = parent.el.attrib["hand"]

                ref = None
                if "ref" in parent.el.attrib:
                    ref = parent.el.attrib["ref"]

                d.upsert_group(
                    parent.el.tag,
                    parent.uuid,
                    begin,
                    end,
                    priority,
                    hand,
                    ref
                )

        def __traverse_and_parse(el, parents=list()):
            u_elem = UniqeEtreeEl(el)

            __handle_line_breaks(el, parents)

            parents += [u_elem]

            # add inner
            if (u_elem.el.tag == tei("note")
                    and "resp" in u_elem.el.attrib
                    and len(
                        filter(
                            lambda team_hash: u_elem.el.attrib["resp"] == team_hash,
                            bi_team_responsible
                        )
                    ) > 0):
                # omit notes by the BI team
                pass

            elif not u_elem.el.tag in ommitted_tags:
                if u_elem.el.text is not None:
                    __add_content_to_doc(u_elem.el.text, parents)

                for gen in u_elem.el:
                    __traverse_and_parse(gen, parents)


            del parents[parents.index(u_elem)]

            # add tail
            if u_elem.el.tail is not None:
                __add_content_to_doc(u_elem.el.tail, parents)



        __traverse_and_parse(xmltree)
        return d

    def parse_corpus(self, data_dir, spec, DEBUG):

        # PARSE BRACKET DELETES

        def get_del_bracket(doc, pos, bracket):

            adds_notes_at_pos = sorted(
                filter(
                    lambda ad: ad.begin <= pos and ad.end > pos and ad.name in [tei("add"), tei("note")],
                    doc.groups
                ),
                key=lambda x: x.priority
            )

            if len(adds_notes_at_pos) > 0:
                return doc.content[pos] == bracket, adds_notes_at_pos[0]

            return False, None

        def parse_brackets(doc, bracket_open, bracket_close):
            """Generate parenthesized contents in string as pairs (level, contents)."""
            stack = []
            for i, c in enumerate(doc.content):
                is_del_bracket_open, add = get_del_bracket(doc, i, bracket_open)
                is_del_bracket_close, _ = get_del_bracket(doc, i, bracket_close)
                if is_del_bracket_open:
                    stack.append((i, add.hand))
                elif is_del_bracket_close and stack:
                    start, hand = stack.pop()
                    yield start+1, i, hand


        filenames = [filename for filename in listdir(data_dir) if filename[-3:] == 'xml']

        if DEBUG and len(filenames) > 5:
            filenames = random.sample(filenames, 5)

        c = Corpus()
        print "parse"
        for fin in tqdm(filenames):
            c.documents.append(
                self.parse_file(
                    open(
                        path.join(
                            data_dir,
                            fin
                        )
                    ),
                    spec
                )
            )


        ## BRACKET DELETIONS
        for doc in tqdm(c.documents):
            for start, end, hand in parse_brackets(doc, "[", "]"):
                if (end) - (start) > 0:
                    doc.upsert_group(
                        tei("del"),
                        str(uuid.uuid4()),
                        start,
                        end,
                        priority=0,
                        hand=hand
                    )
            for start, end, hand in parse_brackets(doc, "(", ")"):
                if (end) - (start) > 0:

                    doc.upsert_group(
                        tei("del"),
                        str(uuid.uuid4()),
                        start,
                        end,
                        priority=0,
                        hand=hand
                    )


        return c
