#define MACADDRESS 0x00,0x01,0x02,0x03,0x04,0x05
#define MYIPADDR 192,168,0,15
#define MYIPMASK 255,255,255,0
#define MYDNS 192,168,0,1
#define MYGW 192,168,0,1
#define LISTENPORT 1000
#define UARTBAUD 115200

#define N_TEMPERATURE 3

//we will use the uipethernet that uses the pins 10,11,12,13
//also we use the library onewire and the dallastemperature

#include <UIPEthernet.h>
// The connection_data struct needs to be defined in an external file.
#include <UIPServer.h>
#include <UIPClient.h>
#include "utility/logging.h"
#include <OneWire.h>
#include <DallasTemperature.h>

//more definitions 
const byte DQ_data_pin = 9; //one wire
const byte switch_pin= A5, inv_switch_pin = A3;

OneWire onewire(DQ_data_pin);
DallasTemperature ds18b20(&onewire);
float temperature[N_TEMPERATURE] = {};
int voltage[2] = {};


uint8_t mac[6] = {MACADDRESS};
uint8_t myIP[4] = {MYIPADDR};
uint8_t myMASK[4] = {MYIPMASK};
uint8_t myDNS[4] = {MYDNS};
uint8_t myGW[4] = {MYGW};

EthernetServer server = EthernetServer(LISTENPORT);

void read_temperature(unsigned char number, float* temperature, DallasTemperature sensor){
  sensor.requestTemperatures();
  for(int i=0; i<number; i++){
    temperature[i] = sensor.getTempCByIndex(i);
  }
}

void read_voltage(int* output){
  output[1] = analogRead(switch_pin);
  output[2] = analogRead(inv_switch_pin);
}


#if defined(ARDUINO)
void setup() {
#endif  
#if defined(__MBED__)
int main() {
#endif
  #if ACTLOGLEVEL>LOG_NONE
    #if defined(ARDUINO)
      LogObject.begin(UARTBAUD);
    #endif
    #if defined(__MBED__)
      Serial LogObject(SERIAL_TX,SERIAL_RX);
      LogObject.baud(UARTBAUD);
    #endif
  #endif

// initialize the ethernet device
//Ethernet.begin(mac,myIP);
Ethernet.begin(mac,myIP,myDNS,myGW,myMASK);
// start listening for clients
server.begin();
//start onewire
ds18b20.begin();
#if defined(ARDUINO)
}

void loop() {
#endif  

#if defined(__MBED__)
while(true) {
#endif
  size_t size;
  const uint8_t gold[20] = {'A','R','T','E',':','E','X','T','E','R','N','A','L','_','S','E','N','S','O','R'};
  int counter=0;
  if (EthernetClient client = server.available())
    {
      if (client)
        {
          while((size = client.available()) > 0)
            {
              uint8_t* msg = (uint8_t*)malloc(size);
              size = client.read(msg,size);
              counter=0;
              while(counter<20){
                if(gold[counter] != msg[counter])   break;
                else                                counter++;
              }
              free(msg);
              if(counter==20){
                read_temperature(N_TEMPERATURE, temperature, ds18b20);
                read_voltage(voltage);
                for(int i=0; i<N_TEMPERATURE; i++){
                  client.print(temperature[i]);
                  client.print(",");
                }
                client.print(voltage[0]);
                client.print(",");
                client.println(voltage[1]);
              }

            }
        }
    }
}
#if defined(__MBED__)
}
#endif
