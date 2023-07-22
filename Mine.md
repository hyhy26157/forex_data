# forex_data

using kafka to take in forex data from finnhub API and 


#Using GCP VM
1. install gcp
https://cloud.google.com/sdk/docs/install
2. get a cloud account and create cloud vm (using gcp here)
https://cloud.google.com/compute/docs/instances/create-start-instance
Using ubuntu image
3. connect to gcp vm
gcloud init
gcloud compute ssh instance-1 --zone=asia-southeast1-b
note: If you have a dynamic IP address like mine, remember to check your IP address before login and put it on the VM firewall whitelist.
4. Update and Install Java JDK version 8+
Optional: sudo adduser <newuser>
sudo apt-get update
sudo apt-get install openjdk-8-jdk
java -version
5. Download & unzip Apache Zookeeper
wget https://dlcdn.apache.org/zookeeper/zookeeper-3.8.1/apache-zookeeper-3.8.1-bin.tar.gz
tar -xsf <zookeeper-3.8.1-bin.tar.gz>
6. Download & unzip Apache Kafka
wget https://downloads.apache.org/kafka/3.5.0/kafka_2.13-3.5.0.tgz
tar -xsf <kafka-3.5.0-bin.tar.gz>
7. Pre-requisite
# define spark environment in .bashrc
export SPARK_HOME=/opt/spark/spark-3.4.0-bin-hadoop3
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
export PYSPARK_PYTHON=/usr/bin/python3

source .bashrc 
# start spark
$SPARK_HOME/sbin/start-master.sh
# find the start master location
/opt/spark/spark-3.4.0-binhadoop3/logs/<*.Master-1-hdfs>.out
# run slave (single server setup)
$SPARK_HOME/sbin/start-worker.sh spark://hdfs.asia-southeast1-b.c.tfip-390503.internal:7077
# setup zookeeper systemmd
sudo nano /etc/systemd/system/zookeeper.service

[Unit]
Description=Apache Zookeeper server
Documentation=http://zookeeper.apache.org
Requires=network.target remote-fs.target
After=network.target remote-fs.target
[Service]
Type=simple
ExecStart=ExecStart=/home/hadoop/kafka/kafka/bin/zookeeper-server-start.sh /home/hadoop/kafka/kafka/config/zookeeper.properties
ExecStop=/home/hadoop/kafka/kafka/bin/zookeeper-server-stop.sh
Restart=on-abnormal
[Install]
WantedBy=multi-user.target

# setup kafka systemmd
sudo gedit /etc/systemd/system/kafka.service

[Unit]
Description=Apache Kafka Server
Documentation=http://kafka.apache.org/documentation.html
Requires=zookeeper.service
[Service]
Type=simple
Environment="JAVA_HOME=/usr/lib/jvm/java-1.11.0-openjdk-amd64"
ExecStart=/home/hadoop/kafka/kafka/bin/kafka-server-start.sh /home/hadoop/kafka/kafka/config/server.properties
ExecStop=/home/hadoop/kafka/kafka/bin/kafka-server-stop.sh
[Install]
WantedBy=multi-user.target


sudo systemctl daemon-reload
sudo systemctl start kafka
sudo systemctl start zookeeper
systemctl status


~/kafka/kafka/bin/kafka-topics.sh --create --topic forex_producer --bootstrap-server 10.148.0.8:9092 --partitions 1 --replication-factor 1