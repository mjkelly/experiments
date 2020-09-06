
//// the setup function runs once when you press reset or power the board
//void setup() {
//  // initialize digital pin LED_BUILTIN as an output.
//  pinMode(LED_BUILTIN, OUTPUT);
//}
//
//// the loop function runs over and over again forever
//void loop() {
//  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
//  delay(1000);                       // wait for a second
//  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
//  delay(1000);                       // wait for a second
//}


const int buttonPin = 7;
const int ledPin = 6;
unsigned long nextFlipTime = 0;
int state = LOW;
int prevButtonState = 0;

void setup() {
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);
//  pinMode(greenPin, OUTPUT);
//  pinMode(bluePin, OUTPUT);
//  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int delayMs = 500;
  unsigned long now = millis();
  int buttonState = digitalRead(buttonPin);
  unsigned long intervalMs = 0;
  
  if (buttonState == LOW) {
    intervalMs = 1000;
  } else {
    intervalMs = 100;
  }
  
  Serial.print(now);
  Serial.print(" (t)-> ");
  Serial.print(nextFlipTime);
  Serial.print("\n");
  if (now >= nextFlipTime) {
    Serial.print("*** FLIP ***\n");
    if (state == LOW) {
      state = HIGH; 
    } else {
      state = LOW;
    }
    digitalWrite(ledPin, state);
    nextFlipTime = nextFlipTime + intervalMs;
  }

  if (buttonState != prevButtonState) {
    Serial.print(prevButtonState);
    Serial.print(" -> ");
    Serial.print(buttonState);
    Serial.print("\n");
    prevButtonState = buttonState;
    nextFlipTime = now;
  }
  delay(10);

}
