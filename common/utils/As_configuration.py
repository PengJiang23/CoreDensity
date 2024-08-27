import numpy as np
# 本地数据库配置
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_HOST = 'localhost'
DB_PORT = 3306
DB_NAME = 'rpki'


# 服务器数据库
DBS_USER = 'rpki'
DBS_PASSWORD = 'wKVY9alc'
DBS_HOST = '10.12.54.102'
DBS_PORT = 33106
DBS_NAME = 'rpki'


# 导出文件路径
PARENT_FILE_PATH = '../Data/'

# request配置
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}

proxies = {
    'http': '223.70.126.84:3128',
    'http': '58.220.95.79:10000',
    'http': '121.8.215.106:9797',
    'http': '221.226.75.86:55443',
}

# asrank操作属性
# SVG_WIDTH = 900
# SVG_HEIGHT = 800
SVG_WIDTH = 1900
SVG_HEIGHT = 1000
RADIUS_CONST = 100
RAD = np.pi / 180