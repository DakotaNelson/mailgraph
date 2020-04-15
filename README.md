# mailgraph
Build a GEFX graph file of who has sent mail to whom.

Usage
-----

```
virtualenv --python=python3 venv
source venv/bin/activate
pip install -r requirements.txt
python mailgraph.py -o outputfile.gexf file-to-parse.mbox another-file.mbox
```

The script will then churn through the files you provided, and output `outputfile.gexf`. This can be loaded using [Gephi](https://gephi.org/) and explored. Gephi is awesome, and makes it incredibly easy to poke through this data. Poke through the [list of features](https://gephi.org/features/) if you're curious about what you can do with Gephi. (You could use other software too - GEXF is a standard format.)
