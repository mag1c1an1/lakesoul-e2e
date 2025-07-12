# SPDX-FileCopyrightText: LakeSoul Contributors
# 
# SPDX-License-Identifier: Apache-2.0
FROM docker.1ms.run/archlinux/archlinux:base-devel-20250630.0.373922
RUN echo "Server = https://mirrors.tuna.tsinghua.edu.cn/archlinux/\$repo/os/\$arch" | cat - /etc/pacman.d/mirrorlist > tmpf && mv tmpf /etc/pacman.d/mirrorlist
RUN pacman -Sy && pacman -S --noconfirm cargo rustup git jdk11-openjdk cmake make maven zip unzip wget python3 python-pip python-pipx kubectl uv
ENV PATH=/root/.local/bin:$PATH
# protoc
COPY protoc-25.7-linux-x86_64.zip /protoc25.zip
RUN unzip /protoc25.zip && rm -rf protoc25.zip
ENV PATH=/protoc25/bin:$PATH
RUN mv /usr/share/java/maven/conf/settings.xml /usr/share/java/maven/conf/settings.xml.bak
COPY settings.xml /usr/share/java/maven/conf/settings.xml
ENV RUSTUP_DIST_SERVER="https://rsproxy.cn"
ENV RUSTUP_UPDATE_ROOT="https://rsproxy.cn/rustup"
# flink
RUN wget https://mirrors.tuna.tsinghua.edu.cn/apache/flink/flink-1.20.1/flink-1.20.1-bin-scala_2.12.tgz && tar -xzvf flink-1.20.1-bin-scala_2.12.tgz && rm flink-1.20.1-bin-scala_2.12.tgz
ENV FLINK_HOME=/flink-1.20.1
ENV PATH=$FLINK_HOME/bin:$PATH
# spark
# RUN wget https://dmetasoul-bucket.obs.cn-southwest-2.myhuaweicloud.com/releases/spark/spark-3.3.2-bin-hadoop3.tgz && tar -xzvf spark-3.3.2-bin-hadoop3.tgz && rm spark-3.3.2-bin-hadoop3.tgz
# ENV SPARK_HOME=/spark-3.3.2-bin-hadoop3 
# ENV PATH=$SPARK_HOME/bin:$PATH
COPY e2e/dist/e2etest-0.1.1.tar.gz /
RUN tar xvzf e2etest-0.1.1.tar.gz && cd e2etest-0.1.1 && uv sync && uv build && ln -s /e2etest-0.1.1/.venv/bin/e2etest /usr/bin/e2etest
COPY config.yaml /
# RUN pipx install e2etest-0.1.1-py3-none-any.whl --index-url https://mirrors.163.com/pypi/simple