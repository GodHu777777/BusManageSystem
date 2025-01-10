# 西安电子科技大学计科院数据库大作业

# How to use?

## Step 0
    
```bash
git clone https://github.com/GodHu777777/BusManageSystem
cd BusManageSystem
```

安装mysql 我用的docker
```bash
docker pull mysql:8.0.3
docker run -d --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:8.0.3`
```

## Step 1

初始化数据库并启动服务器

```bash
python3 init_db.py # 初始化数据库
python3 app.py # 启动服务器
```

# Conda usage 

1. 安装anaconda[完整教程](https://blog.csdn.net/m0_49683806/article/details/135674621)

```bash
wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh
bash Anaconda3-2023.03-1-Linux-x86_64.sh        
# 检查.bashrc文件里是否配置环境变量eval "$(/root/anaconda3/bin/conda shell.bash hook)"
source ~/.bashrc
```

2. 创建conda环境

```bash
conda create -n "BUS" python=3.8
conda activate BUS
pip install -r requirements.txt
```

然后在浏览器打开[http://localhost:5000](http://localhost:5000)

[数据库设计网课](https://www.bilibili.com/video/BV1DR4y1k7WL/?spm_id_from=333.788.top_right_bar_window_history.content.click)

# 安装mysql

因为自己手上有云服务器，所以参考如下教程[Linux 安装Mysql 详细教程(图文教程)](https://blog.csdn.net/bai_shuang/article/details/122939884)，当然，也很推荐docker~

# Note

1. mysql在linux上好像中文编码支持不够，建议值使用全英文
2. linux上的mysql表名区分大小写，可以参考[Linux环境下MySQL区分大小写的解决办法](https://blog.csdn.net/qq_41397201/article/details/86519519)，本项目偷懒了，所有表都用的小写qaq