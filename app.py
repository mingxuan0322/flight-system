from flask import Flask, render_template, request, url_for, flash, redirect, session
import mysql.connector
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime, timedelta
import json
import random

#Initialize the app from Flask
app = Flask(__name__)
app.secret_key = 'some key that you will never guess'

print("------------Initialized---------------------")

try:
    conn = mysql.connector.connect(
        host='127.0.0.1',
		# host='localhost',
        user='root',
        password='',
        database='flight_system'
    )
    print("------------Configure-------------------")
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
    # username = session.get('username')  # ✅ 如果没登录会返回 None，不报错
    username = session.get('username')
    # print("----------------Hello------------")

    if not username:
        print("----------------index------------")

        return redirect(url_for('search'))
    print("----------------homepage------------")
    return redirect(url_for('home'))
    
    # if 'username' in session:
    #     return redirect(url_for('home'))
    # return redirect(url_for('search'))
    # return render_template('index.html')

# @app.route('/index', methods=['GET'])
# @app.route('/index', methods=['GET'])
@app.route('/index', methods=['GET'])
# def search():
def search():
    flights = []  # ✅ 初始化为默认空列表
    departure_airport = request.args.get('from', '').strip()
    arrival_airport = request.args.get('to', '').strip()
    departure_date = request.args.get('date', '').strip()

    if not departure_airport and not arrival_airport and not departure_date:
        flash("请填写至少一个搜索条件", "danger")
        return render_template('index.html', flights=flights)
    
    try:
        cursor = conn.cursor(dictionary=True)
        conditions = []
        params = []

        if departure_airport:
            conditions.append("departure_airport LIKE %s")
            params.append(f"%{departure_airport}%")
        if arrival_airport:
            conditions.append("arrival_airport LIKE %s")
            params.append(f"%{arrival_airport}%")
        if departure_date:
            conditions.append("DATE(departure_time) = %s")
            params.append(departure_date)

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT flight_num, airline_name, departure_time, arrival_time, departure_airport, arrival_airport, status
            FROM flight
            WHERE {where_clause}
        """

        cursor.execute(query, params)
        flights = cursor.fetchall()

        print("-------查询结果数量:", len(flights))
        print("-------SQL:", query)
        print("-------Params:", params)

    except Exception as e:
        flash("查询失败，请检查搜索条件或稍后重试", "danger")
        print("查询错误:", e)
        flights = []

    finally:
        print(flights)
        print("flights 类型：", type(flights))
        print("flights 内容：", flights)


        cursor.close()

    return render_template('index.html', flights=flights)
    # return render_template('index.html', flights=flights,username=session.get('username'))

# #################################################################################################################
@app.route('/book/<airline_num>/<int:flight_num>')
def book_flight(airline_num, flight_num):
    # 实现订票逻辑
    return f"Booking page for flight {airline_num} #{flight_num}"
    # return redirect(url_for('home'))

# #################################################################################################################
# @app.route('/login')
# def login():
	# return render_template('login.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #get what user input in the login page
        identity = request.form.get('identity')
        email = request.form.get('username').lower()
        # email = request.form.get('login_email').lower().split('@')[0] + '@' + request.form.get('login_email').split('@')[1]
        password = request.form.get('password')  #这里get到的密码应该是输入进去什么就是什么，输入1这里就是1
        
        print(identity, email, password)

        #通过identity定位我从哪个table里面查找我的用户
        table_map = {
            'customer': 'customer',
            'agent': 'booking_agent',
            'staff': 'airline_staff'
        }

        if identity not in table_map:
            flash("Invalid role selected", "danger")
            return render_template("login.html", error="Invalid role")

        table = table_map[identity]
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {table} WHERE email = %s"
        cursor.execute(query, (email,))
        # cursor.execute(f"SELECT * FROM {table} WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        print('----------------user', user)

        if user and check_password_hash(user['password'], password):
            session['user'] = {
                'email': user['email'],
                'identity': identity
            }


        if user and check_password_hash(user['password'], password):
            session['user'] = {
                'email': user['email'],
                'identity': identity
            }

            flash("Login successful!", "success")
            print(f"Redirecting to {identity}_dashboard test")

            if identity == 'customer':
                print(f"Redirecting to {identity}_dashboard")
                return redirect(url_for('customer_dashboard'))
                # print(f"Redirecting to {identity}_dashboard")
            elif identity == 'agent':
                session['user']['agent_id'] = user['booking_agent_id']
                print(session)
                print(f"Redirecting to {identity}_dashboard")
                return redirect(url_for('agent_dashboard'))
            elif identity == 'staff':
                session['user']['airline_name'] = user['airline_name']
                cursor.execute("SELECT permission_type FROM permission WHERE email = %s", (email,))
                permissions = cursor.fetchall()
                # print("permission get from database",permissions)

                if permissions:
                    # 提取权限类型的值
                    session['user']['permissions'] = [permission['permission_type'] for permission in permissions]
                else:
                    session['user']['permissions'] = []  # 没有权限时为空列表
                # print("permissions after processing:", session['user']['permissions'])   
                             
                # 权限为空 设置一个默认值
                if not session['user']['permissions']:
                    session['user']['permissions'] = ['None']
    
                print(session)
                print(f"Redirecting to {identity}_dashboard")

                return redirect(url_for('staff_dashboard'))
        else:
            # 登录失败
            flash("Invalid email or password. Please try again.", "error")
            return redirect(url_for('login'))
        
        # except mysql.connector.Error as err:
        #     print(f"Database error: {err}")
        #     flash("Database error. Please try again later.", "error")
        #     return redirect(url_for('login'))
        # finally:
        #     print('login-finally')
        #     cursor.close()

    return render_template('login.html')

#Define route for register

# #################################################################################################################
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

# #################################################################################################################
@app.route('/register', methods=['GET', 'POST'])
def register():
     print("-------------------------------register------------------------------")
     return render_template("register.html")
# def register():
#     def check_email_exists(email, cursor):
#         query = """
#         SELECT 1 FROM customer WHERE email = %s
#         UNION
#         SELECT 1 FROM booking_agent WHERE email = %s
#         UNION
#         SELECT 1 FROM airline_staff WHERE email = %s
#         """
#         cursor.execute(query, (email, email, email))
#         return cursor.fetchone()

