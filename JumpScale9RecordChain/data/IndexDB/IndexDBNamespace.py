
from js9 import j
from pprint import pprint as print
from functools import reduce
JSBASE = j.application.jsbase_get_class()


class IndexDBNamespace(JSBASE):

    def __init__(self, namespace):
        self.db = j.clients.redis.core_get()
        self.namespace = namespace

        self.path = "%s/indexdb/%s/" % (j.dirs.VARDIR, self.namespace)
        j.sal.fs.createDir(self.path)
        JSBASE.__init__(self)

    def _hsetKeys(self, name):
        if len(name) > 3:
            pre = self.namespace + "_" + name[0:2]
            post = name[2:]
        else:
            pre = self.namespace
            post = name
        return pre, post

    def index_add_term(self, name, uid):
        """
        builds a dense index in redis
        will first make the text dense & remove all unrelevant items
        then will take all words out
        and store the words with references to the uid in binary form

        """
        res = j.data.nltk.dense(name, removespaces=False, word_minsize=4)
        if res == "":
            return
        print(res)

        for item in res.split(" "):

            pre, post = self._hsetKeys(item)
            # pre & post for performance & mem usage

            bdata = self.db.hget(pre, post)
            if bdata == None:
                # does not exist yet, need to add
                bdata = j.tools.numtools.listint_to_bin([uid])
                self.db.hset(pre, post, bdata)
                print("hset:%s:%s:%s" % (pre, post, [uid]))
            else:
                print("exist")
                llist = j.tools.numtools.bin_to_listint(bdata)
                if uid not in llist:
                    llist.append(uid)
                    bdata = j.tools.numtools.listint_to_bin(llist)
                    self.db.hset(pre, post, bdata)
                    print("hset:%s:%s:%s" % (pre, post, llist))

    def find(self, terms):
        res = []
        for term in terms:
            term = j.data.nltk.dense(term, removespaces=False, word_minsize=4)
            if " " in term:
                print("found space in term")
                from IPython import embed
                embed(colors='Linux')
            pre, post = self._hsetKeys(term)
            bdata = self.db.hget(pre, post)
            if bdata != None:
                res.append(j.tools.numtools.bin_to_listint(bdata))

        # now need to find the ones which exist in all items of res (need to find the union)

        res = [set(item) for item in res]
        res2 = reduce(set.intersection, res)

        return res2

    def test(self):
        """
        js9 'j.data.bcdb.test()'

        """

        import nltk
        # nltk.download('brown')
        from nltk.corpus import brown

        j.tools.timer.start("perftest_index")
        nr = 100
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
        for i in range(nr):
            rand = j.data.idgenerator.generateRandomInt(1, 8)  # to create sentences
            toindex = ""
            for i in range(rand):
                picknr = j.data.idgenerator.generateRandomInt(0, nr * 10 - 1)
                word = words[picknr]
                words1.append(word)
                toindex += " %s" % word

            toindex = toindex.strip()
            self.index_add_term(toindex, i)

        j.tools.timer.stop(nr)

        w1 = getword(words1)
        w2 = getword(words1)
        w3 = getword(words1)
        res = self.find(namespace, [w1])
        res1 = self.find(namespace, [w2, w3])

        from IPython import embed
        embed(colors='Linux')
