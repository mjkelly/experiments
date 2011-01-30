// constants won't change. Used here to 
// set pin numbers:
const int redLedPin = 2;
const int greenLedPin = 3;
const int yellowLedPin = 4;
const int clockPin = 13;

// digital output
int ledState = LOW;
int clockState = LOW;

// timing (values are ms)
long previousMillis = 0;
long t = 0;
long interval = 500;

int state = 0; // 0 = red, 1 = green, 2 = yellow

void setup() {
  pinMode(redLedPin, OUTPUT);
  pinMode(greenLedPin, OUTPUT);
  pinMode(yellowLedPin, OUTPUT);
}

void loop() {
  t = millis();
  
  if (t- previousMillis > interval) {
    state = (state + 1) % 3;
    // save the last time you blinked the LED 
    previousMillis = t;   
    
    // we indicate timing with the clock LED
    clockState = ~clockState;
    digitalWrite(clockPin, clockState);

    // set the LED with the ledState of the variable:
    switch (state){
      case 0:
        digitalWrite(redLedPin, HIGH);
        digitalWrite(greenLedPin, LOW);
        digitalWrite(yellowLedPin, LOW);
        break;
      case 1:
        digitalWrite(redLedPin, LOW);
        digitalWrite(greenLedPin, HIGH);
        digitalWrite(yellowLedPin, LOW);
        break;
      case 2:
        digitalWrite(redLedPin, LOW);
        digitalWrite(greenLedPin, LOW);
        digitalWrite(yellowLedPin, HIGH);
        break;
    }
  }
}
