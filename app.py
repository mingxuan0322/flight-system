from flask import Flask, render_template, request, url_for, flash, redirect, session
import mysql.connector
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps
import matplotlib.pyplot as plt
import io
import base64
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
                
            user = session['user']
            if user['identity'] != 'staff':
                flash("admin only", "danger")
                return redirect(url_for('home'))

            if permission and permission not in user.get('permissions', []):
                flash("Insufficient authority", "danger")
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
@app.route('/book/<airline_name>/<int:flight_num>', methods=['GET', 'POST'])
def book_flight(airline_name, flight_num):
    user = session.get('user')
    if not user or user['identity'] != 'customer':
        flash("Only customers can purchase tickets. Please log in.", "warning")
        return redirect(url_for('login'))

    customer_email = user['email']
    cursor = conn.cursor(dictionary=True)

    # 查询航班和剩余座位
    cursor.execute("""
        SELECT f.*, a.seats, COUNT(t.ticket_id) AS sold
        FROM flight f
        JOIN airplane a ON f.airline_name = a.airline_name AND f.airplane_id = a.airplane_id
        LEFT JOIN ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
        WHERE f.airline_name = %s AND f.flight_num = %s
        GROUP BY f.flight_num
    """, (airline_name, flight_num))
    flight = cursor.fetchone()

    if not flight:
        flash("Flight not found.", "danger")
        return redirect(url_for('search'))

    flight['remaining'] = flight['seats'] - flight['sold']

    # 是否已购买过
    cursor.execute("""
        SELECT COUNT(*) AS count FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        WHERE t.airline_name = %s AND t.flight_num = %s AND p.customer_email = %s
    """, (airline_name, flight_num, customer_email))
    has_bought = cursor.fetchone()['count'] > 0

    error = None  # <-- 初始化错误提示

    if request.method == 'POST':
        if flight['remaining'] < 1:
            error = "⚠️ No seats available on this flight."
        elif has_bought:
            error = "⚠️ You have already purchased this flight."
        else:
            try:
                cursor.execute("INSERT INTO ticket (airline_name, flight_num) VALUES (%s, %s)",
                               (airline_name, flight_num))
                ticket_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO purchases (ticket_id, customer_email, purchase_date)
                    VALUES (%s, %s, CURDATE())
                """, (ticket_id, customer_email))
                conn.commit()
                flash("✅ Ticket purchased successfully!", "success")
                return redirect(url_for('customer_dashboard'))
            except Exception as e:
                conn.rollback()
                error = f"❌ Error: {str(e)}"

    cursor.close()
    return render_template("book.html", flight=flight, has_bought=has_bought, error=error)

#ok#################################################################################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    user = session.get('user')
    if user:
        # 登录状态下重定向
        return redirect(url_for(f"{user['identity']}_dashboard"))

    if request.method == 'POST':
        identity = request.form.get('identity')
        email = request.form.get('username').lower().strip()
        password = request.form.get('password').strip()

        tables = {
            'customer': ('customer', 'email'),
            'agent': ('booking_agent', 'email'),
            'staff': ('airline_staff', 'username')
        }

        if identity not in tables:
            flash("Invalid role selected", "danger")
            return redirect(url_for('login'))

        table, id_field = tables[identity]
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(f"SELECT *, password AS hash FROM {table} WHERE {id_field} = %s", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['hash'], password):
                session_data = {
                    'email': user.get('email') or user['username'],
                    'identity': identity
                }

                if identity == 'agent':
                    session_data['agent_id'] = user['booking_agent_id']
                    cursor.execute("SELECT airline_name FROM booking_agent_work_for WHERE email = %s", (email,))
                    rows = cursor.fetchall()
                    session_data['airline_name'] = [r['airline_name'] for r in rows]

                elif identity == 'staff':
                    session_data['airline_name'] = user.get('airline_name')
                    cursor.execute("SELECT permission_type FROM permission WHERE username = %s", (email,))
                    perms = cursor.fetchall()
                    session_data['permissions'] = [p['permission_type'] for p in perms]

                session['user'] = session_data
                flash("Login successful!", "success")
                return redirect(url_for('home'))
            else:
                flash("Invalid credentials", "danger")

        except mysql.connector.Error as err:
            flash(f"Database error: {err.msg}", "danger")
        finally:
            cursor.close()

    return render_template('login.html')
   
# #################################################################################################################
@app.route('/customer')
def customer_dashboard():
    user = session.get('user')
    if not user or user['identity'] != 'customer':
        return redirect(url_for('login'))

    email = user['email']
    cursor = conn.cursor(dictionary=True)

    # 获取 upcoming flights
    cursor.execute("""
        SELECT f.*
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
        WHERE p.customer_email = %s AND f.departure_time > NOW()
        ORDER BY f.departure_time
    """, (email,))
    flights = cursor.fetchall()

    # 获取过去一年消费
    cursor.execute("""
        SELECT SUM(f.price) as total_spent
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
        WHERE p.customer_email = %s AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
    """, (email,))
    total_spent = cursor.fetchone()['total_spent'] or 0

    # 月度消费明细
    cursor.execute("""
        SELECT DATE_FORMAT(p.purchase_date, '%%Y-%%m') as month, SUM(f.price) as amount
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
        WHERE p.customer_email = %s AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
        GROUP BY month ORDER BY month
    """, (email,))
    monthly_data = cursor.fetchall()
    monthly_spending = {row['month']: float(row['amount']) for row in monthly_data}

    # 生成图像
    months = list(monthly_spending.keys())
    amounts = list(monthly_spending.values())

    plt.figure(figsize=(8, 4))
    plt.bar(months, amounts)
    plt.title('Monthly Spending (Last 6 Months)')
    plt.xlabel('Month')
    plt.ylabel('Amount ($)')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
    chart_url = f"data:image/png;base64,{chart_base64}"

    cursor.close()

    return render_template(
        'customer_home.html',
        user=user,
        flights=flights,
        total_spent=total_spent,
        monthly_spending=monthly_spending,
        spending_chart_url=chart_url
    )
    # return render_template("customer_home.html")

# @app.route('/agent')
# def agent_dashboard():
#     user=session.get('user')
#     if 'user' not in session or session['user'].get('identity') != 'agent':
#         flash("Access denied", "danger")
#         return redirect(url_for('login'))
#     return render_template("agent_home.html",user=user)

# @app.route('/agent', methods=['GET','Post'])
@app.route('/agent', methods=['GET'])
def agent_dashboard():
    if 'user' not in session or session['user'].get('identity') != 'agent':
        flash("Access denied", "danger")
        return redirect(url_for('login'))

    user = session['user']
    agent_id = user.get('agent_id')
    today = datetime.today().date()
    six_months_ago = today - timedelta(days=180)
    one_year_ago = today - timedelta(days=365)

    # 查询参数
    start = request.args.get('start')
    end = request.args.get('end')
    src = request.args.get('from')
    dst = request.args.get('to')

    # 处理航班过滤条件
    flight_conditions = ["p.booking_agent_id = %s"]
    flight_params = [agent_id]

    if start:
        flight_conditions.append("f.departure_time >= %s")
        flight_params.append(start)
    if end:
        flight_conditions.append("f.departure_time <= %s")
        flight_params.append(end)
    if src:
        flight_conditions.append("f.departure_airport LIKE %s")
        flight_params.append(f"%{src}%")
    if dst:
        flight_conditions.append("f.arrival_airport LIKE %s")
        flight_params.append(f"%{dst}%")

    flight_condition_str = " AND ".join(flight_conditions)

    cursor = conn.cursor(dictionary=True)

    # 🛫 获取为客户购买的航班
    cursor.execute(f"""
        SELECT f.flight_num, f.airline_name, f.departure_time, f.departure_airport,
               f.arrival_airport, p.customer_email
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
        WHERE {flight_condition_str}
        ORDER BY f.departure_time DESC
    """, tuple(flight_params))
    flights = cursor.fetchall()

    # 💰 获取佣金信息（默认过去30天）
    start_c = start or (today - timedelta(days=30)).isoformat()
    end_c = end or today.isoformat()

    cursor.execute("""
        SELECT 
            SUM(price * 0.1) AS total,
            AVG(price * 0.1) AS avg,
            COUNT(*) AS count
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
        WHERE p.booking_agent_id = %s
          AND p.purchase_date BETWEEN %s AND %s
    """, (agent_id, start_c, end_c))
    commission = cursor.fetchone() or {'total': 0, 'avg': 0, 'count': 0}

    # 🏆 Top 5 Customers by ticket count（过去6个月）
    cursor.execute("""
        SELECT customer_email, COUNT(*) AS tickets
        FROM purchases
        WHERE booking_agent_id = %s AND purchase_date >= %s
        GROUP BY customer_email
        ORDER BY tickets DESC
        LIMIT 5
    """, (agent_id, six_months_ago.isoformat()))
    top_ticket_customers = cursor.fetchall()

    # 🏆 Top 5 Customers by commission（过去12个月）
    cursor.execute("""
        SELECT customer_email, SUM(f.price * 0.1) AS total_commission
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
        WHERE p.booking_agent_id = %s AND p.purchase_date >= %s
        GROUP BY customer_email
        ORDER BY total_commission DESC
        LIMIT 5
    """, (agent_id, one_year_ago.isoformat()))
    top_commission_customers = cursor.fetchall()

    cursor.close()

    return render_template(
        'agent_home.html',
        user=user,
        flights=flights,
        commission=commission,
        top_ticket_customers=top_ticket_customers,
        top_commission_customers=top_commission_customers
    )

# @app.route('/staff')

# @app.route('/staff', methods=['GET', 'POST'])
# @require_permission()
@app.route('/staff', methods=['GET', 'POST'])
def staff_dashboard():
    if 'user' not in session or session['user'].get('identity') != 'staff':
        flash("Access denied", "danger")
        return redirect(url_for('login'))

    user = session['user']
    airline = user.get('airline_name')
    permissions = user.get('permissions', [])
    cursor = conn.cursor(dictionary=True)

    # 📦 处理表单提交
    if request.method == 'POST':
        form_type = request.form.get('form_name')

        try:
            if form_type == 'airport' and 'Admin' in permissions:
                cursor.execute("""
                    INSERT INTO airport (airport_name, airport_city)
                    VALUES (%s, %s)
                """, (request.form['airport_name'], request.form['city']))
                conn.commit()
                flash("机场添加成功", "success")

            elif form_type == 'airplane' and 'Admin' in permissions:
                cursor.execute("""
                    INSERT INTO airplane(airline_name, airplane_id, seats)
                    VALUES (%s,%s, %s)
                """, (airline, int(request.form['airplane_id']),int(request.form['seats'])))
                conn.commit()
                flash("飞机添加成功", "success")

            elif form_type == 'flight' and 'Admin' in permissions:
                cursor.execute("""
                    INSERT INTO flight 
                    (airline_name, flight_num, departure_airport, departure_time, 
                     arrival_airport, arrival_time, price, status, airplane_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    airline,
                    int(request.form['flight_num']),
                    request.form['departure_airport'],
                    request.form['departure_time'],
                    request.form['arrival_airport'],
                    request.form['arrival_time'],
                    float(request.form['price']),
                    request.form['status'],
                    int(request.form['airplane_id'])
                ))
                conn.commit()
                flash("航班创建成功", "success")

            elif form_type == 'grant' and 'Admin' in permissions:
                cursor.execute("""
                    INSERT INTO permission (username, permission_type)
                    VALUES (%s, %s)
                """, (request.form['username'], request.form['permission']))
                conn.commit()
                flash("权限授予成功", "success")

        except Exception as e:
            conn.rollback()
            flash(f"操作失败: {str(e)}", "danger")

    # ✈️ 航班数据
    start_date = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
    end_date = request.args.get('end', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
    cursor.execute("""
        SELECT f.*, COUNT(t.ticket_id) AS seats_sold
        FROM flight f
        LEFT JOIN ticket t USING(airline_name, flight_num)
        WHERE f.airline_name = %s AND f.departure_time BETWEEN %s AND %s
        GROUP BY f.flight_num
    """, (airline, start_date, end_date))
    flights = cursor.fetchall()

    # ✈️ 所有飞机
    cursor.execute("SELECT * FROM airplane WHERE airline_name = %s", (airline,))
    airplanes = cursor.fetchall()

    # 👤 员工列表（用于权限管理）
    cursor.execute("SELECT username FROM airline_staff WHERE airline_name = %s", (airline,))
    staff_list = cursor.fetchall()

    # 📈 销售报告（30天内）
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)

    cursor.execute("""
        SELECT SUM(price) AS total_revenue
        FROM ticket
        NATURAL JOIN purchases
        NATURAL JOIN flight
        WHERE airline_name = %s AND purchase_date BETWEEN %s AND %s
    """, (airline, thirty_days_ago, today))
    total_sales = cursor.fetchone()['total_revenue'] or 0

    cursor.execute("""
        SELECT booking_agent_id, SUM(price) AS revenue, COUNT(*) AS tickets
        FROM ticket
        NATURAL JOIN purchases
        NATURAL JOIN flight
        WHERE airline_name = %s AND purchase_date BETWEEN %s AND %s
              AND booking_agent_id IS NOT NULL
        GROUP BY booking_agent_id
        ORDER BY revenue DESC
        LIMIT 5
    """, (airline, thirty_days_ago, today))
    top_agents = cursor.fetchall()

    # 📍 热门目的地（过去30天按目的机场统计最多）
    cursor.execute("""
        SELECT arrival_airport, COUNT(*) AS total_flights
        FROM flight
        JOIN ticket USING(airline_name, flight_num)
        JOIN purchases USING(ticket_id)
        WHERE airline_name = %s AND purchase_date BETWEEN %s AND %s
        GROUP BY arrival_airport
        ORDER BY total_flights DESC
        LIMIT 5
    """, (airline, thirty_days_ago, today))
    top_destinations = cursor.fetchall()

    # 📅 月度销售（过去6个月）
    cursor.execute("""
        SELECT DATE_FORMAT(purchase_date, '%%Y-%%m') AS month, SUM(price) AS revenue
        FROM purchases
        JOIN ticket USING(ticket_id)
        JOIN flight USING(airline_name, flight_num)
        WHERE airline_name = %s AND purchase_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
        GROUP BY month
        ORDER BY month ASC
    """, (airline,))
    monthly_sales = cursor.fetchall()

    cursor.close()

    return render_template(
        "staff_home.html",
        permissions=permissions,
        airline=airline,
        flights=flights,
        airplanes=airplanes,
        staff_list=staff_list,
        top_destinations=top_destinations,
        monthly_sales=monthly_sales,
        total_sales=total_sales,
        top_agents=top_agents
    )

