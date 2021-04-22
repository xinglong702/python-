import sqlite3

print('开始写入数据库......')
conn = sqlite3.connect('Top250.db')
print('成功打开数据库！！！')

c = conn.cursor()
sql = '''
        create table Top250
        (
            id integer primary key autoincrement,
            info_link text,
            pic_link text,
            cname varchar,
            ename varchar,
            score numeric ,
            rated numeric ,
            intro text,
            info text
        );
    '''
c.execute(sql)
conn.commit()
conn.close()
print('成功建表!!!')
