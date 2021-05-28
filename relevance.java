//Get the original results
TopDocs docs = indexsearcher.search(query,50);
HashMap<String,ScorePair> map = new HashMap<String,ScorePair>();
for (int i = 0; i < docs.scoreDocs.length; i++) {
    FieldsEnum fields = indexreader.getTermVectors(docs.scoreDocs[i].doc).iterator();
    String fieldname;
    while (fieldname = fields.next()) {
        TermsEnum terms = fields.terms().iterator();
        while (terms.next()) {
            putTermInMap(fieldname, terms.term(), terms.docFreq(), map);
        }
    }
}

List<ScorePair> byScore = new ArrayList<ScorePair>(map.values());
Collections.sort(byScore);

BooleanQuery bq = new BooleanQuery();
query.setBoost(5);
bq.add(query,BooleanClause.Occur.SHOULD);
for (int i = 0; i < 50; i++) {
    ScorePair pair = byScore.get(i);
    bq.add(new TermQuery(new Term(pair.field,pair.term)),BooleanClause.Occur.SHOULD);
}
}

void putTermInMap(String field, String term, int freq, Map<String,ScorePair> map) {
    String key = field + ":" + term;
    if (map.containsKey(key))
        map.get(key).increment();
    else
        map.put(key,new ScorePair(freq,field,term));
}

private class ScorePair implements Comparable{
    int count = 0;
    double idf;
    String field;
    String term;

    ScorePair(int docfreq, String field, String term) {
        count++;
        idf = (1 + Math.log(indexreader.numDocs()/((double)docfreq + 1))) ^ 2;
        this.field = field;
        this.term = term;
    }

    void increment() { count++; }

    double score() {
        return Math.sqrt(count) * idf;
    }

    int compareTo(ScorePair pair) {
        if (this.score() < pair.score()) return -1;
        else return 1;
    }
}
