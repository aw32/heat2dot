#!/usr/bin/python3
# small server to serve heat2dot conversion and output as svg

import subprocess
import time
import os
from flask import Flask
from flask import request
from flask import Markup
app = Flask(__name__)

PORT = 1111

@app.route('/')
def main():
    return ("<html><head><title>heat2dot</title></head><body>"
            "<form method=\"POST\" action=\"convert\">"
            "Enter json or yaml text:<br/>"
            "<textarea name=\"text\"></textarea><br/>"
            "<input type=\"submit\"/>"
            "</form>"
            "</body></html>")

@app.route('/convert',methods=['POST'])
def convert():
    if "text" not in request.form:
        return "<html><head><title>heat2dot</title></head><body>Text not found</body></html>",403
    
    infile = "/tmp/inheat2dot_"+str(time.time())
    dotfile = "/tmp/inheat2dot_"+str(time.time())+".dot"

    with open(infile,"w") as intextfile:
        intextfile.write(request.form["text"])
    
    error_messages = None
    svg = None

    try:
        h2d_out = subprocess.run(["cat "+infile+" | ./heat2dot.py > "+dotfile],shell=True,stderr=subprocess.PIPE)
        error_messages = h2d_out.stderr.decode("UTF-8")

        if h2d_out.returncode != 0:
        
            return Markup("<html><head><title>heat2dot</title></head><body>Failure<br/><pre>")+Markup.escape(h2d_out.stderr.decode("UTF-8"))+Markup("</pre></body></html>")
        else:
            dot_out = subprocess.run(["dot -Tsvg "+dotfile],shell=True,stdout=subprocess.PIPE)
            svg = dot_out.stdout.decode("UTF-8")
    except Exception as e:
        print(e)
    finally:
        try:
            os.remove(infile)
        except:
            pass
        try:
            os.remove(dotfile)
        except:
            pass
    
    if error_messages != None and svg == None:
        return Markup("<html><head><title>heat2dot</title></head><body>Failure<br/><pre>")+Markup.escape(error_messages)+Markup("</pre></body></html>")
    elif svg != None:
        if error_messages == None:
            return (Markup("<html><head><title>heat2dot</title></head><body>")+
                    Markup(svg)+
                    Markup("</body></html>"))
        else:
            return (Markup("<html><head><title>heat2dot</title></head><body>")+
                    Markup(svg)+
                    Markup("<br/><pre>")+
                    Markup.escape(error_messages)+
                    Markup("</pre></body></html>"))
    else:
        return "<html><head><title>heat2dot</title></head><body>Something went horribly wrong.</body></html>"

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=PORT)

