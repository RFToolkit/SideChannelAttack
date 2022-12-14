#include "RF24.h"
#include "nRF24L01.h"

RF24 radio(9, 10);
const byte address[6] = "00001";

void setup() {
	Serial.begin(9600);

	radio.begin();
	radio.openReadingPipe(0, address);
	radio.startListening();
}

void loop() {
	if (radio.available()) {
		char text[32] = {'\0'};
		radio.read(&text, sizeof(text));
		Serial.println(text);
	}
}