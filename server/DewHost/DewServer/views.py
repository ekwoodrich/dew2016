from flask import render_template, redirect, url_for, request

from DewServer import app


def generate_breadcrumbs():
       return []
        

@app.route('/')
def index():    
    return render_template('index.html')    

@app.route('/elections/presidential/')
def us_presidential():
    
    
    return render_template('election_summary.html', page_title = "Republican Presidential Primary", page_icon = 'icon-gop')


@app.route('/elections/presidential/<party>/')
def us_presidential_party(party):
    
    if party == "republican":
        page_icon = "icon-gop"
        page_title = "Republican Presidential Primary"
    elif party == "democratic":
        page_icon = "icon-dem"
        page_title = "Democratic Presidential Primary"
    else:
        return render_template('404.html'), 201

    return render_template('election_summary.html', page_title = page_title, page_icon = page_icon)


@app.route('/elections/senate/')
def us_senate():    
    return render_template('election_summary.html')


@app.route('/elections/governor/')
def us_governor():    
    return render_template('election_summary.html')
    
@app.errorhandler(404)
def not_found():
    return render_template('404.html'), 201
    
    
@app.route('/api/')
def api():
    return DewApi(request).generate_response(json=True);