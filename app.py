from flask import Flask, render_template, request, url_for, flash, redirect, session
import mysql.connector
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps

import hashlib 
from werkzeug.security import generate_password_hash, check_password_hash

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

def require_permission(permission=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))
                
            user_type = session['user']['identity']
            
            # 员工权限检查
            if user_type == 'staff' and permission:
                if permission not in session['user'].get('permissions', []):
                    flash("Insufficient permissions", "danger")
                    return redirect(url_for('staff_dashboard'))
            
            return f(*args, **kwargs)
        return wrapped
    return decorator
# # airticket/
# # │
# # ├── index.html             // 首页
# # ├── login.html             // 登录页面
# # ├── register.html          // 注册页面
# # ├── home.html          // 
# # ├── customer_home.html     // 客户主页
# # ├── agent_home.html        // 代理主页
# # ├── staff_home.html        // 航空公司工作人员主页
# # │
# # ├── static/
# # │   └── css/
# # │       └── style.css
# # │
# # └── js/
# #     └── main.js            // 用于未来交互的JS


#Define a route to hello function
# ok#################################################################################################################

@app.route('/')
def hello():
    # username = session.get('username')  # ✅ 如果没登录会返回 None，不报错
    user = session.get('user')
    username = session.get('username')
    # print("----------------Hello------------")

    # if not username:
    #     print("----------------index------------")

    #     return redirect(url_for('search'))
    print("----------------homepage------------")

    if user and user['identity'] == 'customer':
        return redirect(url_for('customer_dashboard'))
    elif user and user['identity'] == 'agent':
        return redirect(url_for('agent_dashboard'))
    elif user and user['identity'] == 'staff':
        return redirect(url_for('staff_dashboard'))
    else:
        print("----------------index------------")
        return redirect(url_for('search'))
    
# ok#################################################################################################################
@app.route('/index', methods=['GET'])
# def search():
def search():
    flights = []  # ✅ 初始化为默认空列表
    departure_airport = request.args.get('from', '').strip()
    arrival_airport = request.args.get('to', '').strip()
    departure_date = request.args.get('date', '').strip()

    if not departure_airport and not arrival_airport and not departure_date:
        flash("Please fill at least one search field", "danger")
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

        # print("-------查询结果数量:", len(flights))
        # print("-------SQL:", query)
        # print("-------Params:", params)

    except Exception as e:
        flash("查询失败，请检查搜索条件或稍后重试", "danger")
        print("查询错误:", e)
        flights = []

    finally:
        print(flights)
        print("flights 类型：", type(flights))
        print("flights 内容：", flights)


        cursor.close()
    user = session.get('user') 
    identity=user['identity'] if user else ''
    return render_template('index.html', flights=flights,user=user,identity=identity)
    # return render_template('index.html', flights=flights,username=session.get('username'))

# #################################################################################################################
@app.route('/book/<airline_name>/<int:flight_num>')
# @app.route('/book')
def book_flight(airline_name, flight_num):
    # 实现订票逻辑
    print('-----------------',airline_name,flight_num)
    return f"Booking page for flight {airline_name} #{flight_num}"
    # return redirect(url_for('home'))

