from tqdm import tqdm
import pandas as pd
import spacy
import ipdb


def extract_from_versions(versions):

    # adds first_version -> last_author_version
    # dels first_version -> last_author_version
    # same first_version -> last_author_version
    # adds last_author_version -> last_version
    # dels last_author_version -> last_version
    # same last_author_version -> last_version


    def get_adds_dels_same(versions, a, b):

        def filter_adds(row):
            return row[a] is None and row[b] is not None

        def filter_dels(row):
            return row[a] is not None and row[b] is None

        def filter_same(row):
            return row[a] is not None and row[b] is not None

        added_chars = versions[versions.apply(filter_adds, axis=1)]
        deleted_chars = versions[versions.apply(filter_dels, axis=1)]
        same_chars = versions[versions.apply(filter_same, axis=1)]


        v_a_chars = versions[a][versions[a].notnull()]
        v_b_chars = versions[b][versions[b].notnull()]

        nlp_a = nlp("".join(v_a_chars))
        nlp_b = nlp("".join(v_b_chars))

        a_token_lookup = [None] * len(v_a_chars)
        b_token_lookup = [None] * len(v_b_chars)

        for token in nlp_a:
            start = token.idx
            end = start+len(token)
            a_token_lookup[start:end] = [token.i]*len(token)

        for token in nlp_b:
            start = token.idx
            end = start+len(token)
            b_token_lookup[start:end] = [token.i]*len(token)

        dels_token = []
        adds_token = []
        same_token = []

        for ichar, char in deleted_chars.iterrows():
            dels_token.append({
                "document": char.document,
                "hand": char[b],
                "token": a_token_lookup[v_a_chars.index.get_loc(ichar)]
            })

        dels_token = pd.DataFrame(dels_token)
        if len(dels_token) > 0:
            dels_token["hand"] = dels_token.hand.apply(
                lambda row: row.replace("#", "") if isinstance(row, unicode) else None
            )
            dels_token = dels_token.drop_duplicates()
            dels_token = dels_token[dels_token.token.notnull()]

        for ichar, char in same_chars.iterrows():
            same_token.append({
                "document": char.document,
                "token": a_token_lookup[v_a_chars.index.get_loc(ichar)]
            })

        same_token = pd.DataFrame(same_token)
        if len(same_token) > 0:
            same_token = same_token.drop_duplicates()
            same_token = same_token[same_token.token.notnull()]

        for ichar, char in added_chars.iterrows():
            adds_token.append({
                "document": char.document,
                "hand": char[b],
                "token": b_token_lookup[v_b_chars.index.get_loc(ichar)]
            })

        adds_token = pd.DataFrame(adds_token)
        if len(adds_token) > 0:
            adds_token = adds_token.drop_duplicates()
            adds_token = adds_token[adds_token.token.notnull()]


        additions = []
        deletions = []
        same = []


        for (document, hand), subdf in dels_token.groupby(["document", "hand"]):

            subdf["grouping"] = [t-i for i,t in enumerate(subdf.token)]

            for (document, hand, _),subsubdf in subdf.groupby(["document", "hand", "grouping"]):
                span = nlp_a[min(subsubdf.token):max(subsubdf.token+1)]
                tmp_doc = nlp(span.text)

                for sentence in tmp_doc.sents:
                    deletions.append({
                        "document": document,
                        "hand": hand,
                        "span_as_doc": nlp(sentence.text)
                    })

        deletions = pd.DataFrame(deletions)


        for document, subdf in same_token.groupby(["document"]):

            subdf["grouping"] = [t-i for i,t in enumerate(subdf.token)]

            for (document, _),subsubdf in subdf.groupby(["document", "grouping"]):

                span = nlp_a[min(subsubdf.token):max(subsubdf.token+1)]
                tmp_doc = nlp(span.text)

                for sentence in tmp_doc.sents:
                    same.append({
                        "document": document,
                        "span_as_doc": nlp(sentence.text)
                    })

        same = pd.DataFrame(same)
        same["hand"] = [None] * len(same)


        for (document, hand), subdf in adds_token.groupby(["document", "hand"]):

            subdf["grouping"] = [t-i for i,t in enumerate(subdf.token)]

            for (document, hand, _),subsubdf in subdf.groupby(["document", "hand", "grouping"]):
                span = nlp_b[min(subsubdf.token):max(subsubdf.token+1)]
                tmp_doc = nlp(span.text)

                for sentence in tmp_doc.sents:
                    additions.append({
                        "document": document,
                        "hand": hand,
                        "span_as_doc": nlp(sentence.text)
                    })

        additions = pd.DataFrame(deletions)

        return additions, deletions, same

    print "load first half"
    (adds_first_version2last_author_version,
     dels_first_version2last_author_version,
     same_first_version2last_author_version) = get_adds_dels_same(versions, "first_version",
                                                                  "last_author_version")
    print "load second half"
    (adds_last_author_version2last_version,
     dels_last_author_version2last_version,
     same_last_author_version2last_version) = get_adds_dels_same(versions, "last_author_version",
                                                                 "last_version")


    result = [
        adds_first_version2last_author_version,
        dels_first_version2last_author_version,
        same_first_version2last_author_version,
        adds_last_author_version2last_version,
        dels_last_author_version2last_version,
        same_last_author_version2last_version
    ]
    for corpus in result:
        if len(corpus) > 0:
            corpus["span_as_doc"] = corpus["span_as_doc"].apply(lambda doc: doc.to_bytes())

    return result
