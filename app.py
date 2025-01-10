from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime, date

app = Flask(__name__)

# 保持原有的 MySQL 配置
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '123456',
    'database': 'flaskdb'
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# 首页 - 显示主要功能入口
@app.route('/')
def index():
    return render_template('index.html')

# 1. 司机管理
@app.route('/drivers')
def list_drivers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT d.*, f.name as fleet_name, r.name as route_name 
        FROM drivers d 
        JOIN fleets f ON d.fleet_id = f.id 
        LEFT JOIN routes r ON d.route_id = r.id
    ''')
    drivers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('drivers/list.html', drivers=drivers)

@app.route('/driver/add', methods=['GET', 'POST'])
def add_driver():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO drivers (job_number, name, gender, fleet_id, route_id) VALUES (%s, %s, %s, %s, %s)',
            (
                request.form['job_number'],
                request.form['name'],
                request.form['gender'],
                request.form['fleet_id'],
                request.form['route_id'] or None
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('list_drivers'))
    
    # 获取车队和线路列表
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, name FROM fleets')
    fleets = cursor.fetchall()
    cursor.execute('SELECT id, name FROM routes')
    routes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('drivers/add.html', fleets=fleets, routes=routes)

# 2. 车辆管理
@app.route('/vehicles')
def list_vehicles():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT plate_number, seats FROM vehicles')
    vehicles = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('vehicles/list.html', vehicles=vehicles)

@app.route('/vehicle/add', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO vehicles (plate_number, seats) VALUES (%s, %s)',
            (
                request.form['plate_number'],
                request.form['seats']
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('list_vehicles'))
    
    return render_template('vehicles/add.html')

# 3. 违章管理
@app.route('/violations')
def list_violations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM violation_list_view ORDER BY time DESC')
    violations = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('violations/list.html', violations=violations)

@app.route('/violation/add', methods=['GET', 'POST'])
def add_violation():
    # 检查当前用户是否为队长或路队长
    is_captain = True  # 这里应该从用户会话中获取实际的权限状态
    
    if request.method == 'POST' and is_captain:
        # 将前端传来的date格式转换为MySQL datetime格式
        violation_date = datetime.strptime(request.form['time'], '%Y-%m-%d')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO violations (driver_id, vehicle_id, violation_type, time, location) VALUES (%s, %s, %s, %s, %s)',
            (
                request.form['driver_id'],
                request.form['vehicle_id'],
                request.form['violation_type'],
                violation_date,
                request.form['location']
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('list_violations'))
    
    # 获取可选的司机和车辆列表
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 获取当前用户管理的车队/线路的司机
    cursor.execute('''
        SELECT d.id, d.name, d.job_number 
        FROM drivers d
    ''')
    drivers = cursor.fetchall()
    
    # 获取车辆列表
    cursor.execute('SELECT id, plate_number FROM vehicles')
    vehicles = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # 设置默认的违章日期为当前日期
    default_time = date.today().strftime('%Y-%m-%d')
    
    return render_template('violations/add.html', 
                         drivers=drivers,
                         vehicles=vehicles,
                         is_captain=is_captain,
                         default_time=default_time)

# 4. 查询功能
@app.route('/fleet/drivers', methods=['GET'])
def fleet_drivers():
    # 如果没有传入fleet_id参数，显示选择车队的表单
    if not request.args.get('fleet_id'):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, name FROM fleets')
        fleets = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('queries/fleet_drivers_form.html', fleets=fleets)
    
    # 如果传入了fleet_id，显示查询结果
    fleet_id = request.args.get('fleet_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT driver_id, job_number, driver_name, gender, route_name
        FROM driver_fleet_view
        WHERE fleet_id = %s
    ''', (fleet_id,))
    drivers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('queries/fleet_drivers.html', drivers=drivers)

@app.route('/driver/violations', methods=['GET'])
def driver_violations():
    driver_id = request.args.get('driver_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if driver_id and start_date and end_date:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT violation_type, time, location, plate_number
            FROM driver_violation_view
            WHERE driver_id = %s AND DATE(time) BETWEEN %s AND %s
        ''', (driver_id, start_date, end_date))
        violations = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('queries/driver_violations.html', violations=violations)
    
    # 获取司机列表供选择
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, name, job_number FROM drivers')
    drivers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('queries/driver_violations_form.html', drivers=drivers)

@app.route('/fleet/violation_stats', methods=['GET'])
def fleet_violation_stats():
    fleet_id = request.args.get('fleet_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if fleet_id and start_date and end_date:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT violation_type, SUM(violation_count) as total_count
            FROM fleet_violation_stats_view
            WHERE fleet_id = %s AND violation_date BETWEEN %s AND %s
            GROUP BY violation_type
        ''', (fleet_id, start_date, end_date))
        stats = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('queries/violation_stats.html', stats=stats)
    
    # 获取车队列表供选择
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, name FROM fleets')
    fleets = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('queries/violation_stats_form.html', fleets=fleets)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
