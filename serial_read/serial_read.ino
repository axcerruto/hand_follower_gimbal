/*
* Created by Antonio X Cerruto 21 Jan 2024
*/

void setup(){
  Serial.begin(9600);
  while (!Serial) {
    ;  // wait for serial port to connect. Needed for native USB port only
  }
}
 
void loop()
{ 
  digitalWrite(m1EnPin, HIGH);
  motor1.step(stepsPerRevolution);
  digitalWrite(m1EnPin, LOW);
  delay(2000);
}
