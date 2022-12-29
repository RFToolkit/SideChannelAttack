#include <SPI.h>
#include "RF24.h"
#include "nRF24L01.h"

RF24 radio(9, 10);
const byte address[6] = "00001";
int i = 0;

void setup() {
	radio.begin();
	radio.openWritingPipe(address);
	radio.stopListening();
}

void loop() {
	const char text[32] = {'\0'};
	sprintf(text, "%d", i++);
	radio.write(&text, strlen(text) * sizeof(char));

	delay(1000);
}