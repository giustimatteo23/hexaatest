FROM debian:latest

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev dpkg git

#TODO APACHE

#apache2 setup
RUN mkdir -p /var/lock/apache2
RUN mkdir -p /var/run/apache2
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_PID_FILE /var/run/apache2.pid
ENV APACHE_RUN_DIR /var/run/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_LOG_DIR /var/log/apache2
ENV LANG C

#PYTHON
RUN wget https://www.python.org/ftp/python/3.10.5/Python-3.10.5.tgz
RUN tar -xf Python-3.10.5.tgz
WORKDIR Python-3.10.5
RUN ./configure --enable-optimizations
RUN make -j 4
RUN make altinstall
RUN python3.10 --version
RUN apt-get -y install python3-pip
RUN pip install selenium webdriver_manager
RUN pip install virtualenv
RUN virtualenv selenv

RUN apt-get install python3-venv -y
ENV VIRTUAL_ENV=/root/Python-3.10.5/selenv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR selenv/
RUN mkdir tester
WORKDIR tester/
RUN 
#TODO install the program from git
