#include <Servo.h>
#include <SoftwareSerial.h>

// motors init
const int ENA = 3;
const int R1  = 2;
const int R2  = 4;
const int L1  = 6;
const int L2  = 7;
const int ENB = 5;

//servo init
Servo myServo;

const int servoPin = 9;

// HC-05 init
#define TXD 10
#define RXD 11

SoftwareSerial mySerial(RXD, TXD);  // RX, TX

// ------------------------
// Movement Functions
// ------------------------

void f() {
  digitalWrite(R2, HIGH);
  digitalWrite(R1, LOW);
  digitalWrite(L2, HIGH);
  digitalWrite(L1, LOW);
  delay(100);
}

void b() {
  digitalWrite(R2, LOW);
  digitalWrite(R1, HIGH);
  digitalWrite(L2, LOW);
  digitalWrite(L1, HIGH);
  delay(100);
}

void l() {
  digitalWrite(R2, HIGH);
  digitalWrite(R1, LOW);
  digitalWrite(L2, LOW);
  digitalWrite(L1, LOW);
  delay(100);
}

void r() {
  digitalWrite(R2, LOW);
  digitalWrite(R1, LOW);
  digitalWrite(L2, HIGH);
  digitalWrite(L1, LOW);
  delay(100);
}

void s() {
  digitalWrite(R1, LOW);
  digitalWrite(R2, LOW);
  digitalWrite(L1, LOW);
  digitalWrite(L2, LOW);
  delay(100);
}

// ------------------------
// Servo Open/Close
// ------------------------
void o() {             // open = 90° clockwise
  myServo.write(80);
  delay(300);
}

void c() {             // close = 90° counterclockwise
  myServo.write(160);
  delay(300);
}

// ------------------------
// Setup
// ------------------------
void setup() {
  // Motor pins
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(R1, OUTPUT);
  pinMode(R2, OUTPUT);
  pinMode(L1, OUTPUT);
  pinMode(L2, OUTPUT);

  digitalWrite(ENA, HIGH);
  digitalWrite(ENB, HIGH);

  // s();  // stop motors at start

  // Servo
  myServo.attach(servoPin);
  myServo.write(80);
  // c(); // add a little bit of flair
  // o();

  // Bluetooth
  Serial.begin(9600);
  mySerial.begin(9600);

}

// ------------------------
// Main Loop
// ------------------------
void loop() {

  // bluetooth commands
  if (mySerial.available()) {       // Check if data received from Bluetooth
    char cmd = mySerial.read();     // Read single character

    if (cmd == 'f') f();            // Move forward
    else if (cmd == 'b') b();       // Move backward
    else if (cmd == 'l') l();       // Turn left
    else if (cmd == 'r') r();       // Turn right
    else if (cmd == 's') s();       // Stop all motors
    else if (cmd == 'o') o();       // Servo open
    else if (cmd == 'c') c();       // Servo close
  }
  // // servo test
  // o();
  // c();
  // delay(500);

  // // motor test
  // // f();
  // // delay(1000);
  // s();
}
