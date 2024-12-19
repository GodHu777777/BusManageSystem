from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# MySQL 配置
db_config = {
    'host': '81.70.210.120',
    'user': 'root',  # 替换成你的 MySQL 用户
    'password': '',  # 替换成你的密码
    'database': 'flask_db'
}

# 连接 MySQL 数据库
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# 首页，展示所有用户
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', users=users)

# 添加用户页面
@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, email) VALUES (%s, %s)', (name, email))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('add_user.html')

if __name__ == '__main__':
    app.run(debug=True)