@app.route('/change_status', methods=['POST'])
@require_permission('Operator')
def change_status():
    airline_name = request.form.get('airline_name')
    flight_num = request.form.get('flight_num')
    new_status = request.form.get('new_status')

    allowed_status = {'on-time', 'delayed', 'in-progress', 'arrived'}

    if not airline_name or not flight_num or new_status not in allowed_status:
        flash("Invalid status update request", "danger")
        return redirect(url_for('staff_dashboard'))

    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE flight
            SET status = %s
            WHERE airline_name = %s AND flight_num = %s
        """, (new_status, airline_name, flight_num))
        conn.commit()
        flash(f"Flight #{flight_num} status updated to '{new_status}'", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Failed to update status: {e}", "danger")
    finally:
        cursor.close()

    return redirect(url_for('staff_dashboard'))

# @app.route('/staff/grant_permission', methods=['POST'])
# @require_permission('Admin')
# def grant_permission():
#     username = request.form['username'].strip()
#     permission = request.form['permission']

#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             INSERT IGNORE INTO permission (username, permission_type)
#             VALUES (%s, %s)
#         """, (username, permission))
#         conn.commit()
#         flash(f"Granted {permission} to {username}", "success")
#     except Exception as e:
#         conn.rollback()
#         flash(f"Error: {str(e)}", "danger")
#     finally:
#         cursor.close()

