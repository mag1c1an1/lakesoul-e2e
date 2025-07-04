FROM docker.1ms.run/archlinux/archlinux:base-devel-20250630.0.373922
RUN pacman -Sy && pacman -S --noconfirm cargo rustup git jdk11-openjdk cmake make maven zip unzip wget python3 python-pip python-pipx
# protoc
RUN wget https://github.com/protocolbuffers/protobuf/releases/download/v25.7/protoc-25.7-linux-x86_64.zip -O /protoc25.zip && unzip /protoc25.zip && rm -rf protoc25.zip
ENV PATH=/protoc25/bin:$PATH
