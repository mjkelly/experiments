/*
 * Read a switch and blink an LED at one rate if the switch is open, and
 * another if it's closed.
 * 
 * We don't have to wait a full blink cycle to switch the rate, we detect the
 * button press within ~1ms.
 *
 * We don't debounce the input (we just have this silly 1ms delay to filter out
 * a little noise).
 */
const int buttonPin = 7;
const int ledPin = 6;
unsigned long nextFlipTime = 0;
int state = LOW;
int prevButtonState = 0;
unsigned long ticks = 0;

void setup() {
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int delayMs = 500;
  unsigned long now = millis();
  int buttonState = digitalRead(buttonPin);
  unsigned long intervalMs = 0;
  ticks++;
  
  if (buttonState == LOW) {
    intervalMs = 1000;
  } else {
    intervalMs = 100;
  }
  
  if (now >= nextFlipTime) {
    Serial.print("FLIP (");
    Serial.print(ticks);
    Serial.print(")\n");
    if (state == LOW) {
      state = HIGH; 
    } else {
      state = LOW;
    }
    digitalWrite(ledPin, state);
    nextFlipTime = nextFlipTime + intervalMs;
    ticks = 0;
  }

  if (buttonState != prevButtonState) {
    Serial.print(prevButtonState);
    Serial.print(" -> ");
    Serial.print(buttonState);
    Serial.print("\n");
    prevButtonState = buttonState;
    nextFlipTime = now;
  }
  // Instead of real debouncing, we reduce the number of times we poll with a
  // short delay.
  delay(1);
}
