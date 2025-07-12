#include <Wire.h>
#include <MPU9250_asukiaaa.h>
#include <Servo.h>

#define EN1 5
#define EN2 6
#define m11 7
#define m12 8
#define m21 3
#define m22 10
#define trigpin 11
#define echopin 12

MPU9250_asukiaaa gyro_sensor;
enum komut_verileri {ileri__git, sola__don, saga__don, dur__, geri__don};
Servo servo_motor; 

bool veri_gonderimi_bitti=false;
int input [4]={};
int n = 0;

const float Kp_sag = 8;
const float Kp_sol = 8;
const float Kp_geri = 8;

const float Kp_m = 5;
const float Ki_m = 0.8; 
const float Ki_sol = 1.5;
const float Ki_sag = 1.7;  
const float tolerans_aci = 3.0;      
const float tolerans_mesafe = 5.0;
const int sabit_hiz = 170;
const int max_pwm = 170;          
const double hedef_mesafe = 8;
bool donus_yapilamaz = false;
void setup() {
  servo_motor.attach(9);
  Serial.begin(9600);
  Wire.begin();
  servo_motor.write(90);
  delay(100);

  pinMode(m11, OUTPUT);
  pinMode(m12, OUTPUT);
  pinMode(m21, OUTPUT);
  pinMode(m22, OUTPUT);
  pinMode(EN1, OUTPUT);
  pinMode(EN2, OUTPUT);

  gyro_sensor.setWire(&Wire);
  gyro_sensor.beginAccel();
  gyro_sensor.beginGyro();
  gyro_sensor.beginMag();

  delay(2000);

  pinMode(trigpin, OUTPUT);
  pinMode(echopin, INPUT);
}

void loop() {

  while (Serial.available()) {
    input[n] = Serial.read();

    if (input[n] == 9) { 
      n = 0;
      veri_gonderimi_bitti = true;
    } else {
      n++;
    }
  }
//input[0]: komut (0: ileri git , 1: sola dön, 2: sağa dön, 3: geri dön)
//input[1]: kosul (0: koşul yok, 1: engel algılayana kadar, 2: engelin solundan kurtul, 3: engelin sagından kurtul)
//input[2]: süre (saniye cinsinden süre yazılır)
//input[3]: mesaj sonu 9 ile belirtilir. 
  if (veri_gonderimi_bitti) {
    veri_gonderimi_bitti = false;

    switch (input[0]) {
      case ileri__git:
      
        ileri_git(input[1], input[2] * 1000);
        break;

      case sola__don:
        sola_don();
        break;

      case saga__don:
        saga_don();
        break;

      case dur__:
        dur(input[2] * 1000);
        break;
        
      case geri__don:
        geri_don();
        break;    
    }
     
    delay(1000);
    Serial.write(1);
  }
 
}


