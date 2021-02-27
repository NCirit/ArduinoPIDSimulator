#include "Simulator.h"


float set_noktasi = 10, cikis;
float sensor; // ornegin sicaklik sensorunden gelen deger olsun
//oransal, turev, integreal
float kp = 10, kd = 40, ki = 1;

float P, I, D;

// onceki_hata, simdiki hata, dt
float onceki_hata, e,  zaman_degisimi;

// dt'nin hesaplanmasi icin
unsigned long son_sure, anlik_zaman;

Simulator sim;

void setup()
{
	Serial.begin(115200);
  //sensor = sim.getSensorData(sensor);
	//sim.sendConstans(kp, ki, kd);

	// required part
	sim.sendResetSignal();
	set_noktasi = sim.getSetPoint();
	sim.sendSetPoint(set_noktasi);
	sim.getConstants(kp, ki, kd);
	sim.sendConstans(kp, ki, kd);

}

void loop()
{

	// required part
	sensor = sim.getSensorData();
	sim.sendSensorData(sensor);

	anlik_zaman = millis();
	zaman_degisimi = anlik_zaman - son_sure;
	son_sure = anlik_zaman;
	e = set_noktasi - sensor;

	P = kp * e;
	// burada toplamanin etkisi eski yapilan hatalarin birikimini sistemde tutmak
	// ilerleyen zamanla hata azaldikca bu deger yavas yavas artmaya baslayacak
	I += ki * e * zaman_degisimi * 1e-3;
	// burada fark ne kadar fazla ise turevin etkisi sisteme yuksektir.
	D = kd * (e - onceki_hata) * 1e3 / zaman_degisimi; 
	onceki_hata = e;
	// arduino icin cikis degeri 0-255 arasinda olmalidir.
	cikis = P + I + D;
	if(cikis > 255)
		cikis = 255;
	else if(cikis < 0)
		cikis = 0;
  

	sim.sendControlSignal(cikis);
	sim.sendConstans(kp, ki, kd);
  sim.sendPIDInfo(P, I, D);

}