#     # try:
#     a = 1
#     if a==1 :
#         cursor = conn.cursor(dictionary=True)

#         cursor.execute("SELECT airline_name FROM airline")
#         airlines = cursor.fetchall()

#         if request.method == 'POST':
#             form_type = request.form.get('form_type')
#             # print(form_type)

#             existing_email_query = """
#                 SELECT 1 FROM customer WHERE email = %s
#                 UNION
#                 SELECT 1 FROM booking_agent WHERE email = %s
#                 UNION
#                 SELECT 1 FROM airline_staff WHERE email = %s
#                 """

#             if form_type == 'customer':
#                 customer_email = request.form.get('customer_email').lower().split('@')[0] + '@' + request.form.get('customer_email').lower().split('@')[1]
#                 customer_name = request.form.get('customer_name')
#                 customer_password = request.form.get('customer_password')
#                 customer_building_number = request.form.get('customer_building_number')
#                 customer_street = request.form.get('customer_street')
#                 customer_city = request.form.get('customer_city')
#                 customer_state = request.form.get('customer_state')
#                 customer_phone = request.form.get('customer_phone')
#                 customer_passport = request.form.get('customer_passport')
#                 customer_passport_expire = request.form.get('customer_passport_expire')
#                 customer_nationality = request.form.get('customer_nationality')
#                 customer_birthday = request.form.get('customer_birthday')
#                 # print(customer_email, customer_name, customer_password) 

#                 # 验证注册输入信息是否为空
#                 if not all([
#                     customer_email, customer_name, customer_password, 
#                     customer_building_number, customer_street, customer_city, 
#                     customer_state, customer_phone, customer_passport, 
#                     customer_passport_expire, customer_nationality, customer_birthday
#                 ]):
#                     flash('All fields are required!', 'danger')
#                     return redirect(url_for('register'))

#                 # 检查是否已存在用户
#                 if check_email_exists(customer_email, cursor):
#                     flash('Email already exists!', 'danger')
#                     return redirect(url_for('register'))

#                 # 对密码进行加密
#                 hashed_password = generate_password_hash(customer_password, method='pbkdf2:sha256')

#                 # 将用户数据插入数据库
#                 query = """
#                 INSERT INTO customer (
#                     email, name, password, building_number, street, city, state, phone_number, 
#                     passport_number, passport_expiration, passport_country, date_of_birth
#                 ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#                 """

#                 values = (customer_email, customer_name, hashed_password, customer_building_number, customer_street, customer_city, customer_state, customer_phone, customer_passport, customer_passport_expire, customer_nationality, customer_birthday)
#                 cursor.execute(query, values)
#                 conn.commit()
#                 cursor.close()

#                 flash('Registration successful! You can now log in.', 'success')
#                 return redirect(url_for('register'))  # 注册成功后重定向到主页或其他页面
            
#             elif form_type == 'agent':
#                 agent_email = request.form.get('agent_email').lower().split('@')[0] + '@' + request.form.get('agent_email').lower().split('@')[1]
#                 agent_password = request.form.get('agent_password')
#                 agent_id = request.form.get('agent_id')

#                 if not all([agent_email, agent_password, agent_id]):
#                     flash('All fields are required!', 'danger')
#                     return redirect(url_for('register'))
                
#                 if check_email_exists(agent_email, cursor):
#                     flash('Email already exists!', 'danger')
#                     return redirect(url_for('register'))
                