void ileri_git(int kosul, int hedef_zaman) {
    
    digitalWrite(m11, HIGH);
    digitalWrite(m12, LOW);
    digitalWrite(m21, HIGH);
    digitalWrite(m22, LOW);

    unsigned long zaman = millis();
    unsigned long baslangic_zamani = millis();
    double mesafe_hata = 0;
    int m_hiz = 0;
    double mesafe = 0;
    double integral = 0;
    double mesafe_yan = 0;
    double mesafe_on = 0;
    double onceki_zaman = millis();
    int devam1 = 0;
    int devam2 = 0;
   

    while(((zaman-baslangic_zamani)<hedef_zaman)||hedef_zaman==0){
    zaman = millis();
    
      
        mesafe=mesafe_olcumu();
        mesafe_hata=mesafe-hedef_mesafe;
    
        if(mesafe > 30)
          m_hiz=sabit_hiz;
        else{  

          unsigned long guncel_zaman = millis();       
          double gecen_zaman = (guncel_zaman - onceki_zaman) / 1000.0;
          onceki_zaman = guncel_zaman;
          integral += mesafe_hata * gecen_zaman;       
          m_hiz= constrain(abs(mesafe_hata) * Kp_m + Ki_m*integral, 0, max_pwm);

        }

        if(mesafe_hata<tolerans_mesafe && mesafe > 0){

          dur(0);
          delay(500);
          if(kosul>1){

            
            if(kosul==2){
              
              devam1 = sola_don();
              if(!devam1)
                break;
              delay(1000);
              servo_motor.write(180);
              delay(500);
              
            }  
            else{
              devam1 = saga_don();
              if(!devam1)
                break;
              delay(1000);
              servo_motor.write(0);
              delay(500);
            
              
              
            }
            delay(500);

            while(1){
              mesafe_yan = mesafe_olcumu();
              delay(100);
              servo_motor.write(90);
              delay(300);
              mesafe_on = mesafe_olcumu();
              delay(300);
              servo_motor.write(180*(3-kosul));
              if(mesafe_yan<50 && mesafe_on > 60){
              digitalWrite(m11, HIGH);
              digitalWrite(m12, LOW);
              digitalWrite(m21, HIGH);
              digitalWrite(m22, LOW);

              int mevcut_pwm = 100;
              while (mevcut_pwm <= 140) {
                analogWrite(EN1, mevcut_pwm);
                analogWrite(EN2, mevcut_pwm);
                mevcut_pwm += 10;
                if (mevcut_pwm < 140)
                  delay(50); 
                else 
                  delay(100);
              }

              dur(0);
              delay(100);
              }
              else if (mesafe_yan>= 50 && mesafe_on > 60)
              {
                servo_motor.write(90);
                delay(100);
                break;
              }
              else{
                dur(0);
                servo_motor.write(90);
                delay(100);
                donus_yapilamaz = true;
                break;
              }
              
            }

            if(donus_yapilamaz){
              donus_yapilamaz=false;
              break;
            }  
            dur(0);
            delay(500);
            digitalWrite(m11, HIGH);
            digitalWrite(m12, LOW);
            digitalWrite(m21, HIGH);
            digitalWrite(m22, LOW);
            analogWrite(EN1, 150);
            analogWrite(EN2, 150);          
            delay(750);
            dur(0);
            delay(500);
            if(kosul==2){
              
              
              devam2 = saga_don();
              if(!devam2)
                break;
              delay(200);

            }  
            else if(kosul==3){
              
              devam2 = sola_don();
              if(!devam2)
                break;
              delay(200);

                
            }

          }
          break;
        }
      analogWrite(EN1, m_hiz-20);
      analogWrite(EN2, m_hiz);
    
  }
    if(hedef_zaman > 0){
      digitalWrite(m11, LOW);
      digitalWrite(m12, LOW);
      digitalWrite(m21, LOW);
      digitalWrite(m22, LOW);
      analogWrite(EN1, 0);
      analogWrite(EN2, 0);
    }
}



void dur(int hedef_zaman) {
  digitalWrite(m11, LOW);
  digitalWrite(m12, LOW);
  digitalWrite(m21, LOW);
  digitalWrite(m22, LOW);
  analogWrite(EN1, 0);
  analogWrite(EN2, 0);
  delay(hedef_zaman);
}

double mesafe_olcumu() {
  digitalWrite(trigpin, LOW);
  delayMicroseconds(5);
  digitalWrite(trigpin, HIGH);
  delayMicroseconds(15);
  digitalWrite(trigpin, LOW);

  long sure = pulseIn(echopin, HIGH, 100000); 
  if (sure == 0) {
   
    return -1; 
  }

  double mesafe = sure * 0.0343 / 2;
  return mesafe;
}


int sola_don() {
      delay(500);
      digitalWrite(m11, HIGH);
      digitalWrite(m12, LOW);
      digitalWrite(m21, LOW);
      digitalWrite(m22, HIGH);
      float donus_acisi = 0.0;
      float hedef_aci = -90;        
      unsigned long son_zaman = millis();
      double mesafe_sol = 0;
      double mesafe_sag = 0;
      unsigned long zaman = millis();
      unsigned long baslangic_zamani = millis(); 
      double integral = 0; 
      double onceki_zaman = millis();    
      servo_motor.write(0);
      delay(800);
      mesafe_sol = mesafe_olcumu();
      delay(800);
      servo_motor.write(90);
      delay(800);
      servo_motor.write(180);
      delay(800);
      mesafe_sag = mesafe_olcumu();
      delay(800);
      servo_motor.write(90);
      delay(100);

      while(1){
        zaman=millis();
        if(mesafe_sol > 15 && mesafe_sag > 10) {
          gyro_sensor.gyroUpdate();
          float gz = gyro_sensor.gyroZ();
          if (abs(gz) < 0.5) gz = 0;

          unsigned long guncel_zaman = millis();
          float dt = (guncel_zaman - son_zaman) / 1000.0;
          son_zaman = guncel_zaman;

          donus_acisi += gz * dt;
          float hata = hedef_aci - donus_acisi;

          if (-hata <= 8 ) { 
            dur(0);
            return 1;
          }
          unsigned long integral_guncel_zaman = millis();       
          double gecen_zaman = (integral_guncel_zaman - onceki_zaman) / 1000.0;
          onceki_zaman = integral_guncel_zaman;
          integral -= hata * gecen_zaman;       
          int hiz = constrain(abs(hata) * Kp_sol + Ki_sol*integral, 0, max_pwm);

          analogWrite(EN1, hiz);
          analogWrite(EN2, hiz);
          delay(10);
        }
        else {
          
          dur(0);
         
         return 0;
        }
      }
      dur(0);
    
}


