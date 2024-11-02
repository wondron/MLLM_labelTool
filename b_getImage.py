
import pymysql

def get_cookbook_data(output_type=0):
    db = pymysql.connect(
        host="rdsp1488a7h360d1p3b6no.mysql.rds.aliyuncs.com",
        user="roki_ai",
        password="Bj9HGD9UCnxbpTGYMg7VeP9I0LcdJ",
        port=3306,
        database="cook-management",
        charset="utf8",
    )
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)


