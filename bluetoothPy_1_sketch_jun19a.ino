// Объявление внешних подключений
#include <GyverPID.h>
GyverPID pid;
const int analogInPin = A5;  // Разъем для подключения аналогового датчика
const int Fs = 5;          // Частота дискретизации сигнала (Гц)
// Объявление переменных
//int sensorValue = 0;         // Результат измерения
uint32_t ms_old = 0;         // Время предыдущего измерения
// Процедура инициализации
#define VREF 5.04      // точное напряжение на пине 5V (в данном случае зависит от стабилизатора на плате Arduino)
#define DIV_R1 1000000  // точное значение 10 кОм резистора
#define DIV_R2 1000000   // точное значение 4.7 кОм резистора
void setup() {
  
  pinMode( analogInPin, INPUT );// Настройка ввода аналоговой части 
  
  ms_old = millis();          // Инициализировать предыдущее время измерения текущим временем в мс
  pid.Kp = 1700;
  pid.Ki = 10;
  pid.Kd = 10;
  pid.setDt(1);
  pid.setDirection(NORMAL);
  pid.setpoint = 3.4;
  Serial.begin(9600);          // Настройка скорости передачи на ПК (бод)
  Serial.setTimeout(50);
  Serial.println("input, output, integral, setpoint");
}
// Главный цикл работы
void loop() {
  

 pidCountrol();
 parsing();
}
// ПДИ резулятор
void pidCountrol() {
  static uint32_t tmr;
  static uint32_t tmr2;
  
  if (millis() - tmr>1) {
    tmr = millis();
    pid.input = (int)analogRead(analogInPin) * VREF * ((DIV_R1 + DIV_R2) / DIV_R2) / 1024;
    pid.getResult();
    pid.getResult();
    
    analogWrite(5, pid.output);
   
  }
  if (millis() - tmr2>1000) {
    tmr2 = millis();
   Serial.print(pid.input); Serial.print('#');
    Serial.print(pid.output); Serial.print('#');
    Serial.print(pid.integral); Serial.print('#');
    Serial.println(pid.setpoint);
   
  }
    
}
// Обратная связь для регулирования напряжения на выводе
void parsing(){
  static uint32_t tmr3;
  if (Serial.available() > 1) {
    char incoming = Serial.read();
    float value = Serial.parseFloat();
    switch (incoming){
      case '1': pid.Kp = value; break;      
      case '2': pid.Ki = value; break;
      case '3': pid.Kd = value; break;
      case '4': pid.setpoint = value; break;
    }
  
    if (millis() - tmr3>1000){
      tmr3 = millis();
      Serial.print('9'); Serial.print('#'); 
    Serial.print(pid.Kp); Serial.print('#');     
    Serial.print(pid.Ki);Serial.print('#');
    Serial.print(pid.Kd);Serial.print('#');
    Serial.println(pid.setpoint);
    }
  }
}
