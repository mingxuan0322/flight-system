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