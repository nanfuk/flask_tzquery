# -*- coding:utf8 -*-
from flask import Flask



app = Flask(__name__)

@app.before_first_request
def test():
    print "test"

if __name__ == "__main__":
    #test()
    app.run(debug=True)