FINWARE_NAME=node-master

compile:
	avr-gcc -Os -DF_CPU=16000000UL -mmcu=atmega328p -c -o ${FINWARE_NAME}.o ${FINWARE_NAME}.cpp

generate:
	avr-gcc -mmcu=atmega328p ${FINWARE_NAME}.o -o ${FINWARE_NAME}

hex:
	avr-objcopy -O ihex -R .eeprom ${FINWARE_NAME} ${FINWARE_NAME}.hex

upload: 
	avrdude -F -V -c arduino -p ATMEGA328P -P /dev/ttyACM0 -b 115200 -U flash:w:${FINWARE_NAME}.hex

all: compile generate hex upload