import sys, os, lucene, threading, time
from datetime import datetime

from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, StringField, TextField
from org.apache.lucene.index import \
    FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.store import RAMDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search.similarities import ClassicSimilarity,BooleanSimilarity


def addDoc(w, title, isbn):
    t1 = FieldType()
    t1.setStored(True)
    t1.setTokenized(True)
    t1.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

    t2 = FieldType()
    t2.setStored(False)
    t2.setTokenized(True)
    t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
    
    doc = Document()
    doc.add(Field("title", title, t1))
    doc.add(Field("isbn", isbn, t1))
    w.addDocument(doc)

lucene.initVM(vmargs=['-Djava.awt.headless=true'])
print('lucene', lucene.VERSION)
start = datetime.now()
analyzer = StandardAnalyzer()
similarity = BooleanSimilarity()
#similarity = ClassicSimilarity()
index = RAMDirectory()

config = IndexWriterConfig(analyzer)
config.setSimilarity(similarity)
w = IndexWriter(index, config)

file = open('./ohsumed.88-91', 'r')
lines = file.readlines()
file.close()
last = ''
for line in lines:
    if last == '.U':
        u = line.strip()
    if last == '.W':
        wr = line.strip()
        addDoc(w, wr, u)
    last = line.strip()

w.close()
querys=[]
file = open('query.ohsu.1-63', 'r')
lines = file.readlines()
file.close()
for line in lines:
    if len(line) > 1 and line[1] == 'n' and line[0] =='<':
        qid = line.split()[2]
    if line[0] != '<' and len(line) > 1:
        cmd = line.replace('/',' ')
        querys.append((qid, cmd))

#print(querys)

log = open('boolean.ohsu','w')
for qid, command in querys:
    query = QueryParser("title", analyzer).parse(command)
    reader = DirectoryReader.open(index)
    searcher = IndexSearcher(reader)
    searcher.setSimilarity(similarity)
    hits = searcher.search(query, 50).scoreDocs
    for i in range(len(hits)):
        docId = hits[i].doc
        d = searcher.doc(docId)
        log.write('{} Q0 {} {} {} Boolean\n'.format(qid, d.get('isbn'), i+1, hits[i].score))

log.close()

print('Hello from the other side')
