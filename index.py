from flask import Flask,render_template,request,redirect,session,url_for
from flask_mysqldb import MySQL
from datetime import datetime,time
from flask_login import LoginManager
from flask_login import login_required
from flask_mail import Mail, Message

app=Flask(__name__)
login = LoginManager(app)
mail=Mail(app)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'MYDB'
mysql = MySQL(app)


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'corpojasltd@gmail.com'
app.config['MAIL_PASSWORD'] = 
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


app.static_folder = 'static'


@app.route('/send')
def send():
    return render_template('forgot.html')

@app.route("/mail",methods=['POST','GET'])
def s_mail():
    if(request.method=='POST'):
        name=request.form['name']
        print(name)
    msg = Message('Hello', sender = 'corpojasltd@gmail.com', recipients = ['ojasgupta.456@gmail.com'])
    msg.body = "Hello Flask message sent from Flask-Mail"
    return "hello"



@app.route('/')
def start():
    return render_template('front.html')

@app.route('/signup')
def signup():
    return render_template('signin.html')    


def calculate_age(born):
    birth_date = born
    print(born)
    today = datetime.today()
    print(today)
    years = today.year - birth_date.year
    if all((x >= y) for x,y in zip(today.timetuple(), birth_date.timetuple())):
        age = years
    else:
        age = years - 1
    return age


@app.route('/signin',methods=['POST','GET'])
def create():
    if request.method=='POST':
        f_name=request.form['first']
        m_name=request.form['middle']
        l_name=request.form['last']
        email=request.form['email']
        password=request.form['password']
        city=request.form['city']
        state=request.form['state']
        zip=request.form['zip']
        aadhar=request.form['aadhar']
        mobile=request.form['mobile']
        username=request.form['name']
        date=request.form['date']
        print(date)
        print(date)
        cur =  mysql.connection.cursor()
        try:
            query="INSERT INTO person(first,middle,last,email,password,City,State,Zip,Aadhar,Mobile,name,date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(query,(f_name,m_name,l_name,email,password,city,state,zip,aadhar,mobile,username,date))
            mysql.connection.commit()
            cur.close()
            return render_template("signin.html")
        except:
            return "This Email has already been registered"          

        #cur.execute("SELECT * FROM users")
        #fetchdata=cur.fetchall()
        #cur.close()
        #print(fetchdata)
      

@app.route('/login',methods=['POST','GET'])
def login():
    if(request.method=='POST'):
        name=request.form['username']
        email=request.form['email']
        password=request.form['password']
        cur =  mysql.connection.cursor()
        query="SELECT * FROM person WHERE email=%s AND name=%s"
        data=(email ,name)
        cur.execute(query,data)
        fetchdata=cur.fetchall()
        print(fetchdata[0])
        if(fetchdata[0][5]==password):
            session['loggedin'] = True
            session['id'] = fetchdata[0][0]
            session['username'] = fetchdata[0][11]
           
            return redirect(url_for('sidebar',name=fetchdata[0][11],email=fetchdata[0][4]))
        else:
            return "not loggd in"    


@app.route('/sidebar/<name>/<email>')
def sidebar(name,email):
    try:
        if(name==session['username']):
            cur =  mysql.connection.cursor()
            query="SELECT * FROM person WHERE email=%s AND name=%s"
            data=(email ,name)
            cur.execute(query,data)
            fetchdata=cur.fetchall()
            age=calculate_age(fetchdata[0][12])
            return render_template('sidebar.html',l=list(fetchdata[0]),age=age)
        else:
            return "Please Log in Dude"    
    except:
        return "error 404"        


@app.route('/apply', methods=['POST','GET'])
def apply():
    if(request.method=='POST'):
        drop=request.form['tvalue']
        return drop








@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('start'))


    

if __name__=='__main__':
    app.run(debug=True)
