FROM ubuntu

RUN apt update &&\
    apt install -y gcc-avr binutils-avr avr-libc avrdude python3

RUN python -m pip install pyserial
