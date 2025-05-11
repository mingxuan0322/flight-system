
/* 扩展航空公司数据 */
INSERT IGNORE INTO airline (airline_name) VALUES
('Pacific Wings'),
('Euro Connect'),
('Demo Airlines'),
('Sky High Airways'),
('Japan Airlines');

/* 扩展机场数据 */
INSERT IGNORE INTO airport (airport_name, airport_city) VALUES
('JFK','New York'),
('PVG','Shanghai'),
('HND', 'Tokyo'),
('LHR', 'London'),
('DXB', 'Dubai'),
('LAX', 'Los Angeles'),
('HND', 'Tokyo'),
('LHR', 'London'),
('DXB', 'Dubai');

/* 扩展飞机数据（包含小容量飞机用于超售测试）*/
INSERT IGNORE INTO airplane (airline_name, airplane_id, seats) VALUES
('Demo Airlines', 3, 5),  -- 小容量用于超售测试
('Sky High Airways', 102, 220),
('Euro Connect',1,200),
('Pacific Wings', 1, 180);

/* 扩展客户数据（密码均为test123）*/
INSERT IGNORE INTO customer (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth) VALUES
('test01@customer.com', 'test1', 'test123', '1', 'Gold Street', 'Beverly Hills', 'CA', 3105551234, 'VIP123456', '2030-01-01', 'USA', '1980-12-01'),
('test02@customer.com', 'test2', 'test123', '55', 'World Ave', 'Paris', 'TX', 2145555678, 'PASSP7890', '2027-09-15', 'France', '1995-07-04'),
('customer1@test.com', 'Customer One', 'test123', '12', 'Main St', 'New York', 'NY', 1234567890, 'P1234567', '2029-06-01', 'USA', '1990-01-01'),
('customer2@test.com', 'Customer Two', 'test123', '34', 'Oak Ave', 'Chicago', 'IL', 9876543210, 'P7654321', '2028-08-15', 'USA', '1992-02-02');
/* 扩展代理数据 */
INSERT IGNORE INTO booking_agent (email, password, booking_agent_id) VALUES
('euro_agent@test.com', 'test123', 2001),
('asia_agent@test.com', 'test123', 3001),
('agent02@test.com','test123',1001),
('agent01@test.com','test123',4001);

INSERT IGNORE INTO booking_agent_work_for (email, airline_name) VALUES
('euro_agent@test.com', 'Sky High Airways'),
('asia_agent@test.com', 'Euro Connect'),
('agent01@test.com', 'Euro Connect'),
('agent02@test.com', 'Pacific Wings');

/* 扩展员工权限数据 */
INSERT IGNORE INTO airline_staff (username, password, first_name, last_name, date_of_birth, airline_name) VALUES
-- ('euro_admin@test.com', '$2b$12$euroadm...', 'Hans', 'Schmidt', '1985-05-05', 'Euro Connect'),
-- ('pacific_ops@test.com', '$2b$12$pacops...', 'Yuki', 'Tanaka', '1990-11-11', 'Pacific Wings');
('staff01@test.com', 'test123', 'Hans', 'Schmidt', '1985-05-05', 'Euro Connect'),
('staff02@test.com', 'test123', 'Yuki', 'Tanaka', '1990-11-11', 'Pacific Wings');

INSERT IGNORE INTO permission (username, permission_type) VALUES
('euro_admin@test.com', 'Admin'),
('pacific_ops@test.com', 'Operator');

/* 扩展航班数据（包含不同状态）*/
INSERT IGNORE INTO flight (airline_name, flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price, status, airplane_id) VALUES
('Demo Airlines', 103, 'LAX', '2023-12-10 10:00:00', 'JFK', '2023-12-10 18:00:00', 350, 'on-time', 3),  -- 5座位飞机
('Euro Connect', 501, 'LHR', '2023-12-12 12:00:00', 'DXB', '2023-12-12 20:00:00', 950, 'delayed', 1),
('Pacific Wings', 701, 'HND', '2023-12-15 09:00:00', 'PVG', '2023-12-15 11:00:00', 450, 'cancelled', 1);

/* 扩展票务数据（包含超售测试场景）*/
-- 已售完的航班（Demo Airlines 103，5座位）
INSERT IGNORE INTO ticket (ticket_id, airline_name, flight_num) VALUES
(10005, 'Demo Airlines', 103),
(10006, 'Demo Airlines', 103),
(10007, 'Demo Airlines', 103),
(10008, 'Demo Airlines', 103),
(10009, 'Demo Airlines', 103);

INSERT IGNORE INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date) VALUES
(10005, 'customer1@test.com', 2001, '2023-11-05'),
(10006, 'customer2@test.com', NULL, '2023-11-05'),
(10007, 'test01@customer.com', 2001, '2023-11-06'),
(10008, 'test02@customer.com', 3001, '2023-11-06'),
(10009, 'customer1@test.com', NULL, '2023-11-07');

/* 历史数据（用于报表测试）*/
INSERT IGNORE INTO flight (airline_name, flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price, status, airplane_id) VALUES
('Demo Airlines', 201, 'JFK', '2022-06-01 08:00:00', 'LHR', '2022-06-01 20:00:00', 1200, 'on-time', 3);

INSERT IGNORE INTO ticket (ticket_id, airline_name, flight_num) VALUES
(20001, 'Demo Airlines', 201);

INSERT IGNORE INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date) VALUES
(20001, 'customer1@test.com', 1001, '2022-05-15');