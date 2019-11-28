from flask import Flask,render_template,request,redirect,session,url_for,flash
from flask_mysqldb import MySQL
from datetime import datetime,time,date
from flask_login import LoginManager
from flask_login import login_required
from flask_mail import Mail, Message
from dateutil import relativedelta
import uuid
import re 
app=Flask(__name__)
login = LoginManager(app)
mail=Mail(app)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'MYDB'
mysql = MySQL(app)


#app.config['MAIL_SERVER']='smtp.gmail.com'
#app.config['MAIL_PORT'] = 465
#app.config['MAIL_USERNAME'] = 'cyz@gmail.com'
#app.config['MAIL_PASSWORD'] = "uhhgksglkd"
#app.config['MAIL_USE_TLS'] = False
#app.config['MAIL_USE_SSL'] = True
#mail = Mail(app)




regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
app.static_folder = 'static'


@app.route('/send')
def send():
    return render_template('forgot.html')

@app.route("/mail",methods=['POST','GET'])
def s_mail():
    if(request.method=='POST'):
        name=request.form['username']
        email=request.form['email']
        print(name)
    msg = Message('Hello', sender = 'cyz@gmail.com', recipients = email)
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
        if(len(f_name)==0  or len(email)==0 or len(password)==0 or len(city)==0 or len(state)==0 or len(zip)==0 or len(aadhar)==0 or len(mobile)==0 or len(username)==0 or len(date)==0):
            flash('*Fill in all the information','all')
            return render_template('signin.html')
            
        else:
            if(re.search(regex,email)):  
                print("Valid Email")     
            else:  
                flash('Enter a Valid Email','email')
                return render_template('signin.html')

            flag = 0
               
            if (len(password)<8): 
                flag = -1
            elif not re.search("[a-z]", password): 
                flag = -1      
            elif not re.search("[A-Z]", password): 
                flag = -1
            elif not re.search("[_@$]", password): 
                flag = -1
            elif re.search("\s", password): 
                flag = -1
            else: 
                flag = 0
                print("Valid Password") 
            
            if flag ==-1:  
                flash('Length>7 must Contain [@_-!],[A-Z],[a-z]','password')
                return render_template('signin.html')   
            if(len(mobile)<10 or len(mobile)>10):      
                flash('Enter a Valid Mobile No.','mob')
                return render_template('signin.html')   
            if(len(zip)!=6) :    
                flash('Invalid','zip')
                return render_template('signin.html')
            
            if(len(aadhar)!=12):   
                flash('Invalid','aadhar')
                return render_template('signin.html')        

                

        cur =  mysql.connection.cursor()
        try:
            query="INSERT INTO person(first,middle,last,email,password,City,State,Zip,Aadhar,Mobile,name,date,acc_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(query,(f_name,m_name,l_name,email,password,city,state,zip,aadhar,mobile,username,date,'User'))
            mysql.connection.commit()
            cur.close()
            flash('Account Created Please LogIn')
            return render_template('front.html')
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
        user=request.form['tvalue']
        name=request.form['username']
        email=request.form['email']
        password=request.form['password']
        if(len(name)==0 or len(email)==0 or len(password)==0):
            flash('*Fill in all the information')
            return render_template('front.html')
        else:    
            cur =  mysql.connection.cursor()
            query="SELECT * FROM person WHERE email=%s AND name=%s AND acc_type=%s"
            data=(email,name,user)
            cur.execute(query,data)
            fetchdata=cur.fetchall()
            if(len(fetchdata)==0):
                flash('*Please enter valid details')
                return render_template('front.html')

         
            if(user=='User'):
                if(fetchdata[0][5]==password):
                    session['loggedin'] = True
                    session['id'] = fetchdata[0][0]
                    session['username'] = fetchdata[0][11]
                    page=0
                    return redirect(url_for('sidebar',name=fetchdata[0][11],email=fetchdata[0][4],page=page))
                else:
                    flash('*Please enter valid details')
                    return render_template('front.html')
            elif(user=='Admin'):
                if(fetchdata[0][5]==password):
                    session['loggedin'] = True
                    session['id'] = fetchdata[0][0]
                    session['username'] = fetchdata[0][11]
                    
                    return redirect(url_for('admin',name=fetchdata[0][11],ap=1))
                else:
                    flash('*Please enter valid details')
                    return render_template('front.html') 
    

                       


def diff_month(d1, d2):
    print(d1.year)
    return (d1.year - d2.year) * 12 + d1.month - d2.month


