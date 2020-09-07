/*
 * Read a switch and blink an LED at one rate if the switch is open, and
 * another if it's closed.
 * 
 * We don't have to wait a full blink cycle to switch the rate, we detect the
 * button press within the debounce interval. This version uses a debounce
 * library to make things much simpler.
 */

#include "FTDebouncer.h"

const int BUTTON_PIN = 7;
const int LED_PIN = 6;
const int INTERVAL_HIGH = 1000;
const int INTERVAL_LOW = 100;

unsigned long nextFlipTime = 0;
int ledState = HIGH;
unsigned long ticks = 0;
unsigned long intervalMs = INTERVAL_HIGH;

FTDebouncer pinDebouncer;

void setup() {
  pinDebouncer.addPin(BUTTON_PIN, HIGH, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  pinDebouncer.begin();
  Serial.begin(9600);

  // Make sure we start in the correct state
  int buttonState = digitalRead(BUTTON_PIN);
  if (buttonState == HIGH)  {
    onPinDeactivated(BUTTON_PIN);
  } else {
    onPinActivated(BUTTON_PIN);
  }
}

void loop() {
  unsigned long now = millis();
  ticks++;
  pinDebouncer.update();
  
  if (now >= nextFlipTime) {
    Serial.print("FLIP (");
    Serial.print(ticks);
    Serial.print(")\n");
    if (ledState == LOW) {
      ledState = HIGH; 
    } else {
      ledState = LOW;
    }
    digitalWrite(LED_PIN, ledState);
    nextFlipTime = nextFlipTime + intervalMs;
    ticks = 0;
  }
}

void onPinActivated(int pinNumber){
  Serial.print("pin up\n");
  if (pinNumber == BUTTON_PIN) {
    intervalMs = INTERVAL_HIGH;
    nextFlipTime = millis();
  }
}

void onPinDeactivated(int pinNumber){
  Serial.print("pin down\n");
  if (pinNumber == BUTTON_PIN) {
    intervalMs = INTERVAL_LOW;
    nextFlipTime = millis();
  }
}
