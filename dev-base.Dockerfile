FROM docker.1ms.run/library/alpine:latest # 基于alpine官方镜像
RUN sed -i 's#https\?://dl-cdn.alpinelinux.org/alpine#https://mirrors.tuna.tsinghua.edu.cn/alpine#g' /etc/apk/repositories
RUN apk add curl git rustup cargo protoc openjdk11
