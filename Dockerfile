FROM python:3.10

MAINTAINER rw <ruowei.du93@gmail.com>

COPY requirements /tmp/requirements
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r /tmp/requirements/deployment.txt

RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

ARG work_home=/app

RUN mkdir ${work_home}

WORKDIR ${work_home}

COPY . ${work_home}

COPY deployment/start.sh /start.sh

RUN chmod +x /start.sh

EXPOSE 80

CMD ["/start.sh"]
