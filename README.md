### Test Info
'test01@customer.com'
'test02@customer.com'
'customer1@test.com'
'customer2@test.com'

### Booking Agent
('euro_agent@test.com', 'test123', 2001),
('asia_agent@test.com', 'test123', 3001),
('agent02@test.com','test123',1001),
('agent01@test.com','test123',4001);

### Airline Staff
('euro_admin@test.com', 'Euro Connect'),
('pacific_ops@test.com', 'Pacific Wings');
('staff01@test.com', 'Euro Connect'),
('staff02@test.com', 'Pacific Wings');

### Airports
('JFK', 'New York'),
('PVG', 'Shanghai'),
('LAX', 'Los Angeles'),
('HND', 'Tokyo'),
('LHR', 'London'),
('DXB', 'Dubai'),
('SFO', 'San Francisco'),
('CDG', 'Paris'),
('SIN', 'Singapore'),
('AMS', 'Amsterdam'),    -- 荷兰
('ICN', 'Seoul'),        -- 韩国
('SYD', 'Sydney'),       -- 澳大利亚
('DEL', 'Delhi'),        -- 印度
('IST', 'Istanbul'),     -- 土耳其
('GRU', 'São Paulo'),    -- 巴西
('MEX', 'Mexico City'),  -- 墨西哥
('CPT', 'Cape Town');  

### airplane
-- 原有飞机
('Demo Airlines', 1, 150),
('Demo Airlines', 2, 200),
('Demo Airlines', 3, 5),
('Sky High Airways', 101, 180),
('Euro Connect', 1, 200),
('Pacific Wings', 1, 180),
-- 新增飞机
('Global Airways', 1, 250),   -- 宽体客机
('Global Airways', 2, 300),   
('Asia Connect', 1, 220),     
('Japan Airlines', 1, 280),   -- 补充日航飞机
('Atlantic Wings', 1, 412),   -- A380
('Polar Express', 1, 368),     -- 波音777-300ER
('Oceania Air', 1, 329),       -- A350-1000
('Sahara Airways', 1, 189),    -- 波音737 MAX 8
('Nordic Connect', 1, 174);    -- A320neo

### flight

('Demo Airlines', 103, 'LAX', '2023-12-10 10:00:00', 'JFK', '2023-12-10 18:00:00', 350, 'on-time', 3),
('Euro Connect', 501, 'LHR', '2023-12-12 12:00:00', 'DXB', '2023-12-12 20:00:00', 950, 'delayed', 1),
-- 新增航班
('Global Airways', 101, 'SFO', '2024-03-15 22:00:00', 'CDG', '2024-03-16 10:00:00', 1899, 'on-time', 1),
('Polar Express', 201, 'HND', '2024-03-20 08:00:00', 'CPT', '2024-03-20 23:30:00', 3299, 'on-time', 1),
('Oceania Air', 301, 'SYD', '2024-04-01 09:00:00', 'SFO', '2024-04-01 04:00:00', 2899, 'on-time', 1);

### ticket
(10005, 'Demo Airlines', 103),
(10006, 'Demo Airlines', 103),
-- 新增票务
(30001, 'Global Airways', 101),
(30002, 'Global Airways', 101),
(30003, 'Polar Express', 201);


### purchase
(10005, 'customer1@test.com', 2001, '2023-11-05'),
-- 新增记录
(30001, 'customer1@test.com', NULL, '2024-02-28'),
(30002, 'test02@customer.com', 2001, '2024-03-01');



### staff
('euro_admin@test.com', '$2b$12$euroadm...', 'Hans', 'Schmidt', '1985-05-05', 'Euro Connect'),
('pacific_ops@test.com', '$2b$12$pacops...', 'Yuki', 'Tanaka', '1990-11-11', 'Pacific Wings');
('staff01@test.com', 'test123', 'Hans', 'Schmidt', '1985-05-05', 'Euro Connect'),
('staff02@test.com', 'test123', 'Yuki', 'Tanaka', '1990-11-11', 'Pacific Wings');

### ad
('euro_admin@test.com', 'Admin'),
('pacific_ops@test.com', 'Operator');
### functions

1. View Public Info
    ``` Search for upcoming flights ```
    ``` ***see the flights status ```
2. Login: 3 types of user login
3. Register: 3 types of user registrations (Customer, Booking agent, Airline Staff) option via forms.



### Entities & Relationships

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