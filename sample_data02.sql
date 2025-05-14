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
('Oceania Air', 301, 'SYD', '2024-04-01 09:00:00', 'SFO', '2024-04-01 04:00:00', 2899, 'on-time', 1),
-- INSERT INTO flight VALUES
('Polar Express', 1000, 'CPT', '2025-06-12 12:00:00', 'MEX', '2025-06-12 21:00:00', 678, 'on-time', 1),
('Demo Airlines', 1001, 'SIN', '2025-05-30 15:00:00', 'MEX', '2025-05-30 23:00:00', 1948, 'delayed', 1),
('Demo Airlines', 1002, 'SYD', '2025-06-29 16:00:00', 'HND', '2025-06-30 03:00:00', 1830, 'cancelled', 1),
('Euro Connect', 1003, 'IST', '2025-06-19 06:00:00', 'DEL', '2025-06-19 13:00:00', 882, 'on-time', 1),
('Pacific Wings', 1004, 'DXB', '2025-07-01 11:00:00', 'CDG', '2025-07-01 20:00:00', 1050, 'on-time', 1),
('Demo Airlines', 1005, 'ICN', '2025-06-18 10:00:00', 'SFO', '2025-06-18 18:00:00', 1280, 'on-time', 1),
('Demo Airlines', 1006, 'CDG', '2025-06-20 07:00:00', 'ICN', '2025-06-20 15:00:00', 1340, 'on-time', 1),
('Polar Express', 1007, 'SFO', '2025-06-24 09:00:00', 'AMS', '2025-06-24 18:00:00', 1570, 'on-time', 1),
('Polar Express', 1008, 'MEX', '2025-05-27 05:00:00', 'IST', '2025-05-27 14:00:00', 920, 'on-time', 1),
('Pacific Wings', 1009, 'SYD', '2025-06-05 12:00:00', 'LAX', '2025-06-05 22:00:00', 1100, 'on-time', 1),
('Euro Connect', 1010, 'LHR', '2025-07-05 16:00:00', 'JFK', '2025-07-05 22:00:00', 1120, 'on-time', 1),
('Pacific Wings', 1011, 'DEL', '2025-07-06 09:00:00', 'IST', '2025-07-06 17:00:00', 799, 'delayed', 1),
('Demo Airlines', 1012, 'MEX', '2025-05-14 14:00:00', 'LHR', '2025-05-15 00:00:00', 1720, 'on-time', 1),
('Polar Express', 1013, 'GRU', '2025-07-10 20:00:00', 'SYD', '2025-07-11 08:00:00', 2100, 'on-time', 1),
('Polar Express', 1014, 'CDG', '2025-05-31 09:00:00', 'HND', '2025-05-31 20:00:00', 471, 'cancelled', 1);

-- ********** 票务数据（示例）********** --
INSERT IGNORE INTO ticket (ticket_id, airline_name, flight_num) VALUES
-- 原有票务
(10005, 'Demo Airlines', 103),
(10006, 'Demo Airlines', 103),
-- 新增票务
(30001, 'Global Airways', 101),
(30002, 'Global Airways', 101),
(30003, 'Polar Express', 201),
-- INSERT INTO ticket VALUES
(50000, 'Polar Express', 1000),
(50001, 'Polar Express', 1000),
(50002, 'Demo Airlines', 1001),
(50003, 'Demo Airlines', 1002),
(50004, 'Euro Connect', 1003),
(50005, 'Pacific Wings', 1004),
(50006, 'Demo Airlines', 1005),
(50007, 'Demo Airlines', 1006),
(50008, 'Polar Express', 1007),
(50009, 'Polar Express', 1008),
(50010, 'Pacific Wings', 1009),
(50011, 'Euro Connect', 1010),
(50012, 'Pacific Wings', 1011),
(50013, 'Demo Airlines', 1012),
(50014, 'Polar Express', 1013),
(50015, 'Polar Express', 1014),
(50016, 'Polar Express', 1014),
(50017, 'Demo Airlines', 1001),
(50018, 'Polar Express', 1000),
(50019, 'Pacific Wings', 1004),
(50020, 'Demo Airlines', 1012),
(50021, 'Euro Connect', 1003),
(50022, 'Pacific Wings', 1009),
(50023, 'Polar Express', 1013),
(50024, 'Demo Airlines', 1002),
(50025, 'Polar Express', 1007),
(50026, 'Polar Express', 1014),
(50027, 'Polar Express', 1014),
(50028, 'Pacific Wings', 1011),
(50029, 'Polar Express', 1008),
(50030, 'Demo Airlines', 1005),
(50031, 'Polar Express', 1013),
(50032, 'Euro Connect', 1010),
(50033, 'Demo Airlines', 1006),
(50034, 'Polar Express', 1014);


-- ********** 购买记录（示例）********** --
INSERT IGNORE INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date) VALUES
-- 原有记录
(10005, 'customer1@test.com', 2001, '2023-11-05'),
-- 新增记录
(30001, 'customer1@test.com', NULL, '2024-02-28'),
(30002, 'test02@customer.com', 2001, '2024-03-01'),
-- INSERT INTO purchases VALUES
(50000, 'test01@customer.com', 4001, '2025-04-30'),
(50001, 'test02@customer.com', 1001, '2025-04-15'),
(50002, 'test02@customer.com', 4001, '2025-04-04'),
(50003, 'test02@customer.com', 1001, '2025-04-07'),
(50004, 'test01@customer.com', 1001, '2025-04-16'),
(50005, 'test02@customer.com', 3001, '2025-04-28'),
(50006, 'customer2@test.com', 3001, '2025-04-03'),
(50007, 'customer1@test.com', 2001, '2025-04-13'),
(50008, 'test02@customer.com', 4001, '2025-04-12'),
(50009, 'customer2@test.com', 2001, '2025-04-23'),
(50010, 'test01@customer.com', 1001, '2025-04-26'),
(50011, 'customer1@test.com', 2001, '2025-04-25'),
(50012, 'test01@customer.com', 3001, '2025-04-21'),
(50013, 'test01@customer.com', 2001, '2025-04-10'),
(50014, 'customer2@test.com', 2001, '2025-04-22'),
(50015, 'customer1@test.com', 2001, '2025-04-13'),
(50016, 'customer1@test.com', 2001, '2025-04-13'),
(50017, 'test01@customer.com', 2001, '2025-04-20'),
(50018, 'customer2@test.com', 3001, '2025-04-01'),
(50019, 'customer2@test.com', 1001, '2025-04-10'),
(50020, 'test02@customer.com', 1001, '2025-04-27'),
(50021, 'customer2@test.com', 3001, '2025-04-12'),
(50022, 'test02@customer.com', 1001, '2025-04-09'),
(50023, 'customer2@test.com', 2001, '2025-04-11'),
(50024, 'test01@customer.com', 4001, '2025-04-22'),
(50025, 'test02@customer.com', 1001, '2025-04-11'),
(50026, 'test01@customer.com', 3001, '2025-04-14'),
(50027, 'test01@customer.com', 3001, '2025-04-22'),
(50028, 'test02@customer.com', 2001, '2025-04-04'),
(50029, 'test01@customer.com', 2001, '2025-04-28'),
(50030, 'test01@customer.com', 4001, '2025-04-04'),
(50031, 'customer1@test.com', 2001, '2025-04-17'),
(50032, 'test02@customer.com', 3001, '2025-04-18'),
(50033, 'customer1@test.com', 1001, '2025-04-20'),
(50034, 'customer2@test.com', 3001, '2025-04-02');