#     return redirect(url_for('staff_dashboard'))

# # 添加机场路由
# @app.route('/staff/add_airport', methods=['GET', 'POST'])
# @require_permission('Admin')
# def add_airport():
#     if request.method == 'POST':
#         airport_name = request.form['airport_name'].strip()
#         city = request.form['city'].strip()
        
#         try:
#             cursor = conn.cursor()
#             cursor.execute("""
#                 INSERT INTO airport (airport_name, airport_city)
#                 VALUES (%s, %s)
#             """, (airport_name, city))
#             conn.commit()
#             flash(f"机场 {airport_name} 添加成功", "success")
#         except mysql.connector.IntegrityError:
#             conn.rollback()
#             flash("机场已存在", "danger")
#         except Exception as e:
#             conn.rollback()
#             flash(f"数据库错误: {str(e)}", "danger")
#         finally:
#             cursor.close()
#         return redirect(url_for('staff_dashboard'))

#     return render_template('staff_add_airport.html')



# @app.route('/staff/add_airplane', methods=['POST'])
# @require_permission('Admin')
# def staff_add_airplane():
#     if 'user' not in session or session['user'].get('identity') != 'staff':
#         flash("Access denied", "danger")
#         return redirect(url_for('login'))
    
#     return

# # 员工查看航班
# @app.route('/staff/flights')
# @require_permission()
# def staff_view_flights():
#     if 'user' not in session or session['user'].get('identity') != 'staff':
#         flash("Access denied", "danger")
#         return redirect(url_for('login'))
#     # 获取查询参数
#     start_date = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
#     end_date = request.args.get('end', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
    
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("""
#         SELECT f.*, COUNT(t.ticket_id) AS seats_sold
#         FROM flight f
#         LEFT JOIN ticket t USING(airline_name, flight_num)
#         WHERE f.airline_name = %s
#           AND f.departure_time BETWEEN %s AND %s
#         GROUP BY f.flight_num
#     """, (airline, start_date, end_date))
    
#     flights = cursor.fetchall()
#     cursor.close()
#     return render_template('staff_flights.html', flights=flights)

# 其他功能按类似模式实现...
# #################################################################################################################

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

	