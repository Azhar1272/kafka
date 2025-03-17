from airflow import DAG
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.python import PythonOperator
from datetime import datetime
import json
import logging


def extract_data():
    mysql_hook = MySqlHook(mysql_conn_id='mysql_conn_docker')
    sql = "SELECT count(1) as cnt FROM users;"
    records = mysql_hook.get_records(sql)
    
    data = json.dumps(records)
    with open('/tmp/data.json', 'w') as f:
        f.write(data)

def upload_to_s3():
    s3_hook = S3Hook(aws_conn_id='aws_default')
    s3_hook.load_file('/tmp/data.json', key='airflow/data.json', bucket_name='epam-cargil-project', replace=True)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 15),
}

dag = DAG('mysql_to_s3', default_args=default_args, schedule_interval='@daily')
upload_task = PythonOperator(task_id='upload', python_callable=upload_to_s3, dag=dag)
logging.basicConfig(level=logging.INFO)
logging.info("s3 connection succeeded:",upload_task)
extract_task = PythonOperator(task_id='extract', python_callable=extract_data, dag=dag)


extract_task >> upload_task
