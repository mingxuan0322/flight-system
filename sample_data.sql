-- 插入航空公司
INSERT INTO airline (airline_name) VALUES ('China Eastern'), ('Delta Air Lines');

-- 插入飞机
INSERT INTO airplane (airplane_id, airline_name, seats) VALUES
(1, 'China Eastern', 300),
(2, 'Delta Air Lines', 280);

-- 插入机场
INSERT INTO airport (airport_name, city) VALUES
('PVG', 'Shanghai'),
('JFK', 'New York');

-- 插入航班
INSERT INTO flight (airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, base_price, status, airplane_id) VALUES
('China Eastern', 'MU587', 'PVG', 'JFK', '2025-05-10 09:00:00', '2025-05-10 20:00:00', 500.00, 'on-time', 1),
('Delta Air Lines', 'DL89', 'JFK', 'PVG', '2025-05-12 15:00:00', '2025-05-13 05:00:00', 520.00, 'delayed', 2);

-- 插入用户
INSERT INTO customer (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth)
VALUES ('alice@example.com', 'Alice', md5('alice123'), '101', 'Nanjing Rd', 'Shanghai', 'SH', '13800000000', 'P1234567', '2030-01-01', 'China', '1998-05-05');

-- 插入代理与其关系
INSERT INTO booking_agent (email, password) VALUES ('agent1@example.com', md5('agentpass'));
INSERT INTO booking_agent_work_for (email, airline_name) VALUES ('agent1@example.com', 'China Eastern');

-- 插入员工
INSERT INTO airline_staff (username, password, first_name, last_name, date_of_birth, airline_name)
VALUES ('staff1', md5('staffpass'), 'John', 'Doe', '1980-01-01', 'China Eastern');

-- 模拟 ticket 票号
INSERT INTO ticket (ticket_id, airline_name, flight_num) VALUES
('T001', 'China Eastern', 'MU587'),
('T002', 'Delta Air Lines', 'DL89');

-- 客户购票
INSERT INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date)
VALUES ('T001', 'alice@example.com', NULL, '2025-05-01');

-- 代理为他人购票
INSERT INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date)
VALUES ('T002', 'alice@example.com', (SELECT booking_agent_id FROM booking_agent WHERE email='agent1@example.com'), '2025-05-01');
