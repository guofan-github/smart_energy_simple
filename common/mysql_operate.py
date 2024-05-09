import logging

import pymysql

from conf.公共信息 import db_host, db_port, db_user, db_password, db_database


# 连接到MySQL数据库
def connect_to_mysql():
    try:
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_database,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Connected to MySQL successfully!")
        return connection
    except pymysql.Error as e:
        print("Error:", e)


# 插入数据到表中
def insert_data(connection, data):
    try:
        with connection.cursor() as cursor:
            query = "INSERT INTO your_table_name (column1, column2, column3) VALUES (%s, %s, %s)"
            cursor.execute(query, data)
        connection.commit()
        print("Data inserted successfully!")
    except pymysql.Error as e:
        print("Error:", e)
        connection.rollback()


# 查询表中的数据
def select_data(connection):
    try:
        with connection.cursor() as cursor:
            query = "SELECT * FROM sys_project ORDER BY created_time DESC LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchall()
            print(f"查询到的最新创建项目为:{result}")
            logging.info(f"查询到的最新创建项目为:{result}")
            for row in result:
                print(row)
    except pymysql.Error as e:
        print("Error:", e)


# 删除表中按创建时间倒序排列的第一条记录
def delete_first_record(connection):
    try:
        cursor = connection.cursor()
        query = "DELETE FROM sys_project ORDER BY created_time DESC LIMIT 1"
        cursor.execute(query)
        connection.commit()
        print("First record deleted successfully!")
    except pymysql.Error as err:
        print("Error:", err)
        connection.rollback()


# 更新按创建时间倒序排列的第一条记录的某个字段值
def update_first_record(connection, new_value):
    try:
        cursor = connection.cursor()
        query = "UPDATE sys_project SET deleted_flag = %s ORDER BY created_time DESC LIMIT 1"
        cursor.execute(query, (new_value,))
        connection.commit()
        print("已经将本次自动化测试新建的项目从数据库中更改deleted_flag为1!")
        logging.info("已经将本次自动化测试新建的项目从数据库中更改deleted_flag为1!")
    except pymysql.Error as err:
        print("Error:", err)
        connection.rollback()


# 主函数
def main():
    # 连接到MySQL数据库
    connection = connect_to_mysql()

    # # 插入数据到表中
    # data_to_insert = ("value1", "value2", "value3")  # 替换为实际数据
    # insert_data(connection, data_to_insert)

    # # 删除表中按创建时间倒序排列的第一条记录
    # delete_first_record(connection)

    # 更新按创建时间倒序排列的第一条记录的某个字段值
    new_value = "1"  # 替换为新值
    update_first_record(connection, new_value)

    # 查询表中的数据
    select_data(connection)

    # 关闭数据库连接
    connection.close()


if __name__ == "__main__":
    main()
