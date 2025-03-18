##from open wheather api to kafka consumer (docker local)-- done
1. pyhton code to produce data from open weather api to kafka topic (kafka\kafka_openweather_producer.py)
2. run docker from docker-compose.yaml, this will import kafka, mysql, airflow, postgres, redis  - docker\docker-composer.yaml
3. run python kafka_openweather_producer.py in docker terminal
4. run kafka-console-consumer

##from python producer to python consumer (dynamo db dump data) (EC2) -- done
1. refer kafka\Kafka_to_ddb.txt

##from mysql to s3 using airflow dag (docker) -- done
1. run docker from docker-compose.yaml, this will import kafka, mysql, airflow, postgres, redis  - docker\docker-composer.yaml
2. create mysql and aws connection in airflow
3. create python file that reads the data from mysql and put into s3 -- airflow_dags\mysql_to_s3.py
4. place the mysql_to_s3.py into docker\dags
5. run airflow dag -- you will get the .json file in s3

## mysql ----airflow(docker)---> s3(csv)
1. run docker from docker-compose.yaml, this will import kafka, mysql, airflow, postgres, redis  - docker\docker-composer.yaml
2. create mysql and aws connection in airflow
3. create python file that reads the data from mysql and put into s3 -- airflow_dags\mysql_to_s3_csv.py
4. place the mysql_to_s3_csv.py into docker\dags
5. run airflow dag -- you will get the .csv file in s3


##spark submit to ddb

##consume kafka data from flink
