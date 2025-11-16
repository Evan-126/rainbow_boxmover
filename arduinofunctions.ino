#include <Servo.h>
#include <SoftwareSerial.h>

const int ENA = 3;
const int R1  = 2;
const int R2  = 4;
const int L1  = 6;
const int L2  = 7;
const int ENB = 5;

const int servoPin = 9;

#define TXD 10
#define RXD 11

Servo myServo;
SoftwareSerial mySerial(RXD, TXD);  // RX, TX

void f() {
  digitalWrite(R1, HIGH);
  digitalWrite(R2, LOW);
  digitalWrite(L1, HIGH);
  digitalWrite(L2, LOW);
  delay(100);
}

void b() {
  digitalWrite(R1, LOW);
  digitalWrite(R2, HIGH);
  digitalWrite(L1, LOW);
  digitalWrite(L2, HIGH);
  delay(100);
}

void l() {
  digitalWrite(R1, HIGH);
  digitalWrite(R2, LOW);
  digitalWrite(L1, LOW);
  digitalWrite(L2, LOW);
  delay(100);
}

void r() {
  digitalWrite(R1, LOW);
  digitalWrite(R2, LOW);
  digitalWrite(L1, HIGH);
  digitalWrite(L2, LOW);
  delay(100);
}

void s() {
  digitalWrite(R1, LOW);
  digitalWrite(R2, LOW);
  digitalWrite(L1, LOW);
  digitalWrite(L2, LOW);
  delay(100);
}

void o() {                // open = 90° clockwise
  myServo.write(90);
  delay(300);
}

void c() {                // close = 90° counterclockwise
  myServo.write(0);
  delay(300);
}

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

  s();  // stop motors at start

  // Servo
  myServo.attach(servoPin);
  myServo.write(0);

  // Bluetooth
  Serial.begin(9600);
  mySerial.begin(9600);
}

// ------------------------
// Main Loop
// ------------------------
void loop() {

}
