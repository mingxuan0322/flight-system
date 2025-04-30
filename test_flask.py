from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'key'  # 建议启用 Session 管理
print("----initiated----")

conn = mysql.connector.connect(
    # host='localhost',
    host='127.0.0.1',
    user='root',             # XAMPP 默认用户名通常为 root
    password='',             # 若你设置了密码，则修改为相应密码
    database='airticket',
    port=3306   # 使用刚才创建的数据库名称
)

print('----configured----')

@app.route('/')
def index():
    # 主页可以根据登录状态进行不同显示。这里简单跳转到航班列表
    print("----index page----")
    return redirect(url_for('upcoming_flights'))
    # return render_template('flights.html')

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
        flights = cursor.fetchall()
    except Exception as e:
        print("查询错误：", e)
        flights = []
    finally:
        cursor.close()
    return render_template('flights.html', flights=flights)

if __name__ == "__main__":
    print(">>> Flask is starting...")
    try:
        app.run(host='127.0.0.1', port=5000, debug=True)
    except Exception as e:
        print(">>> ERROR:", e)
