from flask import Flask, render_template, request, url_for, redirect, session
import mysql.connector
from datetime import datetime

#Initialize the app from Flask
app = Flask(__name__)
app.secret_key = 'some key that you will never guess'

print("------------Initialized")

try:
    conn = mysql.connector.connect(
        host='127.0.0.1',
		# host='localhost',
        user='root',
        password='',
        database='airTicket'
    )
    print("------------Configure")
except Exception as e:
    print(">>> Database connection failed:", e)
    exit(1)
# ├── static/
# │   └── css/
# │       └── style.css
# # airticket/
# # │
# # ├── index.html             // 首页
# # ├── login.html             // 登录页面
# # ├── register.html          // 注册页面
# # ├── customer_home.html     // 客户主页
# # ├── agent_home.html        // 代理主页
# # ├── staff_home.html        // 航空公司工作人员主页
# # │
# # ├── css/
# # │   └── style.css          // 所有页面共用的样式表
# # │
# # └── js/
# #     └── main.js            // 用于未来交互的JS


#Define a route to hello function
@app.route('/')
def hello():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
	return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')

# @app.route('/logout')
# def login():
# 	return render_template('logout.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = "SELECT * FROM user WHERE username = '{}' and password = '{}'"
	cursor.execute(query.format(username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = "SELECT * FROM user WHERE username = '{}'"
	cursor.execute(query.format(username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins = "INSERT INTO user VALUES('{}', '{}')"
		cursor.execute(ins.format(username, password))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/home')
def home():
    username = session['username']
    cursor = conn.cursor();
    query = "SELECT ts, blog_post FROM blog WHERE username = '{}' ORDER BY ts DESC"
    cursor.execute(query.format(username))
    data1 = cursor.fetchall() 
    cursor.close()
    return render_template('home.html', username=username, posts=data1)
	
@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['username']
	cursor = conn.cursor();
	blog = request.form['blog']
	query = "INSERT INTO blog (blog_post, username) VALUES('{}', '{}')"
	cursor.execute(query.format(blog, username))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')

@app.route('/upcoming-flights')
def upcoming_flights():
    print("----flight page----")

    # 利用 mysql.connector 获取数据库游标，设置 dictionary=True 以字典形式返回数据
    cursor = conn.cursor(dictionary=True)
    try:
        # 根据 flight 表中 departure_time 过滤出当前时间之后的航班信息
        query = """
            SELECT airline_name, flight_num, departure_airport, departure_time, 
                   arrival_airport, arrival_time, status 
            FROM flight 
            WHERE departure_time >= %s 
            ORDER BY departure_time ASC
        """
        cursor.execute(query, (datetime.now(),))
        # conn.commit()

        flights = cursor.fetchall()
    except Exception as e:
        print("查询错误：", e)
        flights = []
    finally:
	    # conn.commit()
        cursor.close()
    return render_template('flights.html', flights=flights)


app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION

# if __name__ == "__main__":
#     print(">>> Flask is starting...")
#     app.run('127.0.0.1', 5000, debug=True)
#     print(">>> Flask has stopped")
if __name__ == "__main__":
    print(">>> Flask is starting...")
    try:
        app.run(host='127.0.0.1', port=5000, debug=True)
    except Exception as e:
        print(">>> ERROR:", e)

	