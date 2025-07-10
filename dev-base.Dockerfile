FROM docker.1ms.run/archlinux/archlinux:base-devel-20250630.0.373922
RUN echo "Server = https://mirrors.tuna.tsinghua.edu.cn/archlinux/\$repo/os/\$arch" | cat - /etc/pacman.d/mirrorlist > tmpf && mv tmpf /etc/pacman.d/mirrorlist
RUN pacman -Sy && pacman -S --noconfirm cargo rustup git jdk11-openjdk cmake make maven zip unzip wget python3 python-pip python-pipx kubectl
ENV PATH=/root/.local/bin:$PATH
# protoc
RUN wget https://github.com/protocolbuffers/protobuf/releases/download/v25.7/protoc-25.7-linux-x86_64.zip -O /protoc25.zip && unzip /protoc25.zip && rm -rf protoc25.zip
ENV PATH=/protoc25/bin:$PATH
RUN mv /usr/share/java/maven/conf/settings.xml /usr/share/java/maven/conf/settings.xml.bak
COPY settings.xml /usr/share/java/maven/conf/settings.xml
ENV RUSTUP_DIST_SERVER="https://rsproxy.cn"
ENV RUSTUP_UPDATE_ROOT="https://rsproxy.cn/rustup"
