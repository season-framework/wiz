FROM ubuntu:latest
ENV LANG=ko_KR.UTF-8 LC_ALL=ko_KR.UTF-8

RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install libfontenc1 libxfont2 xfonts-encodings xfonts-utils xfonts-base xfonts-75dpi language-pack-ko -y
RUN apt-get install fonts-nanum fonts-nanum-coding fonts-nanum-extra -y
RUN apt-get install pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl -y
RUN apt-get install curl wget net-tools build-essential zip unzip git -y

RUN apt-get install npm -y
RUN npm i -g n
RUN n lts
RUN apt-get purge nodejs npm -y

RUN cd /opt && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /opt/Miniconda3-latest.sh && \
    /bin/bash /opt/Miniconda3-latest.sh -b -p /opt/conda && \
    rm /opt/Miniconda3-latest.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc

ENV PATH /opt/conda/bin:$PATH
RUN pip install season python3-saml gevent-websocket redis flask_session flask-socketio dizest

WORKDIR /opt
RUN wiz create app

WORKDIR /opt/app
CMD [ "wiz", "run", "--port", "3000" ]

EXPOSE 3000/tcp