#                 # Check if agent_id already exists
#                 existing_agent_id_query = "SELECT 1 FROM booking_agent WHERE booking_agent_id = %s"
#                 cursor.execute(existing_agent_id_query, (agent_id,))
#                 existing_agent_id = cursor.fetchone()
#                 if existing_agent_id:
#                     flash('Agent ID already exists!', 'danger')
#                     return redirect(url_for('register'))

                
#                 hashed_password = generate_password_hash(agent_password, method='pbkdf2:sha256')
#                 query = """
#                     INSERT INTO booking_agent (
#                         email, password, booking_agent_id
#                     ) VALUES (%s, %s, %s)
#                     """
#                 values = (agent_email, hashed_password, agent_id)
#                 cursor.execute(query, values)
#                 conn.commit()
#                 cursor.close()

#                 flash('Booking Agent registration successful!', 'success')
#                 return redirect(url_for('register'))
            
#             elif form_type == 'staff':
#                 staff_email = request.form.get('staff_email').split('@')[0].lower()+ '@' + request.form.get('staff_email').lower().split('@')[1]
#                 staff_password = request.form.get('staff_password')
#                 staff_first_name = request.form.get('staff_first_name')
#                 staff_last_name = request.form.get('staff_last_name')
#                 staff_birthday = request.form.get('staff_birthday')
#                 staff_airline_name = request.form.get('staff_airline_name')
#                 # print(staff_airline_name)

#                 if not all([staff_email, staff_password, staff_first_name, staff_last_name, staff_birthday, staff_airline_name]):
#                     flash('All fields are required!', 'danger')
#                     return redirect(url_for('register'))
                
#                 if check_email_exists(staff_email, cursor):
#                     flash('Email already exists!', 'danger')
#                     return redirect(url_for('register'))
            
#                 hashed_password = generate_password_hash(staff_password, method='pbkdf2:sha256')
#                 query = """
#                     INSERT INTO airline_staff (
#                         email, password, first_name, last_name, date_of_birth, airline_name
#                     ) VALUES (%s, %s, %s, %s, %s, %s)
#                     """
#                 values = (staff_email, hashed_password, staff_first_name, staff_last_name, staff_birthday, staff_airline_name)
#                 cursor.execute(query, values)
#                 conn.commit()
#                 cursor.close()

#                 flash('Airline Staff registration successful!', 'success')
#                 return redirect(url_for('register'))
            
#     # except mysql.connector.Error as err:
#     #         print(f"Database error: {err}")
#     #         flash("Database error. Please try again later.", "error")
#     #         return redirect(url_for('register'))
#     # finally:
#     #     if conn.is_connected():
#     #         print('register-finally')
#     #         cursor.close()

#     return render_template('register.html',airlines=airlines)

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

# #################################################################################################################
@app.route('/home')
def home():
    username = session.get('username')
    if not username:
        return redirect(url_for('index'))
    # username = session['username']
    cursor = conn.cursor()
    query = "SELECT * FROM ticket WHERE customer = '{}' ORDER BY purchase_date DESC"
    cursor.execute(query.format(username))
    tickets = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=username, tickets=tickets)

	
# #################################################################################################################
# @app.route('/post', methods=['GET', 'POST'])
# def post():
# 	username = session['username']
# 	cursor = conn.cursor()
# 	blog = request.form['blog']
# 	query = "INSERT INTO blog (blog_post, username) VALUES('{}', '{}')"
# 	cursor.execute(query.format(blog, username))
# 	conn.commit()
# 	cursor.close()
# 	return redirect(url_for('home'))

# #################################################################################################################
@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')
# #################################################################################################################
@app.route('/about')
def about():
    return render_template('about.html')

# #################################################################################################################
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

#################################################################################################################
# @app.route('/search', methods=['GET'])
# def search_flights():
#     # 获取表单数据
#     departure_airport = request.args.get('from')
#     arrival_airport = request.args.get('to')
#     departure_date = request.args.get('date')
#     cursor = conn.cursor()
#     query = """
#         SELECT flight_num, airline_name, departure_time, arrival_time, departure_airport, arrival_airport, status
#         FROM flight 
#         WHERE departure_airport LIKE %s AND arrival_airport LIKE %s AND DATE(departure_time) = %s
#     """
#     cursor.execute(query, (f"%{departure_airport}%", f"%{arrival_airport}%", departure_date))
#     flights = cursor.fetchall()
#     cursor.close()
#     return render_template('search.html', flights=flights)
#     # 调用数据库查询函数（你需要实现这个函数来根据条件查询航班）
#     flights = get_flights(departure_airport, arrival_airport, departure_date)

#     return render_template('search.html', flights=flights)

# def get_flights(departure_airport, arrival_airport, departure_date):
#     # 这里根据你的数据库查询逻辑获取航班数据
#     # 伪代码：返回符合条件的航班数据列表
#     return [
#         {
#             'flight_num': 'AA123',
#             'airline_name': 'Air Freedom',
#             'departure_airport': departure_airport,
#             'departure_time': '2025-06-15 10:00',
#             'arrival_airport': arrival_airport,
#             'arrival_time': '2025-06-15 14:00',
#             'status': 'On-Time'
#         },
#         # 其他航班数据
#     ]







# app.secret_key = 'some key that you will never guess'
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

	