#ok#################################################################################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    user = session.get('user')
    print("----------------login------------")

    if user and user['identity'] == 'customer':
        return redirect(url_for('customer_dashboard'))
    elif user and user['identity'] == 'agent':
        return redirect(url_for('agent_dashboard'))
    elif user and user['identity'] == 'staff':
        return redirect(url_for('staff_dashboard'))

    if request.method == 'POST':
        #get what user input in the login page
        identity = request.form.get('identity')
        email = request.form.get('username').lower().strip()
        # email = request.form.get('login_email').lower().split('@')[0] + '@' + request.form.get('login_email').split('@')[1]
        password = request.form.get('password').strip()  #这里get到的密码应该是输入进去什么就是什么，输入1这里就是1
        
        print(identity, email, password)

        #通过identity定位我从哪个table里面查找我的用户 & agent中时username而不是email
        tables = {
            'customer': ('customer', 'email'),
            'agent': ('booking_agent', 'email'),
            'staff': ('airline_staff', 'username')
        }
        if identity not in tables:
            flash("Invalid role selected", "danger")
            return redirect(url_for('login'), error="Invalid role")
            # return render_template("login.html", error="Invalid role")

        table,id_field  = tables[identity]
        cursor = conn.cursor(dictionary=True)
        try:
            # 获取用户记录
            cursor.execute(f"""
                SELECT *, password AS hash 
                FROM {table} 
                WHERE {id_field} = %s
            """, (email,))
            user = cursor.fetchone()

            # 验证密码
            if user and check_password_hash(user['hash'], password):
                session['user'] = {
                    'email': user.get('email') or user['username'],
                    'identity': identity,
                }
                flash("Login successful!", "success")
                return redirect(url_for('home'))
            else:
                flash("Invalid credentials", "danger")
                
        except mysql.connector.Error as err:
            flash(f"Database error: {err.msg}", "danger")
        finally:
            cursor.close()

    return render_template('login.html')    
    #     query = f"SELECT * FROM {table} WHERE email = %s"
    #     cursor.execute(query, (email,))
    #     # cursor.execute(f"SELECT * FROM {table} WHERE email = %s", (email,))
    #     user = cursor.fetchone()
    #     cursor.close()
    #     print('----------------user', user,password)

    #     # if user and check_password_hash(user['password'], password):
    #     #     session['user'] = {
    #     #         'email': user['email'],
    #     #         'identity': identity
    #     #     }


    #     if user and check_password_hash(user['password'], password):
    #         print('----------------------------------------')
    #         session['user'] = {
    #             'email': user['email'],
    #             'identity': identity
    #         }

    #         #######################################
    #         where=session.get('action')
    #         airline=session.get('airline_name')
    #         flight=session.get('flight_num')
    #         if where == 'book':
    #             return redirect(url_for(book_flight,),airline_name=airline,flight_num=flight)


    #         flash("Login successful!", "success")
    #         print(f"Redirecting to {identity}_dashboard test")

    #         if identity == 'customer':
    #             print(f"Redirecting to {identity}_dashboard")
    #             return redirect(url_for('customer_dashboard'))
    #             # print(f"Redirecting to {identity}_dashboard")
    #         elif identity == 'agent':
    #             session['user']['agent_id'] = user['booking_agent_id']
    #             print(session)
    #             print(f"Redirecting to {identity}_dashboard")
    #             return redirect(url_for('agent_dashboard'))
    #         elif identity == 'staff':
    #             session['user']['airline_name'] = user['airline_name']
    #             cursor.execute("SELECT permission_type FROM permission WHERE email = %s", (email,))
    #             permissions = cursor.fetchall()
    #             # print("permission get from database",permissions)

    #             if permissions:
    #                 # 提取权限类型的值
    #                 session['user']['permissions'] = [permission['permission_type'] for permission in permissions]
    #             else:
    #                 session['user']['permissions'] = []  # 没有权限时为空列表
    #             # print("permissions after processing:", session['user']['permissions'])   
                             
    #             # 权限为空 设置一个默认值
    #             if not session['user']['permissions']:
    #                 session['user']['permissions'] = ['None']
    
    #             print(session)
    #             print(f"Redirecting to {identity}_dashboard")

    #             return redirect(url_for('staff_dashboard'))
    #     else:
    #         # 登录失败
    #         flash("Invalid email or password. Please try again.", "error")
    #         return redirect(url_for('login'))
        
    #     # except mysql.connector.Error as err:
    #     #     print(f"Database error: {err}")
    #     #     flash("Database error. Please try again later.", "error")
    #     #     return redirect(url_for('login'))
    #     # finally:
    #     #     print('login-finally')
    #     #     cursor.close()

    # # return render_template('login.html')