@app.route("/sidebar/<name>/<email>/<int:page>")
def sidebar(name,email,page):
    #try:
        if(name==session['username']):
            cur =  mysql.connection.cursor()
            query="SELECT * FROM person WHERE email=%s AND name=%s"
            data=(email ,name)
            cur.execute(query,data)
            fetchdata=cur.fetchall()
            age=calculate_age(fetchdata[0][12])
            al=0   
            query1="SELECT apply,permanent,renewal,uni_id,date,lost FROM users WHERE email=%s AND name=%s"
            data=(email,name)
            cur.execute(query1,data)
            fetch1=cur.fetchall()
            print(fetch1) 
            if(page==0):
                if(len(fetch1)!=0):
                    return render_template('sidebar.html',l=list(fetchdata[0]),age=age,al=fetch1[0][0],per=fetch1[0][1],re=fetch1[0][2],id=fetch1[0][3],dt=fetch1[0][4],page=0)
                else:
                    return render_template('sidebar.html',l=list(fetchdata[0]),age=age,al=0,per=0,re=0,page=0)    
            elif(page==1):
                if(len(fetch1)!=0):
                    today=datetime.today()
                    print(today.year)
                    print(fetch1[0][4].year)
                    mn=diff_month(today,fetch1[0][4])
                    print(mn)
                    return render_template('perm.html',l=list(fetchdata[0]),age=age,al=fetch1[0][0],per=fetch1[0][1],re=fetch1[0][2],id=fetch1[0][3],dt=fetch1[0][4],mn=mn,page=1)
                else:
                    return render_template('perm.html',l=list(fetchdata[0]),age=age,al=0,per=0,re=0,page=1)
            elif(page==2):         
                if(len(fetch1)!=0):
                   # tm=calculate_age(fetch1[0][4])
                    #print(tm)
                    tm=0
                    return render_template('renewal.html',l=list(fetchdata[0]),age=age,al=fetch1[0][0],per=fetch1[0][1],re=fetch1[0][2],id=fetch1[0][3],dt=fetch1[0][4],tm=tm,page=2)
                else:
                    return render_template('renewal.html',l=list(fetchdata[0]),age=age,al=0,per=0,re=0,page=2)  

            elif(page==3):
                if(len(fetch1)!=0):
                   # tm=calculate_age(fetch1[0][4])
                    #print(tm)
                    tm=0
                    return render_template('lost.html',l=list(fetchdata[0]),age=age,al=fetch1[0][0],per=fetch1[0][1],re=fetch1[0][2],id=fetch1[0][3],dt=fetch1[0][4],tm=tm,lo=fetch1[0][5],page=3)
                else:
                    return render_template('lost.html',l=list(fetchdata[0]),age=age,al=0,per=0,re=0,page=3)   
            elif(page==4):
                query="SELECT * FROM person"
                cur.execute(query)
                fet=cur.fetchone()
                print(fet)
                return render_template('details.html',l=list(fetchdata[0]),l1=list(fet),page=4)
                             
                
                
                
        else:
            return "Please Log in Dude"    
    #except:
      #  return "error 404"        
         
#admin---------------------------------------------------------admin----------------------------admin-----------------------

