FROM dmetasoul/dev-base:0.1
# flink
RUN wget https://mirrors.tuna.tsinghua.edu.cn/apache/flink/flink-1.20.1/flink-1.20.1-bin-scala_2.12.tgz && tar -xzvf flink-1.20.1-bin-scala_2.12.tgz && rm flink-1.20.1-bin-scala_2.12.tgz
ENV FLINK_HOME=/flink-1.20.1
ENV PATH=$FLINK_HOME/bin:$PATH
# spark
RUN wget https://dmetasoul-bucket.obs.cn-southwest-2.myhuaweicloud.com/releases/spark/spark-3.3.2-bin-hadoop3.tgz && tar -xzvf spark-3.3.2-bin-hadoop3.tgz && rm spark-3.3.2-bin-hadoop3.tgz
ENV SPARK_HOME=/spark-3.3.2-bin-hadoop3 
ENV PATH=$SPARK_HOME/bin:$PATH
