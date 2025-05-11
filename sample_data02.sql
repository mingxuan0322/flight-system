-- ============== 合并基础数据层 ============== --
-- 注意：使用 INSERT IGNORE 避免重复数据冲突 --
-- 执行顺序：airline -> airport -> airplane -> flight -> ticket -> purchases

-- ********** 航空公司数据 ********** --
INSERT IGNORE INTO airline (airline_name) VALUES
('Pacific Wings'),
('Euro Connect'),
('Demo Airlines'),
('Sky High Airways'),
('Japan Airlines'),
('Global Airways'),      -- 新增
('Asia Connect'),        -- 新增
('Atlantic Wings'),      -- 新增
('Polar Express'),       -- 新增
('Sahara Airways'),      -- 新增
('Nordic Connect'),      -- 新增
('Oceania Air');         -- 新增

-- ********** 机场数据 ********** --
INSERT IGNORE INTO airport (airport_name, airport_city) VALUES
-- 原有机场
('JFK', 'New York'),
('PVG', 'Shanghai'),
('LAX', 'Los Angeles'),
('HND', 'Tokyo'),
('LHR', 'London'),
('DXB', 'Dubai'),
-- 新增机场
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
('CPT', 'Cape Town');    -- 南非

-- ********** 飞机数据 ********** --
INSERT IGNORE INTO airplane (airline_name, airplane_id, seats) VALUES
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

-- ********** 航班数据（示例）********** --
INSERT IGNORE INTO flight (
  airline_name, flight_num, departure_airport, 
  departure_time, arrival_airport, arrival_time, 
  price, status, airplane_id
) VALUES
-- 原有航班
('Demo Airlines', 103, 'LAX', '2023-12-10 10:00:00', 'JFK', '2023-12-10 18:00:00', 350, 'on-time', 3),
('Euro Connect', 501, 'LHR', '2023-12-12 12:00:00', 'DXB', '2023-12-12 20:00:00', 950, 'delayed', 1),
-- 新增航班
('Global Airways', 101, 'SFO', '2024-03-15 22:00:00', 'CDG', '2024-03-16 10:00:00', 1899, 'on-time', 1),
('Polar Express', 201, 'HND', '2024-03-20 08:00:00', 'CPT', '2024-03-20 23:30:00', 3299, 'on-time', 1),
('Oceania Air', 301, 'SYD', '2024-04-01 09:00:00', 'SFO', '2024-04-01 04:00:00', 2899, 'on-time', 1);

-- ********** 票务数据（示例）********** --
INSERT IGNORE INTO ticket (ticket_id, airline_name, flight_num) VALUES
-- 原有票务
(10005, 'Demo Airlines', 103),
(10006, 'Demo Airlines', 103),
-- 新增票务
(30001, 'Global Airways', 101),
(30002, 'Global Airways', 101),
(30003, 'Polar Express', 201);

-- ********** 购买记录（示例）********** --
INSERT IGNORE INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date) VALUES
-- 原有记录
(10005, 'customer1@test.com', 2001, '2023-11-05'),
-- 新增记录
(30001, 'customer1@test.com', NULL, '2024-02-28'),
(30002, 'test02@customer.com', 2001, '2024-03-01');