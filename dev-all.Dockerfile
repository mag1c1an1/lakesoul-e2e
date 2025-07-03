FROM dmetasoul/dev-base:0.1.0 # use alpine
# flink
RUN curl -O https://mirrors.tuna.tsinghua.edu.cn/apache/flink/flink-1.20.1/flink-1.20.1-bin-scala_2.12.tgz
# CMD ["/bin/sh"]
# # 同步包数据库并更新系统（Arch Linux滚动更新特性）
# # RUN pacman -Syu --noconfirm \
# #     && pacman -S --noconfirm python python-pip \
# #     && pacman -Scc --noconfirm  # 清理缓存，减小镜像体积
#
# # # 设置工作目录
# # WORKDIR /app
#
# # # 复制应用代码和依赖文件
# # COPY requirements.txt .
# # RUN pip install --no-cache-dir -r requirements.txt
#
# # COPY . .
#
# # # 暴露端口
# # EXPOSE 8000
#
# # # 启动命令
# # CMD ["python", "app.py"]
