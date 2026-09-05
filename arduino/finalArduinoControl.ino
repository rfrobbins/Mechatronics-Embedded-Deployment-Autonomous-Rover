#include <Servo.h> 
#include <stdlib.h>
#include <string.h>

//===================================================
//Initialize & Set Parameters
//===================================================

Servo left1; 
Servo left2; 
Servo right3; 
Servo right4; 

//Arduino physical output pins 
const byte LEFT_M1 = 2; 
const byte LEFT_M2 = 3;
const byte RIGHT_M3 = 12;
const byte RIGHT_M4 = 13;

//Baud rate
const unsigned long BAUD = 115200; 

//PWM Nuetral us
const int NEUTRAL = 1500; 

//PWM Delta Value
const int DELTA = 500; 

//SOFTWARE POWER LIMITER (Value is percentage of full power)
const int POWER_LIMIT = 40;

//Min and max power calculated based on power limit percentage. 
const int MIN = NEUTRAL - (DELTA * POWER_LIMIT / 100); 
const int MAX = NEUTRAL + (DELTA * POWER_LIMIT / 100);

//Failsafe time
const unsigned long FAILSAFE = 500; 

char buffer[32]; 
byte bufferIndex = 0; 

unsigned long lastCommandTime = 0; 

//===================================================
//Power Inversion 
//Motors are set up so each gearbox has one inverted. 
//===================================================
const bool INVERT_LEFT_M1  = false;
const bool INVERT_LEFT_M2  = true;
const bool INVERT_RIGHT_M3 = true;
const bool INVERT_RIGHT_M4 = true;

int invertPulse(int pulse, bool invert){
  if(!invert){
    return pulse; 
  }
  // Min becomes max, and max becomes min. 
  return (2 * NEUTRAL) - pulse;
}

//===================================================
//Set PWM For Left and Right Gearboxes
//===================================================

void setMotors(int leftPWM, int rightPWM){
  //constrain to min and max us
  leftPWM = constrain(leftPWM, MIN, MAX); 
  rightPWM = constrain(rightPWM, MIN, MAX); 

  //Write Left Motors 
  left1.writeMicroseconds(invertPulse(leftPWM, INVERT_LEFT_M1)); 
  left2.writeMicroseconds(invertPulse(leftPWM, INVERT_LEFT_M2)); 

  //Write Right Motors 
  right3.writeMicroseconds(invertPulse(rightPWM, INVERT_RIGHT_M3)); 
  right4.writeMicroseconds(invertPulse(rightPWM, INVERT_RIGHT_M4)); 
}

void neutral(){
  setMotors(NEUTRAL,NEUTRAL); 
}

//===================================================
//Process Jetson Commands 
//Excepted Format: leftPWM_us,rightPWM_us
//===================================================

void processCommand(char *command){
  //find comma address
  char *comma = strchr(command, ','); 

  if(comma == NULL){
    Serial.println("ERROR: Invalid command format.");
    return; 
  }
  *comma = '\0'; //split command at comma

  int leftPWM = atoi(command); 
  int rightPWM = atoi(comma+1); 

  //Make sure commands are within excpeted PWM us values
  if(leftPWM < 1000 || leftPWM > 2000 || rightPWM < 1000 || rightPWM > 2000){
     Serial.println("ERROR: Invalid command.");
     return; 
  }

  setMotors(leftPWM, rightPWM); 

  lastCommandTime = millis(); 
}

//===================================================
//Setup
//===================================================

void setup(){
  
  Serial.begin(BAUD); 

  left1.attach(LEFT_M1); 
  left2.attach(LEFT_M2); 
  right3.attach(RIGHT_M3); 
  right4.attach(RIGHT_M4);
  
  neutral(); //send neutral command on startup

  lastCommandTime = millis(); 

  Serial.println("ARDUINO READY");
}

//===================================================
//Read Jetson Commands
//===================================================

void loop(){
  while(Serial.available()> 0){
    char jetsonCommand = Serial.read(); 

    if(jetsonCommand == '\n'){ //Newline indicates the end of a command
      buffer[bufferIndex] = '\0'; //Add a newline to the array to make it a readable string 

      if(bufferIndex > 0){ 
        processCommand(buffer); 
      }
      bufferIndex = 0; //erase command from buffer
    }
    else if(jetsonCommand != '\r'){
      if(bufferIndex < sizeof(buffer)-1){
        buffer[bufferIndex] = jetsonCommand; 
        bufferIndex++; 
      }
      else{ //oversized command 
        bufferIndex = 0; 
        Serial.println("ERROR: Command too long.");
      }
    }
  }
  //Failsafe 
  if(millis() - lastCommandTime > FAILSAFE){
  neutral();
  }
}
