from tqdm import tqdm
import cPickle as pickle
import random
import pandas as pd
import ipdb
import spacy


# own imports
from base import tei, Document, Group, Corpus, UniqeEtreeEl


def get_three_versions_of_doc(document):
    # * original version: no changes at all
    # * last version of the original author
    # * modifications made by different hand

    content = document.content
    mod_tags = [tei("add"), tei("del"), tei("note")]

    mods = filter(lambda g: g.name in mod_tags, document.groups)

    first_version = []
    last_author_version = []
    last_version = []
    last_version_hand = []
    pers_names = []

    for pos in range(len(content)):

        pers_tags_at_pos = filter(
            lambda g: g.name == tei("persName") and g.begin <= pos and g.end > pos,
            document.groups
        )

        if len(pers_tags_at_pos) > 0:
            pers_name = pers_tags_at_pos[0]
            if pers_name.ref is not None:
                pers_names.append(pers_name.ref)
            else:
                pers_names.append(None)
        else:
            pers_names.append(None)

        c_char = document.content[pos]
        c_last_version_hand = None

        mods_at_pos = sorted(
            filter(
                lambda ad: ad.begin <= pos and ad.end > pos,
                mods
            ),
            key=lambda x: x.priority
        )

        if len(mods_at_pos) == 0:
            c_first_version = c_char
            c_last_author_version = c_char
            c_last_version = c_char

        else:
            # get most recent mod type for each version
            first_mod_at_pos = mods_at_pos[-1]
            last_mod_at_pos = mods_at_pos[0]

            last_mod_before_other_hand = None
            for last_mod_before_other_hand in mods_at_pos:
                if last_mod_before_other_hand.hand is None:
                    break

            if last_mod_before_other_hand.hand is not None:
                last_mod_before_other_hand = None

            if first_mod_at_pos.name == tei("del"):
                c_first_version = c_char
            else:
                c_first_version = None

            if last_mod_before_other_hand is not None:
                if last_mod_before_other_hand.name != tei("del"):
                    c_last_author_version = c_char
                else:
                    c_last_author_version = None
            else:
                c_last_author_version = c_first_version

            if last_mod_at_pos.name == tei("del"):
                c_last_version = None
            else:
                c_last_version = c_char

            c_last_version_hand = last_mod_at_pos.hand

        first_version.append(c_first_version)
        last_author_version.append(c_last_author_version)
        last_version.append(c_last_version)
        last_version_hand.append(c_last_version_hand)

    return first_version, last_author_version, last_version, last_version_hand, pers_names


def extract_versions_from_corpus(nlp, corpus, DEBUG=False):

    if DEBUG and len(corpus.documents) > 40:
        documents = random.sample(corpus.documents, 40)
    else:
        documents = corpus.documents

    characters_first_version = []
    characters_last_author_version = []
    characters_last_version = []
    document_names = []
    last_version_hands = []
    pers_names = []

    for doc in tqdm(documents):
        (first_version,
         last_author_version,
         last_version,
         last_version_hand,
         c_pers_names) = get_three_versions_of_doc(doc)

        characters_first_version += first_version
        characters_last_author_version += last_author_version
        characters_last_version += last_version
        document_names += [doc.file_name] * len(first_version)
        last_version_hand += last_version_hand
        pers_names += c_pers_names

    nlp_first_version = nlp("".join(filter(lambda x: x is not None, characters_first_version)))
    nlp_last_author_version = nlp("".join(filter(lambda x: x is not None, characters_last_author_version)))
    nlp_last_version = nlp("".join(filter(lambda x: x is not None, characters_last_version)))

    def fill_lookup(nlp_obj, chars, index):
        lookup = [None] * len(chars)
        for token in nlp_obj:
            start = index[token.idx]
            end = start+len(token)
            lookup[start:end] = [token.i]*len(token)
        return lookup

    total_index_to_first_version_index = []
    total_index_to_last_version_index = []
    total_index_to_last_author_version_index = []

    for i in range(len(characters_first_version)):
        if characters_first_version[i] is not None:
            total_index_to_first_version_index.append(i)
        if characters_last_author_version[i] is not None:
            total_index_to_last_author_version_index.append(i)
        if characters_last_version[i] is not None:
            total_index_to_last_version_index.append(i)

    token_lookup_first_version = fill_lookup(nlp_first_version, characters_first_version, total_index_to_first_version_index)
    token_lookup_last_author_version = fill_lookup(nlp_last_author_version, characters_last_author_version, total_index_to_last_author_version_index)
    token_lookup_last_version = fill_lookup(nlp_last_version, characters_last_version, total_index_to_last_version_index)

    result = {
        "characters_first_version": characters_first_version,
        "nlp_first_version": nlp_first_version.to_bytes(),
        "token_lookup_first_version": token_lookup_first_version,

        "characters_last_author_version": characters_last_author_version,
        "nlp_last_author_version": nlp_last_author_version.to_bytes(),
        "token_lookup_last_author_version": token_lookup_last_author_version,

        "characters_last_version": characters_last_version,
        "nlp_last_version": nlp_last_version.to_bytes(),
        "token_lookup_last_version": token_lookup_last_version,

        "document_names": document_names,
        "last_version_hands": last_version_hands
    }
    return result