@app.route('/admin/<name>/<int:ap>')
def admin(name,ap):
    if(ap==1):
        if(name==session['username']):
            cur =  mysql.connection.cursor()
            query="SELECT * FROM users "
           
            cur.execute(query, )
            fetchdata=cur.fetchall()
            print(len(fetchdata))
            return render_template('admin.html',l=list(fetchdata),name=name,ap=ap)
    elif(ap==2):
        if(name==session['username']):
            cur =  mysql.connection.cursor()
            query="SELECT * FROM users"
           
            cur.execute(query, )
            fetchdata=cur.fetchall()
            print(len(fetchdata))
            return render_template('admin.html',l=list(fetchdata),name=name,ap=ap)
    elif(ap==3):
        if(name==session['username']):
            cur =  mysql.connection.cursor()
            query="SELECT * FROM users "
         
            cur.execute(query, )
            fetchdata=cur.fetchall()
            print(len(fetchdata))
            return render_template('admin.html',l=list(fetchdata),name=name,ap=ap)
    elif(ap==4):
        if(name==session['username']):
            cur =  mysql.connection.cursor()
            query="SELECT * FROM users "
            cur.execute(query, )
            fetchdata=cur.fetchall()
            print(len(fetchdata))
            return render_template('admin.html',l=list(fetchdata),name=name,ap=ap) 

    elif(ap==5):
        if(name==session['username']):
            cur =  mysql.connection.cursor()
            query="SELECT * FROM users"
            cur.execute(query)
            fetchdata=cur.fetchall()
            print(len(fetchdata))
            return render_template('admin.html',l=list(fetchdata),name=name,ap=ap) 
    elif(ap==6):
        if(name==session['username']):
            cur =  mysql.connection.cursor()
            query="SELECT * FROM users"
            cur.execute(query)
            fetchdata=cur.fetchall()
            print(len(fetchdata))
            return render_template('admin.html',l=list(fetchdata),name=name,ap=ap)       
    elif(ap==8):
        if(name==session['username']):
            cur =  mysql.connection.cursor()
            query="SELECT * FROM users"
            cur.execute(query)
            fetchdata=cur.fetchall()
            query="SELECT count(*) FROM users WHERE date=%s"
            today = date.today()
            data=(today, )
            cur.execute(query,data)
            cnt=cur.fetchone()
            print(cnt)
            query="SELECT count(*) from users WHERE YEAR(date)=%s"
            data=("2019", )
            cur.execute(query,data)
            cnt1=cur.fetchone()
            print(cnt1)
            query="SELECT count(*) from users WHERE apply=2"
            cur.execute(query)
            cnt2=cur.fetchone()
            print(cnt2)
            query="SELECT count(*) from users WHERE permanent=2"
            cur.execute(query)
            cnt3=cur.fetchone()
            print(cnt3)
            query="SELECT count(*) from users WHERE permanent=2"
            cur.execute(query)
            cnt3=cur.fetchone()
            print(cnt3)
            query="SELECT count(*) from person WHERE acc_type=%s"
            data=("User", )
            cur.execute(query,data)
            cnt4=cur.fetchone()
            print(cnt4)
            query="SELECT count(*) from person WHERE City=%s AND acc_type=%s"
            data=("Kanpur","User")
            cur.execute(query,data)
            cnt5=cur.fetchone()
            print(cnt5)
            return render_template('admin.html',l=list(fetchdata),name=name,ap=8,cnt=cnt,cnt1=cnt1,cnt2=cnt2,cnt3=cnt3,cnt4=cnt4,cnt5=cnt5)         

                     


@app.route('/check/<name>/<int:ap>', methods=['POST','GET'])
def check(name,ap):
    if(request.method=='POST'):
        cur =  mysql.connection.cursor()
        reg=request.form['reg']
        query="SELECT * FROM users WHERE uni_id=%s"
        data=(reg, )
        cur.execute(query,data)
        fet=cur.fetchall()
        print(fet)
        query="SELECT * FROM person WHERE name=%s"
        data=(fet[0][1], )
        cur.execute(query,data)
        fet=cur.fetchone()

        query="SELECT * FROM users"
        cur.execute(query)
        fetchdata=cur.fetchone()
        print(fet)
        return render_template('admin.html',l=list(fetchdata),name=name,ap=7,l1=list(fet))



@app.route('/admina/<aname>/<name>/<email>/<int:ap>')
def admina(aname,name,email,ap):
    if(ap==1):
        if(aname==session['username']):
            
            cur =  mysql.connection.cursor()
            query1=("UPDATE users SET apply=%s WHERE name=%s AND email=%s")
            data=(2,name,email)
            cur.execute(query1,data)
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('admin',name=aname,ap=ap))     
        else:
            print(name,email)
            return "not logged int"
    elif(ap==2):
        if(aname==session['username']):
            print("hkbbbbbbbbbbbbbbbbbdkjfffffffffffffdsnfjnds")
            cur =  mysql.connection.cursor()
            query1=("UPDATE users SET permanent=%s WHERE name=%s AND email=%s")
            data=(2,name,email)
            cur.execute(query1,data)
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('admin',name=aname,ap=ap))     
        else:
            print(name,email)
            return "not logged int"   
    elif(ap==3):
        if(aname==session['username']):
            print("hkbbbbbbbbbbbbbbbbbdkjfffffffffffffdsnfjnds")
            cur =  mysql.connection.cursor()
            query1=("UPDATE users SET renewal=%s WHERE name=%s AND email=%s")
            data=(2,name,email)
            cur.execute(query1,data)
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('admin',name=aname,ap=ap))     
        else:
            print(name,email)
            return "not logged int"                        
    elif(ap==4):
        if(aname==session['username']):
            print("hkbbbbbbbbbbbbbbbbbdkjfffffffffffffdsnfjnds")
            cur =  mysql.connection.cursor()
            query1=("UPDATE users SET lost=%s WHERE name=%s AND email=%s")
            data=(2,name,email)
            cur.execute(query1,data)
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('admin',name=aname,ap=ap))     
        else:
            print(name,email)
            return "not logged int"
    elif(ap==5):
        if(aname==session['username']):
            print("hkbbbbbbbbbbbbbbbbbdkjfffffffffffffdsnfjnds")
            cur =  mysql.connection.cursor()
            query1=("UPDATE users SET lost=%s WHERE name=%s AND email=%s")
            data=(2,name,email)
            cur.execute(query1,data)
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('admin',name=aname,ap=ap))     
        else:
            print(name,email)
            return "not logged int"  
    elif(ap==6):
        if(aname==session['username']):
            print("hkbbbbbbbbbbbbbbbbbdkjfffffffffffffdsnfjnds")
            cur =  mysql.connection.cursor()
            query1=("UPDATE users SET lost=%s WHERE name=%s AND email=%s")
            data=(2,name,email)
            cur.execute(query1,data)
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('admin',name=aname,ap=ap))     
        else:
            print(name,email)
            return "not logged int"            
            
                       

        

