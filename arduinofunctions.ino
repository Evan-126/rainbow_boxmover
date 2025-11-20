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

// R2 HIGH TO R2 220
void f() { // forward drive full
  digitalWrite(R2, 220);
  digitalWrite(R1, LOW);
  digitalWrite(L2, HIGH);
  digitalWrite(L1, LOW);
  delay(100);
}

void b() { // backward drive full
  digitalWrite(R2, LOW);
  digitalWrite(R1, HIGH);
  digitalWrite(L2, LOW);
  digitalWrite(L1, HIGH);
  delay(100);
}

void l() {    // left turn (full right forward)
  digitalWrite(R2, 220);
  digitalWrite(R1, LOW);
  digitalWrite(L2, LOW);
  digitalWrite(L1, LOW);
  delay(100);
}

void r() {   // right turn (full left forward)
  digitalWrite(R2, LOW);
  digitalWrite(R1, LOW);
  digitalWrite(L2, HIGH);
  digitalWrite(L1, LOW);
  delay(100);
}

void s() {      //full stop
  digitalWrite(R1, LOW);
  digitalWrite(R2, LOW);
  digitalWrite(L1, LOW);
  digitalWrite(L2, LOW);
  delay(100);
}

void a() {      // approach (slow for 2 cm)
  digitalWrite(ENA, 80);
  digitalWrite(ENB, 80);
  digitalWrite(R2, 220);
  digitalWrite(R1, LOW);
  digitalWrite(L2, HIGH);
  digitalWrite(L1, LOW);
  delay(500);
  digitalWrite(ENA, HIGH);
  digitalWrite(ENB, HIGH);
}

// ------------------------
// Servo Open/Close
// ------------------------
void o() {             // open = 90° clockwise
  myServo.write(60);
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


  // Bluetooth
  Serial.begin(9600);
  mySerial.begin(9600);

  
  // Servo
  myServo.attach(servoPin);
  myServo.write(60);
  c(); // add a little bit of flair
  o();

}

// Main Loop

void loop() {

  // bluetooth commands
  if (mySerial.available()) {       // Check if data received from Bluetooth
    char cmd = mySerial.read();     // Read single character

    if (cmd == 'F') f();            // Move forward
    else if (cmd == 'B') b();       // Move backward
    else if (cmd == 'L') l();       // Turn left
    else if (cmd == 'R') r();       // Turn right
    else if (cmd == 'S') s();       // Stop all motors
    else if (cmd == 'A') a();       // Approach target
    else if (cmd == 'O') o();       // Servo open
    else if (cmd == 'C') c();       // Servo close
  }
  // // servo test
  // o();
  // c();
  // delay(500);

  // motor test
  // f();
  // delay(4000);
  // a();
  // delay(3000);
  // l();
  // delay(4000);
  // s();
  // delay(500);
  // r();
  // delay(4000);
  // s();
  // delay(500);
  s();
}
