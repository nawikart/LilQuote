import re
from flask import Flask, session, request, redirect, render_template, flash, url_for

from db.data_layer import get_all_quotes, get_all_quotes_for, get_all_quotes_by_uids, search_by_user_or_email, create_quote, delete_quote, create_user, get_user_by_id, get_user_by_email, get_user_by_name, create_user

EMAIL_REGEX = re.compile(r'^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$')

app = Flask(__name__)
app.secret_key = '0d599f0ec05c3bda8c3b8a68c32a1b47'

def is_blank(name, field):
    if len(field) == 0:
        flash('{} cant be blank'.format(name))
        return True
    return False

@app.route('/')
def index():
    return render_template('index.html', all_quotes = get_all_quotes())

@app.route('/create_quote', methods=['POST'])
def create__quote():
    create_quote(session['user_id'], request.form['html_content'])
    return redirect(url_for('index'))

@app.route('/delete/<quote_id>')
def delete__quote(quote_id):
    delete_quote(quote_id)
    return redirect(url_for('index'))

@app.route('/search')
def search():
    return redirect(url_for('search_users', query=request.args['html_query']))
    
@app.route('/results/<query>')
def search_users(query):
    try:
        users = search_by_user_or_email(query)
        print('------------------------')
        uids = []
        for u in users:
            uids.append(str(u.id))
            
        return render_template('index.html', all_quotes = get_all_quotes_by_uids(','.join(uids)))
    except:
        flash('username didnt match.')

    return render_template('index.html', all_quotes = get_all_quotes())

@app.route('/user/<user_id>')
def user_quotes(user_id):
    return render_template('index.html', all_quotes = get_all_quotes_for(user_id))

@app.route('/login-form')
def login_form():
    return render_template('login.html')

@app.route('/register-form')
def register_form():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    fullname = request.form['html_fullname']
    username = request.form['html_username']
    email = request.form['html_email']
    password = request.form['html_password']
    confirm = request.form['html_confirm']

    is_valid = not is_blank('fullname', fullname)
    is_valid = not is_blank('email', email)
    is_valid = not is_blank('password', password)
    is_valid = not is_blank('confirm', confirm)

    if not EMAIL_REGEX.match(email):
        is_valid = False
        flash('invalid email format')

    if password != confirm:
        is_valid = False
        flash('password did not match')
    
    if(len(password) < 6):
        is_valid = False
        flash('password is too short')    

    if is_valid:
        try:
            user = create_user(fullname, username, email, password)
            setup_web_session(user)
            return redirect(url_for('index'))
        except:
            flash('email already registered.')

    return redirect(url_for('register_form'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['html_email']
    password = request.form['html_password']

    try:
        user = get_user_by_email(email)
        if user.password == password:
            setup_web_session(user)
            return redirect(url_for('index'))
        else:
            flash('password do not match')
    except:
        flash('invalid login')

    return redirect(url_for('login_form'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def setup_web_session(user):
    session['user_id'] = user.id
    session['username'] = user.username
    return True


app.run(debug=True)