# #################################################################################################################
@app.route('/customer')
def customer_dashboard():
    if 'user' not in session or session['user'].get('identity') != 'customer':
        flash("Access denied", "danger")
        return redirect(url_for('login'))

    email = session['user']['email']
    cursor = conn.cursor(dictionary=True)

    # 获取未来的航班
    cursor.execute("""
        SELECT f.flight_num, f.airline_name, f.departure_time, f.arrival_time, f.status
        FROM flight f
        JOIN ticket t ON f.flight_num = t.flight_num AND f.airline_name = t.airline_name
        JOIN purchases p ON t.ticket_id = p.ticket_id
        WHERE p.customer_email = %s AND f.departure_time >= NOW()
        ORDER BY f.departure_time ASC
    """, (email,))
    flights = cursor.fetchall()

    # 增加日期范围查询参数
    start_date = request.args.get('start', (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
    # 获取过去一年的总消费 & 按月消费
    one_year_ago = datetime.now() - timedelta(days=365)
    cursor.execute("""
        SELECT 
            SUM(f.price) AS total,
            DATE_FORMAT(p.purchase_date, '%%Y-%%m') AS month,
            COUNT(*) AS tickets
        FROM purchases p
        JOIN ticket t USING(ticket_id)
        JOIN flight f USING(airline_name, flight_num)
        WHERE p.customer_email = %s
          AND p.purchase_date BETWEEN %s AND %s
        GROUP BY month
        ORDER BY month
    """, (email, start_date, end_date))
    # spending_data = cursor.fetchall()
    purchases = cursor.fetchall()
    total_spent = sum([float(p['price']) for p in purchases])

    monthly_spending = defaultdict(float)
    for p in purchases:
        month = p['purchase_date'].strftime('%Y-%m')
        monthly_spending[month] += float(p['price'])

    cursor.execute("SELECT name FROM customer WHERE email = %s", (email,))
    customer = cursor.fetchone()

    cursor.close()

    return render_template(
        'customer_home.html',
        user=customer,
        flights=flights,
        total_spent=round(total_spent, 2),
        monthly_spending=dict(monthly_spending)
    )

    # return render_template("customer_home.html")

@app.route('/agent')
def agent_dashboard():
    if 'user' not in session or session['user'].get('identity') != 'agent':
        flash("Access denied", "danger")
        return redirect(url_for('login'))
    return render_template("agent_home.html")


@app.route('/staff')
def staff_dashboard():
    if 'user' not in session or session['user'].get('identity') != 'staff':
        flash("Access denied", "danger")
        return redirect(url_for('login'))
    

    return render_template("staff_home.html")


@app.route('/staff/add_airplane', methods=['POST'])
@require_permission('Admin')
def staff_add_airplane():
    if 'user' not in session or session['user'].get('identity') != 'staff':
        flash("Access denied", "danger")
        return redirect(url_for('login'))
    
    return

# 员工查看航班
@app.route('/staff/flights')
@require_permission()
def staff_view_flights():
    if 'user' not in session or session['user'].get('identity') != 'staff':
        flash("Access denied", "danger")
        return redirect(url_for('login'))
    # 获取查询参数
    start_date = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
    end_date = request.args.get('end', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.*, COUNT(t.ticket_id) AS seats_sold
        FROM flight f
        LEFT JOIN ticket t USING(airline_name, flight_num)
        WHERE f.airline_name = %s
          AND f.departure_time BETWEEN %s AND %s
        GROUP BY f.flight_num
    """, (airline, start_date, end_date))
    
    flights = cursor.fetchall()
    cursor.close()
    return render_template('staff_flights.html', flights=flights)

# 其他功能按类似模式实现...
# #################################################################################################################

@app.route('/purchase/<airline_name>/<int:flight_num>', methods=['POST'])
def purchase_flight(airline_name, flight_num):
    if 'user' not in session or session['user'].get('identity') != 'staff':
        flash("Access denied", "danger")
        return redirect(url_for('login'))
    
    user_type = session['user']['identity']
    customer_email = None
    agent_id = None
    
    if user_type == 'customer':
        customer_email = session['user']['email']
    elif user_type == 'agent':
        agent_id = session['user']['agent_id']
        customer_email = request.form.get('customer_email')  # 需要验证客户是否存在
    else:
        flash("Staff cannot purchase tickets", "danger")
        return redirect(url_for('home'))

    try:
        cursor = conn.cursor()
        # 开始事务
        cursor.execute("START TRANSACTION")
        
        # 1. 获取飞机座位数
        cursor.execute("""
            SELECT a.seats - COUNT(t.ticket_id) AS remaining
            FROM airplane a
            LEFT JOIN flight f USING(airline_name, airplane_id)
            LEFT JOIN ticket t USING(airline_name, flight_num)
            WHERE f.airline_name = %s AND f.flight_num = %s
            GROUP BY a.airplane_id
            FOR UPDATE
        """, (airline_name, flight_num))
        remaining = cursor.fetchone()[0]
        
        if remaining < 1:
            raise Exception("No seats available")

        # 2. 生成票号（假设使用自增ID）
        cursor.execute("INSERT INTO ticket (airline_name, flight_num) VALUES (%s, %s)",
                     (airline_name, flight_num))
        ticket_id = cursor.lastrowid

        # 3. 记录购买
        cursor.execute("""
            INSERT INTO purchases 
            (ticket_id, customer_email, booking_agent_id, purchase_date)
            VALUES (%s, %s, %s, CURDATE())
        """, (ticket_id, customer_email, agent_id))
        
        conn.commit()
        flash("Purchase successful!", "success")
    
    except Exception as e:
        conn.rollback()
        flash(f"Purchase failed: {str(e)}", "danger")
    finally:
        cursor.close()
    
    return redirect(url_for('customer_dashboard' if user_type == 'customer' else 'agent_dashboard'))
#Define route for purchase that allow user and agent finish the process

# #################################################################################################################
#Authenticates the login
# @app.route('/loginAuth', methods=['GET', 'POST'])
# def loginAuth():
# 	#grabs information from the forms
# 	username = request.form['username']
# 	password = request.form['password']

# 	#cursor used to send queries
# 	cursor = conn.cursor()
# 	#executes query
# 	query = "SELECT * FROM user WHERE username = '{}' and password = '{}'"
# 	cursor.execute(query.format(username, password))
# 	#stores the results in a variable
# 	data = cursor.fetchone()
# 	#use fetchall() if you are expecting more than 1 data row
# 	cursor.close()
# 	error = None
# 	if(data):
# 		#creates a session for the the user
# 		#session is a built in
# 		session['username'] = username
# 		return redirect(url_for('home'))
# 	else:
# 		#returns an error message to the html page
# 		error = 'Invalid login or username'
# 		return render_template('login.html', error=error)
##################helper#############################
def validate_email(email):
    return '@' in email and len(email) >= 5

def user_exists(email, cursor):
    cursor.execute("""
        SELECT email FROM (
            SELECT email FROM customer
            UNION ALL
            SELECT email FROM booking_agent
            UNION ALL
            SELECT username FROM airline_staff
        ) AS all_emails
        WHERE email = %s
    """, (email,))
    return cursor.fetchone() is not None

def handle_customer_registration(cursor, email, hashed_pw, form):
    required_fields = ['name', 'phone', 'passport']
    if not all(form.get(field) for field in required_fields):
        flash("Missing required customer fields", "danger")
        raise ValueError("Incomplete customer data")

    cursor.execute("""
        INSERT INTO customer (
            email, name, password, phone_number, passport_number,
            building_number, street, city, state, 
            passport_expiration, passport_country, date_of_birth
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        email,
        form['name'],
        hashed_pw,
        form['phone'],
        form['passport'],
        form.get('building', ''),
        form.get('street', ''),
        form.get('city', ''),
        form.get('state', ''),
        form.get('passport_expire', '2025-01-01'),  # 示例默认值
        form.get('country', ''),
        form.get('dob', '2000-01-01')
    ))

def handle_agent_registration(cursor, email, hashed_pw, form):
    agent_id = form.get('agent_id')
    if not agent_id:
        flash("Agent ID required", "danger")
        raise ValueError("Missing agent ID")

    # 检查代理ID唯一性
    cursor.execute("SELECT 1 FROM booking_agent WHERE booking_agent_id = %s", (agent_id,))
    if cursor.fetchone():
        flash("Agent ID already exists", "danger")
        raise ValueError("Duplicate agent ID")

    cursor.execute("""
        INSERT INTO booking_agent (email, password, booking_agent_id)
        VALUES (%s, %s, %s)
    """, (email, hashed_pw, agent_id))

def handle_staff_registration(cursor, email, hashed_pw, form, airlines):
    required_fields = ['first_name', 'last_name', 'airline']
    if not all(form.get(field) for field in required_fields):
        flash("Missing required staff fields", "danger")
        raise ValueError("Incomplete staff data")

    if form['airline'] not in airlines:
        flash("Invalid airline selection", "danger")
        raise ValueError("Invalid airline")

    # 插入员工数据
    cursor.execute("""
        INSERT INTO airline_staff (
            username, password, first_name, last_name,
            date_of_birth, airline_name
        ) VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        email,
        hashed_pw,
        form['first_name'],
        form['last_name'],
        form.get('dob', '1990-01-01'),
        form['airline']
    ))

    # 处理权限
    permissions = form.getlist('permissions')
    if permissions:
        cursor.executemany("""
            INSERT INTO permission (username, permission_type)
            VALUES (%s, %s)
        """, [(email, perm) for perm in permissions])
# #################################################################################################################
@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 获取航空公司列表
        cursor.execute("SELECT airline_name FROM airline")
        airlines = [row['airline_name'] for row in cursor.fetchall()]
        
        if request.method == 'POST':
            form_type = request.form.get('form_type')
            email = request.form.get('email', '').lower().strip()
            password = request.form.get('password', '').strip()

            # 基础验证
            if not validate_email(email):
                flash("Invalid email format", "danger")
                return redirect(url_for('register'))
                
            if len(password) < 6:
                flash("Password must be at least 6 characters", "danger")
                return redirect(url_for('register'))

            # 检查邮箱唯一性
            if user_exists(email, cursor):
                flash("Email already registered", "danger")
                return redirect(url_for('register'))

            # 密码哈希处理
            hashed_pw = generate_password_hash(password)

            # 处理不同用户类型
            if form_type == 'customer':
                handle_customer_registration(cursor, email, hashed_pw, request.form)
            elif form_type == 'agent':
                handle_agent_registration(cursor, email, hashed_pw, request.form)
            elif form_type == 'staff':
                handle_staff_registration(cursor, email, hashed_pw, request.form, airlines)
            else:
                flash("Invalid user type", "danger")
                return redirect(url_for('register'))

            conn.commit()
            flash("Registration successful!", "success")
            return redirect(url_for('login'))

    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Database error: {err.msg}", "danger")
    finally:
        cursor.close()
    
    return render_template('register.html', airlines=airlines)

# #################################################################################################################
@app.route('/home')
def home():
    user = session.get('user')
    if user['identity'] == 'customer':
        return redirect(url_for('customer_dashboard'))
    elif user['identity'] == 'agent':
        return redirect(url_for('agent_dashboard'))
    elif user['identity'] == 'staff':
        return redirect(url_for('staff_dashboard'))
    elif not user:
        ##回到上一个界面
        return redirect(url_for('index'))

    # if not username:
    #     return redirect(url_for('index'))
    # # username = session['username']
    # cursor = conn.cursor()
    # query = "SELECT * FROM ticket WHERE customer = '{}' ORDER BY purchase_date DESC"
    # cursor.execute(query.format(username))
    # tickets = cursor.fetchall()
    # cursor.close()
    # return render_template('home.html', username=username, tickets=tickets)

	
# #################################################################################################################
# from markupsafe import Markup  # 放在文件顶部

# @app.route('/rehash-all-passwords')
# def rehash_all_passwords():
#     cursor = conn.cursor(dictionary=True)
#     result_log = ""

#     tables = {
#         "customer": "email",
#         "booking_agent": "email",
#         "airline_staff": "username"
#     }

#     for table, email_field in tables.items():
#         try:
#             cursor.execute(f"SELECT {email_field}, password FROM {table}")
#             users = cursor.fetchall()

#             if not users:
#                 result_log += f"🛑 No users in table `{table}`.<br>"
#                 continue

#             for user in users:
#                 email = user[email_field]
#                 password = 'test123'

#                 # 强制重新哈希为 pbkdf2:sha256
#                 if password.startswith("pbkdf2:sha256:"):
#                     result_log += f"🔒 {table} | {email} already hashed.<br>"
#                     continue

#                 new_hashed = generate_password_hash(password, method='pbkdf2:sha256')
#                 cursor.execute(
#                     f"UPDATE {table} SET password = %s WHERE {email_field} = %s",
#                     (new_hashed, email)
#                 )
#                 result_log += f"✅ {table} | {email} rehashed to pbkdf2.<br>"

#         except Exception as e:
#             result_log += f"❌ Error in {table}: {e}<br>"

#     conn.commit()
#     cursor.close()
#     return Markup(result_log) or "Nothing processed."

# #################################################################################################################
@app.route('/logout')
def logout():
	session.pop('user')
	return redirect('/')
# #################################################################################################################
@app.route('/about')
def about():
    return render_template('about.html')

# #################################################################################################################
# @app.route('/upcoming-flights')
# def upcoming_flights():
#     print("----flight page----")

#     # 利用 mysql.connector 获取数据库游标，设置 dictionary=True 以字典形式返回数据
#     cursor = conn.cursor(dictionary=True)
#     try:
#         # 根据 flight 表中 departure_time 过滤出当前时间之后的航班信息
#         query = """
#             SELECT airline_name, flight_num, departure_airport, departure_time, 
#                    arrival_airport, arrival_time, status 
#             FROM flight 
#             WHERE departure_time >= %s 
#             ORDER BY departure_time ASC
#         """
#         cursor.execute(query, (datetime.now(),))
#         # conn.commit()

#         flights = cursor.fetchall()
#     except Exception as e:
#         print("查询错误：", e)
#         flights = []
#     finally:
# 	    # conn.commit()
#         cursor.close()
#     return render_template('flights.html', flights=flights)


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

	