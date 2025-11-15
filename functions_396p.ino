#include <Servo.h>
#include <SoftwareSerial.h>

// movement functions up here because setup functino easier if it uses them
void f(){
  digitalWrite(R1, HIGH);
  digitalWrite(R2, LOW);
  digitalWrite(L1, HIGH);
  digitalWrite(L2, LOW);
  delay(100);
}
void b(){
  digitalWrite(R1, LOW);
  digitalWrite(R2, HIGH);
  digitalWrite(L1, LOW);
  digitalWrite(L2, HIGH);
  delay(100);
}
void l(){
  digitalWrite(R1, HIGH);
  digitalWrite(R2, LOW);
  digitalWrite(L1, LOW);
  digitalWrite(L2, LOW);
  delay(100);
}
void r(){
  digitalWrite(R1, LOW);
  digitalWrite(R2, LOW);
  digitalWrite(L1, HIGH);
  digitalWrite(L2, LOW);
  delay(100);
}
void s(){
  digitalWrite(R1, LOW);
  digitalWrite(R2, LOW);
  digitalWrite(L2, LOW);
  digitalWrite(L1, LOW);
  delay(100);
}

void setup() {
  // init serial
  Serial.begin(9600)

  // motor setup
  const int ENA = 3;
  const int R1 = 2;
  const int R2 = 4;
  const int L1 = 6;
  const int L2 = 7;
  const int ENB = 5;

  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(R1, OUTPUT);
  pinMode(R2, OUTPUT);
  pinMode(L1, OUTPUT);
  pinMode(L2, OUTPUT);

  digitalWrite(ENA, HIGH);
  digitalWrite(ENB, HIGH);

  s()

  // servo
  const int servo = 9;

  Servo myServo;

  myServo.attach(servo);

  myServo.write(0)
  // HC-05
  // i lowkey don't know how this works yet
  SoftwareSerial BTSerial(10, 11); // RXD, TXD

}


void loop() {
  // put your main code here, to run repeatedly:

}
