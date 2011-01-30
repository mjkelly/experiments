// constants won't change. Used here to 
// set pin numbers:

#define COUNTER_WIDTH 4
const int outPins[COUNTER_WIDTH] = {2, 3, 4, 5};

int outVals[COUNTER_WIDTH] = {LOW, LOW, LOW, LOW};
long counter = 0;


int clockState = LOW;
int clockPin = 13;


long previousMillis = 0;
long t = 0;
long interval = 1000;

int i;

void setPinsFromCounter(long c) {
  for (i = 0; i < COUNTER_WIDTH; i++) {
    outVals[i] = (c & (1 << i)) ? HIGH : LOW; 
  }
}

void writePins() {
 for (i = 0; i < COUNTER_WIDTH; i++) {
    digitalWrite(outPins[i], outVals[i]);
  }
}

void setup() {
  for (i = 0; i < COUNTER_WIDTH; i++) {
    pinMode(outPins[i], OUTPUT);
  }
  setPinsFromCounter(counter);
  writePins();
}

void loop() {
  t = millis();
  
  if (t - previousMillis > interval) {
    // save the last time you blinked the LED 
    previousMillis = t;   
    
    // we indicate timing with the clock LED
    clockState = ~clockState;
    digitalWrite(clockPin, clockState);
    
    setPinsFromCounter(counter++);
    writePins();

  }
}