int saga_don() {

      delay(500);
      digitalWrite(m11, LOW);
      digitalWrite(m12, HIGH);
      digitalWrite(m21, HIGH);
      digitalWrite(m22, LOW);
      float donus_acisi = 0.0;
      float hedef_aci = 90;         
      unsigned long son_zaman = millis();
      double mesafe_sag = 0;
      double mesafe_sol = 0;
      unsigned long zaman = millis();
      unsigned long baslangic_zamani = millis(); 
      double integral = 0;
      double onceki_zaman = millis();      
      servo_motor.write(180);
      delay(800);
      mesafe_sag = mesafe_olcumu();
      delay(800);
      servo_motor.write(90);
      delay(800);
      servo_motor.write(0);
      delay(800);
      mesafe_sol = mesafe_olcumu();
      delay(300);
      servo_motor.write(90);
      delay(100);
      

      while(1){ 
        zaman=millis();
        if (mesafe_sag > 15 && mesafe_sol > 10) {
          gyro_sensor.gyroUpdate();

          float gz = gyro_sensor.gyroZ();
          if (abs(gz) < 0.5) gz = 0;

          unsigned long guncel_zaman = millis();
          float dt = (guncel_zaman - son_zaman) / 1000.0;
          son_zaman = guncel_zaman;

          donus_acisi += gz * dt;
          float hata = hedef_aci - donus_acisi;

          if (hata <= tolerans_aci ) { 
            dur(0);
            return 1;
          }
          unsigned long integral_guncel_zaman = millis();       
          double gecen_zaman = (integral_guncel_zaman - onceki_zaman) / 1000.0;
          onceki_zaman = integral_guncel_zaman;
          integral += hata * gecen_zaman;       
          int hiz = constrain(abs(hata) * Kp_sag + Ki_sag*integral, 0, max_pwm);

          analogWrite(EN1, hiz);
          analogWrite(EN2, hiz);
          delay(10);
        }
        else{
          dur(0);
          return 0;
        }
      }
      dur(0);
    
}

void geri_don(){
      delay(500);
      digitalWrite(m11, LOW);
      digitalWrite(m12, HIGH);
      digitalWrite(m21, HIGH);
      digitalWrite(m22, LOW);
      float donus_acisi = 0.0;
      float hedef_aci = 180;         
      unsigned long son_zaman = millis();
      double mesafe_sag = 0;
      double mesafe_sol = 0;
      unsigned long zaman = millis();
      unsigned long baslangic_zamani = millis(); 
      double integral = 0;
      double onceki_zaman = millis();      
      servo_motor.write(180);
      delay(800);
      mesafe_sag = mesafe_olcumu();
      delay(800);
      servo_motor.write(90);
      delay(800);
      servo_motor.write(0);
      delay(800);
      mesafe_sol = mesafe_olcumu();
      delay(800);
      servo_motor.write(90);
      delay(100);
      
      while(1){ 
        zaman=millis();
        if (mesafe_sag > 15 && mesafe_sol > 10) {
          gyro_sensor.gyroUpdate();
          float gz = gyro_sensor.gyroZ();
          if (abs(gz) < 0.5) gz = 0;

          unsigned long guncel_zaman = millis();
          float dt = (guncel_zaman - son_zaman) / 1000.0;
          son_zaman = guncel_zaman;

          donus_acisi += gz * dt;
          float hata = hedef_aci - donus_acisi;

          if (hata <= -0.5) {
            dur(0);
            break;
          }
          unsigned long integral_guncel_zaman = millis();       
          double gecen_zaman = (integral_guncel_zaman - onceki_zaman) / 1000.0;
          onceki_zaman = integral_guncel_zaman;
          integral += hata * gecen_zaman;       
          int hiz = constrain(abs(hata) * Kp_geri + Ki_sag*integral, 0, max_pwm);

          analogWrite(EN1, hiz);
          analogWrite(EN2, hiz);
          delay(10);
        }
        else{
          dur(0);
          break;
        }
      }
      dur(0);
    
}