#<admin>------------------------------------------------<admin>-------------------------------<admin>------------------------




@app.route('/apply/<name>/<email>',methods=['POST','GET'])
def apply(name,email):
    if(request.method=='POST'):
        cur =  mysql.connection.cursor()
        query="SELECT name,email FROM person WHERE email=%s AND name=%s"
        data=(email,name)
        cur.execute(query,data)
        fetchdata=cur.fetchone()
        query="SELECT * FROM users WHERE email=%s AND name=%s"
        data=(email,name)
        cur.execute(query,data)
        fetchone=cur.fetchall()
        print(len(fetchone))
        if(len(list(fetchone))==0):
            try:
                today = date.today()
                query1="INSERT INTO users(name,email,apply,permanent,renewal,lost,uni_id,date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                stri=str(uuid.uuid4().int)
                d1 = today.strftime("%Y-%m-%d")
                value=(name,email,1,0,0,0,stri[:12],d1)
                cur.execute(query1,value)
                mysql.connection.commit()
                query="INSERT INTO request(reg,name) VALUES (%s,%s)"
                value=(stri[:12],name)
                cur.execute(query,value)
                mysql.connection.commit()
                cur.close()
            except:
                return "cannot be inserted"    
            
        return redirect(url_for('sidebar',name=name,email=email,page=0))

@app.route('/permanent/<name>/<email>')
def permanent(name,email):
    print(name,email)
    cur =  mysql.connection.cursor()
    query="SELECT name,email FROM person WHERE email=%s AND name=%s"
    data=(email,name)
    cur.execute(query,data)
    fetchdata=cur.fetchone()
    query1=("UPDATE users SET permanent=%s WHERE name=%s AND email=%s")
    data=(1,name,email)
    cur.execute(query1,data)
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('sidebar',name=name,email=email,page=1))


@app.route('/renewal/<name>/<email>')
def renewal(name,email):
    print(name,email)
    cur =  mysql.connection.cursor()
    query="SELECT name,email FROM person WHERE email=%s AND name=%s"
    data=(email,name)
    cur.execute(query,data)
    fetchdata=cur.fetchone()
    query1=("UPDATE users SET renewal=%s WHERE name=%s AND email=%s")
    data=(1,name,email)
    cur.execute(query1,data)
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('sidebar',name=name,email=email,page=2))


@app.route('/lost/<name>/<email>',methods=['POST','GET'])
def lost(name,email):
    if(request.method=='POST'):
        if(len(request.form['fir'])==0):
            flash('*Fill F.I.R Num')
            return redirect(url_for('sidebar',name=name,email=email,page=3))
        else:    
            cur =  mysql.connection.cursor()
            query="SELECT name,email FROM person WHERE email=%s AND name=%s"
            data=(email,name)
            cur.execute(query,data)
            fetchdata=cur.fetchone()
            query1=("UPDATE users SET lost=%s WHERE name=%s AND email=%s")
            data=(1,name,email)
            cur.execute(query1,data)
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('sidebar',name=name,email=email,page=3))


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('start'))



if __name__=='__main__':
    app.run(debug=True)
