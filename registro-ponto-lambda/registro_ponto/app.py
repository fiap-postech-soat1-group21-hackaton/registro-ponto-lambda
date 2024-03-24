import json
import time
from os import getenv, putenv
from datetime import datetime
import pymysql


putenv('TZ', 'America/Sao_Paulo')
time.tzset()

def lambda_handler(event, _):
    connection = None

    try:
        user_id, datetime = get_register(event)
        connection = get_db_connection()
        make_register(user_id, datetime, connection)

        data_reponse = {
            'registro':  str(datetime)
        }

        return {
            'statusCode': 200,
            "body": json.dumps({
                "success": True,
                "data": data_reponse,
            }),
        }

    except Exception as e:
        raise e

    finally:
        if connection:
            connection.close()

def get_register(event):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    timestamp = datetime.now()
    return user_id, timestamp

def get_db_connection():
        try:
            endpoint = getenv("DB_HOST")
            database = getenv("DB_NAME")
            port = int(getenv("DB_PORT"))
            password = getenv("DB_PASSWORD")
            username = getenv("DB_USER")

            connection = None
            connection = pymysql.connect(host=endpoint, port=port, user=username, passwd=password, db=database)

            if not connection:
                raise RuntimeError('Falha ao conectar no banco de dados. Verifique variaveis de ambiente')

            return connection

        except Exception as e:
            print('db connection stage error', e)
            raise e

def make_register(user_id, timestamp, connection):
    try:
        register_table = getenv("DB_TABLE")
        with connection.cursor() as cursor:
            sql = f"INSERT INTO {register_table} (matricula, registro) VALUES (%s, %s)"
            cursor.execute(sql, (user_id, timestamp))
        
        connection.commit()

    except Exception as e:
        print('make_register stage error', e)
        raise e
