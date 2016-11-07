# heat2dot
Heat template to graphviz dot file convertor

Dependencies:
* PyYaml

Optional dependency:
* e.g. Graphviz for graph layout and rendering

Usage:
```
cat heat.json | ./heat2dot.py > heat.dot
cat heat.yaml | ./heat2dot.py > heat.dot
```

Afterwards:
* Convert using graphviz: ```dot -Tsvg heat.dot -o heat.svg```
* Display using e.g. Xdot: ```xdot heat.dot```

Server:
Minimal HTML server to serve the generated graph as svg.
Temp files are written to /tmp and removed afterwards.
Default port 1111.

Dependencies:
* Graphviz
* Flask

Usage:
```
./heat2dot_server.py
```
