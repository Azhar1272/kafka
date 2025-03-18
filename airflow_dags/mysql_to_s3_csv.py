from datetime import datetime
from airflow.operators.email import EmailOperator
import pandas as pd
import logging
from io import StringIO
from airflow import DAG
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Default arguments
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

# Define DAG
dag = DAG(
    'mysql_to_s3_export_csv',
    default_args=default_args,
    schedule_interval="*/10 * * * *",  # Runs every 10 minutes
    catchup=False,
)

# Task 1: Test MySQL Connection
def test_mysql_connection():
    try:
        mysql_hook = MySqlHook(mysql_conn_id='mysql_conn_docker')  
        logging.info("MySQL Connection Successful!")
        test_conn = mysql_hook.get_first("SELECT NOW();")
        logging.info(f"MySQL Test Query Result: {test_conn}")
    except Exception as e:
        logging.error(f"MySQL Connection Failed: {str(e)}")
        raise

mysql_connect_test = PythonOperator(
    task_id='mysql_connect_test',
    python_callable=test_mysql_connection,
    dag=dag,
)

# Task 2: Read Data from MySQL Table
def read_mysql_data():
    try:
        mysql_hook = MySqlHook(mysql_conn_id='mysql_conn_docker')
        records = mysql_hook.get_records("SELECT * FROM users;") 
        
        if not records:
            logging.info("No records found in the table!")
        else:
            logging.info("====== MySQL Query Results ======")
            for record in records:
                logging.info(record)  
    except Exception as e:
        logging.error(f"Error while reading data: {str(e)}")
        raise

read_mysql_task = PythonOperator(
    task_id='read_mysql_data',
    python_callable=read_mysql_data,
    dag=dag,
)

# Task 3: Test AWS S3 Connection
def test_aws_connection():
    try:
        s3_hook = S3Hook(aws_conn_id='aws_default')  
        bucket_name = "epam-cargil-project"  
        s3_hook.check_for_bucket(bucket_name)
        logging.info(f"AWS S3 Connection Successful! Bucket '{bucket_name}' exists.")
    except Exception as e:
        logging.error(f"AWS Connection Failed: {str(e)}")
        raise

aws_connect_test = PythonOperator(
    task_id='aws_connect_test',
    python_callable=test_aws_connection,
    dag=dag,
)

# Task 4: Export MySQL Data to AWS S3

def export_to_s3():
    try:
        mysql_hook = MySqlHook(mysql_conn_id='mysql_conn_docker')
        s3_hook = S3Hook(aws_conn_id='aws_default')

        # Fetch data from MySQL
        records = mysql_hook.get_pandas_df("SELECT * FROM users;")

        if records.empty:
            logging.info("No data found to export!")
            return

        # Convert data to CSV
        csv_buffer = StringIO()
        records.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        s3_bucket = "epam-cargil-project"
        s3_key = f"airflow/users_{timestamp}.csv"  # Filename with timestamp

        # Upload CSV to S3
        s3_hook.load_string(
            string_data=csv_data,
            key=s3_key,
            bucket_name=s3_bucket,
            replace=True
        )

        logging.info(f"Data successfully exported to S3: s3://{s3_bucket}/{s3_key}")

    except Exception as e:
        logging.error(f"Error exporting to S3: {str(e)}")
        raise


export_to_s3_task = PythonOperator(
    task_id='export_to_s3',
    python_callable=export_to_s3,
    dag=dag,
)


# Define recipient emails
# recipient_list = ['m.azhar1618@gmail.com']
# # Generate timestamped file name
# timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# file_name = f"users_{timestamp}.csv"
# send_email = EmailOperator(
#     task_id='send_test_email',
#     to= recipient_list,
#     subject='Airflow: MySQL csv Export to s3 Completed',
#     html_content=f"""
#             <p>Hello Team,</p>
#             <h3>The MySQL data export has been completed successfully.</h3>
#             <p><strong>File Name:</strong> <span style="color:blue;">{file_name}</span></p>
#             <p>Regards,<br>Dinesh<br>Data Engineer<br>Airflow Team</p>
#         """,

#     conn_id='smtp_conn',  # Uses the Airflow UI SMTP Connection
#     dag=dag
# )



#mysql_connect_test >> read_mysql_task >> aws_connect_test >> export_to_s3_task >> send_email 
mysql_connect_test >> read_mysql_task >> aws_connect_test >> export_to_s3_task
