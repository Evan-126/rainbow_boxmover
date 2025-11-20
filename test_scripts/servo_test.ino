#include <Servo.h>

Servo myServo;

const int servoPin = 9; // Servo control pin

void setup() {
  myServo.attach(servoPin);
  
//  Test "open" position
  myServo.write(0);    // Set to open
  delay(1000);          // Hold position for 1 second

  // Test "close" position
  myServo.write(160);   // Set to close
  delay(1000);          // Hold for 1 second
}

void loop() {
  Optionally, you can repeatedly test open/close in the loop:
  myServo.write(60);     // Open
  delay(1000);
  myServo.write(160);    // Close
  delay(1000);
}
