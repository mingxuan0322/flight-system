air_ticket_flask/
├── app.py
├── templates/
│   └── flights.html
└── requirements.txt    #

airline → airline_staff, airplane, booking_agent_work_for, flight

airline_staff → permission

airplane, airport → flight

flight → ticket → purchases ← customer

booking_agent → booking_agent_work_for ← airline



### 📦 Entities & Relationships

#### airline
- `airline_name`: Primary key

#### airline_staff
- `username`: Primary key
- `password`: hashed (bcrypt)
- `airline_name`: FK → airline

#### permission
- Composite PK: (`username`, `permission_type`)
- `username`: FK → airline_staff

#### airplane
- Composite PK: (`airline_name`, `airplane_id`)
- `seats`: number of seats

#### airport
- `airport_name`: Primary key
- `airport_city`

#### booking_agent
- `email`: Primary key
- `password`: hashed (bcrypt)
- `booking_agent_id`: Unique

#### booking_agent_work_for
- Composite PK: (`email`, `airline_name`)
- FKs → booking_agent, airline

#### customer
- `email`: Primary key
- `password`: hashed (bcrypt)
- includes address, phone, passport details

#### flight
- Composite PK: (`airline_name`, `flight_num`)
- `status`: ENUM('on-time', 'delayed', 'cancelled')
- FKs → airport, airplane

#### ticket
- `ticket_id`: Primary key
- FK → flight

#### purchases
- Composite PK: (`ticket_id`, `customer_email`)
- FKs → ticket, customer
- `booking_agent_id`: optional reference to agent

---

## 🖥️ 页面结构与交互设计（简版）

### 登录页
- 用户类型选择（顾客 / 代理 / 员工）
- 提交至后端 `/login`，验证用户信息（bcrypt 比对）

### 注册页
- 对应用户类型注册
- 提交至 `/register`，写入加密密码和资料

### 航班搜索页
- 用户输入条件（出发地、目的地、时间）
- 前端调用 `/search_flights`，显示航班数据（返回 JSON）

### 购票页
- 用户选择航班并确认购买
- 前端提交至 `/purchase_ticket`
- 后端创建 `ticket`，插入到 `purchases`

### 员工权限管理页（airline_staff）
- 查看当前权限 / 分配新权限
- 前端调用 `/get_permissions`、`/add_permission`

---