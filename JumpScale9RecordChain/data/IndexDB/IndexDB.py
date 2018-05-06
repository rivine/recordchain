
from js9 import j
from pprint import pprint as print

from .IndexDBNamespace import *
JSBASE = j.application.jsbase_get_class()


class IndexDB(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.data.indexdb"
        JSBASE.__init__(self)

    def get(self, namespace):
        return IndexDBNamespace(namespace)

    def test(self):
        """
        js9 'j.data.indexdb.test()'

        """

        db = self.get("myns")

        import nltk
        nltk.download('brown')
        from nltk.corpus import brown

        nr = 1000
        namespace = "myns"
        words = brown.words()[:nr * 10]

        def getword(words):
            found = ""
            while len(found) < 5:
                picknr = j.data.idgenerator.generateRandomInt(0, len(words1))
                found = words[picknr]
            return found

        pos = 0
        name1 = ""
        words1 = []

        j.tools.timer.start("perftest_index")
        for i in range(nr):
            rand = j.data.idgenerator.generateRandomInt(1, 8)  # to create sentences
            toindex = ""
            for i in range(rand):
                picknr = j.data.idgenerator.generateRandomInt(0, nr * 10 - 1)
                word = words[picknr]
                words1.append(word)
                toindex += " %s" % word

            toindex = toindex.strip()
            db.index_add_term(toindex, i)

        j.tools.timer.stop(nr)

        w1 = getword(words1)
        w2 = getword(words1)
        w3 = getword(words1)
        res = db.find([w1])
        res1 = db.find([w2, w3])

