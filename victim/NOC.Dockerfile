FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Paris

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update &&\
    apt install -y gcc-avr binutils-avr avr-libc avrdude python3 python3-pip wget unzip \
    libgtk3* libxshmfence-dev libnss3* libsecret-1-dev libasound-dev libgbm-dev libnss3 \
    libxshmfence-dev

RUN python3 -m pip install pyserial

ENV VERSION arduino-ide_2.0.3_Linux_64bit

RUN mkdir -p /opt/install /root/.arduino15/ && cd /opt/install &&\
    wget https://downloads.arduino.cc/arduino-ide/${VERSION}.zip &&\
    unzip ${VERSION}.zip && cd ${VERSION} &&\
    touch /root/.arduino15/package_index.json

RUN echo "/opt/install/${VERSION}/arduino-ide --no-sandbox" >> /usr/bin/arduino /bin/arduino &&\
    chmod +x /usr/bin/arduino /bin/arduino /opt/install/${VERSION}/arduino-ide
