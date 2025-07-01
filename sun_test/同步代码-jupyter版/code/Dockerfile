# 基于官方 Jupyter 数据科学镜像
FROM docker.1ms.run/jupyter/datascience-notebook:latest

USER root

# 安装 Redis Stack Server 所需的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    lsb-release \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*


# 设置工作目录
WORKDIR /home/jovyan/work

# 复制当前目录中的所有 notebook 文件到容器中
COPY . /home/jovyan/work/

# 确保文件权限正确
RUN chown -R jovyan:users /home/jovyan/work/

# 切回 jovyan 用户
USER jovyan

# 安装常用的数据科学包和 Redis 客户端库
RUN pip install --no-cache-dir \
    langchain \
    langchain-openai 

# 创建 Jupyter 配置目录
RUN mkdir -p ~/.jupyter

# 生成配置文件
RUN jupyter notebook --generate-config

# 设置无密码访问
RUN echo "c.NotebookApp.token = ''" >> ~/.jupyter/jupyter_notebook_config.py
RUN echo "c.NotebookApp.password = ''" >> ~/.jupyter/jupyter_notebook_config.py
RUN echo "c.NotebookApp.notebook_dir = '/home/jovyan/work'" >> ~/.jupyter/jupyter_notebook_config.py

# 暴露 Redis 和 Jupyter 使用的端口
EXPOSE 8888

# 启动 Jupyter notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
