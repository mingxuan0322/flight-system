## ⚙️ 数据库字段修改记录

- 将所有 `passport` 字段扩展为 `VARCHAR(200)`，提升兼容性。
- 所有密码字段改为哈希（`bcrypt`），长度设为 `VARCHAR(60)` 并添加注释。
- 为 `booking_agent.booking_agent_id` 添加唯一约束。
- 修改 `flight.status` 字段为 ENUM，提高可读性与规范性。
- 为 `ticket.ticket_id` 添加唯一索引以提升查询效率。


