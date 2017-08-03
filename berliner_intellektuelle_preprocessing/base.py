import uuid
import numpy as np

def tei(tagname):
    return "{{http://www.tei-c.org/ns/1.0}}{}".format(tagname)


class Document(object):

    file_name = None
    content = None
    groups = None

    def __init__(self, file_name):
        self.file_name = file_name
        self.content = ""
        self.groups = []


    def upsert_group(self, name, uuid, begin, end, priority, hand, ref=None):
        group = filter(lambda g: g.uuid == uuid, self.groups)

        if len(group) > 0:
            group = group[0]

            group.begin = min(group.begin, begin)
            group.end = max(group.end, end)
            group.name = name
            group.ref = ref
            group.hand = hand

        else:
            # group not found -> create
            g = Group(name, begin, end, uuid, priority, hand, ref)
            self.groups.append(g)


class Group(object):
    name = None
    uuid = None

    begin = None
    end = None

    priority = None
    hand = None
    ref = None

    def __init__(self, name, begin=None, end=None, uuid=None, priority=np.inf, hand=None, ref=None):
        assert name is not None, "SubGroup needs a name"

        self.name = name
        self.begin = begin
        self.end = end
        self.uuid = uuid
        self.priority = priority
        self.hand = hand
        self.ref = ref

    def overlaps(self, other):
        s_range = np.arange(self.begin, self.end)
        o_range = np.arange(other.begin, other.end)

        intersection = set(s_range).intersection(o_range)

        return len(intersection) > 0

class Corpus(object):
    documents = None

    def __init__(self):
        self.documents = []

class UniqeEtreeEl(object):
    uuid = None
    el = None

    def __init__(self, el):
        self.el = el
        self.uuid = str(uuid.uuid4())
