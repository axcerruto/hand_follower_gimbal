/*
* Created by Antonio X Cerruto 21 Jan 2024
*/
const int BUFFER_SIZE = 4;
char buf[BUFFER_SIZE];
void setup(){
  Serial.begin(250000);
  while (!Serial) {
    ;  // wait for serial port to connect. Needed for native USB port only
  }
}
 
void loop(){ 
  if(Serial.available() > BUFFER_SIZE-1){
    Serial.readBytes(buf, BUFFER_SIZE);
    Serial.println(buf);
    /*
    YOUR CODE HERE:
    Parse serial data and control stepper motors accordingly.
    Input data format examples: 
    'P120' - set pitch angle to 120 degrees
    'Y93' - set yaw angle to 93 degrees
    */
  }
}
