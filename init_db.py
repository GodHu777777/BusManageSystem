import mysql.connector
from app import db_config

def init_database():
    conn = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password']
    )
    cursor = conn.cursor()

    # 删除已存在的数据库并重新创建
    cursor.execute("DROP DATABASE IF EXISTS flaskdb")
    cursor.execute("CREATE DATABASE flaskdb")
    cursor.execute("USE flaskdb")

    # 创建表
    create_tables = [
        """
        CREATE TABLE IF NOT EXISTS fleets (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS routes (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            fleet_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (fleet_id) REFERENCES fleets(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS drivers (
            id INT PRIMARY KEY AUTO_INCREMENT,
            job_number VARCHAR(20) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            gender ENUM('male', 'female') NOT NULL,
            fleet_id INT NOT NULL,
            route_id INT,
            is_captain BOOLEAN DEFAULT FALSE,
            is_route_captain BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (fleet_id) REFERENCES fleets(id),
            FOREIGN KEY (route_id) REFERENCES routes(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS vehicles (
            id INT PRIMARY KEY AUTO_INCREMENT,
            plate_number VARCHAR(20) NOT NULL UNIQUE,
            seats INT NOT NULL,
            route_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (route_id) REFERENCES routes(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS violations (
            id INT PRIMARY KEY AUTO_INCREMENT,
            driver_id INT NOT NULL,
            vehicle_id INT NOT NULL,
            violation_type ENUM('red_light', 'zebra_crossing', 'cross_line', 'illegal_parking') NOT NULL,
            time DATETIME NOT NULL,
            location VARCHAR(200),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (driver_id) REFERENCES drivers(id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
        )
        """
    ]

    # 执行建表语句
    for table in create_tables:
        cursor.execute(table)

    # 创建视图
    create_views = [
        """
        CREATE OR REPLACE VIEW driver_fleet_view AS
        SELECT 
            d.id as driver_id,
            d.job_number,
            d.name as driver_name,
            d.gender,
            d.fleet_id,
            f.name as fleet_name,
            r.id as route_id,
            r.name as route_name
        FROM drivers d
        JOIN fleets f ON d.fleet_id = f.id
        LEFT JOIN routes r ON d.route_id = r.id
        """,
        """
        CREATE OR REPLACE VIEW driver_violation_view AS
        SELECT 
            v.id as violation_id,
            v.violation_type,
            v.time,
            v.location,
            d.id as driver_id,
            d.name as driver_name,
            d.job_number,
            vh.plate_number,
            r.name as route_name,
            f.name as fleet_name
        FROM violations v
        JOIN drivers d ON v.driver_id = d.id
        JOIN vehicles vh ON v.vehicle_id = vh.id
        JOIN routes r ON d.route_id = r.id
        JOIN fleets f ON d.fleet_id = f.id
        """,
        """
        CREATE OR REPLACE VIEW fleet_violation_stats_view AS
        SELECT 
            f.id as fleet_id,
            f.name as fleet_name,
            v.violation_type,
            COUNT(*) as violation_count,
            DATE(v.time) as violation_date
        FROM violations v
        JOIN drivers d ON v.driver_id = d.id
        JOIN fleets f ON d.fleet_id = f.id
        GROUP BY f.id, f.name, v.violation_type, DATE(v.time)
        """,
        """
        CREATE OR REPLACE VIEW violation_list_view AS
        SELECT 
            v.id,
            d.name as driver_name,
            d.job_number,
            vh.plate_number,
            r.name as route_name,
            f.name as fleet_name,
            v.violation_type,
            v.time,
            v.location
        FROM violations v
        JOIN drivers d ON v.driver_id = d.id
        JOIN vehicles vh ON v.vehicle_id = vh.id
        JOIN routes r ON d.route_id = r.id
        JOIN fleets f ON d.fleet_id = f.id
        """
    ]

    # 执行创建视图的语句
    for view in create_views:
        try:
            cursor.execute(view)
        except mysql.connector.Error as err:
            print(f"Error creating view: {err}")

    # 插入测试数据
    test_data = [
        """
        INSERT INTO fleets (name) VALUES 
        ('fleet_one'),
        ('fleet_two')
        """,
        """
        INSERT INTO routes (name, fleet_id) VALUES 
        ('route_1', 1),
        ('route_2', 1),
        ('route_3', 2)
        """,
        """
        INSERT INTO drivers (job_number, name, gender, fleet_id, route_id, is_captain, is_route_captain) VALUES 
        ('d001', 'john', 'male', 1, 1, false, true),
        ('d002', 'mike', 'male', 1, 1, false, false),
        ('d003', 'sarah', 'female', 2, 2, true, false)
        """,
        """
        INSERT INTO vehicles (plate_number, seats, route_id) VALUES 
        ('bj12345', 35, 1),
        ('bj23456', 35, 2),
        ('bj34567', 35, 3)
        """,
        """
        INSERT INTO violations (driver_id, vehicle_id, violation_type, time, location) VALUES 
        (1, 1, 'red_light', '2024-01-01 08:30:00', 'location_1'),
        (2, 2, 'zebra_crossing', '2024-01-02 09:15:00', 'location_2'),
        (1, 1, 'illegal_parking', '2024-01-03 14:20:00', 'location_3')
        """
    ]

    # 执行插入测试数据的语句
    for data in test_data:
        try:
            cursor.execute(data)
        except mysql.connector.Error as err:
            print(f"Error inserting test data: {err}")

    # 提交更改
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    init_database() 