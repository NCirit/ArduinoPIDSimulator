
#include "Simulator.h"
#include "Arduino.h"
#include "Util.h"

void Constants::setValues(float& _kp, float& _ki, float& _kd)
{
	memcpy(kp, &_kp, sizeof(float));
	memcpy(ki, &_ki, sizeof(float));
	memcpy(kd, &_kd, sizeof(float));
}
void ControlSignal::setValue(float signal)
{
	memcpy(controlSignal, &signal, sizeof(float));
}

void PIDSignals::setValue(float& _p, float& _i, float& _d)
{
	memcpy(p, &_p, sizeof(float));
	memcpy(i, &_i, sizeof(float));
	memcpy(d, &_d, sizeof(float));
}

void SetPoint::setValue(float& s)
{
	memcpy(setPoint, &s, sizeof(float));
}

void Sensor::setValue(float& s)
{
	memcpy(data, &s, sizeof(float));
}

Simulator::Simulator()
{
  Serial.begin(115200);  
}

void Simulator::sendConstans(float kp, float ki, float kd)
{
	Constants c;
	c.setValues(kp, ki, kd);
	unsigned char* data = reinterpret_cast<unsigned char*>(&c);
	c.crc = Util::calculateCRC(data, sizeof(Constants) - 1);
	this->write(data, sizeof(Constants));
}

void Simulator::sendControlSignal(float signal)
{
	ControlSignal s;
	s.setValue(signal);
	unsigned char* data = reinterpret_cast<unsigned char*>(&s);
	s.crc = Util::calculateCRC(data, sizeof(ControlSignal) - 1);
	this->write(data, sizeof(ControlSignal));
}

void Simulator::sendPIDInfo(float p, float i, float d)
{
	PIDSignals pid;
	pid.setValue(p, i, d);
	unsigned char* data = reinterpret_cast<unsigned char*>(&pid);
	pid.crc = Util::calculateCRC(data, sizeof(PIDSignals) - 1);
	this->write(data, sizeof(PIDSignals));
}

void Simulator::sendSetPoint(float f)
{
	SetPoint s;
	s.setValue(f);
	unsigned char* data = reinterpret_cast<unsigned char*>(&s);
	s.crc = Util::calculateCRC(data, sizeof(SetPoint) - 1);
	this->write(data, sizeof(SetPoint));
}

void Simulator::sendSensorData(float f)
{
	Sensor s;
	s.setValue(f);
	unsigned char* data = reinterpret_cast<unsigned char*>(&s);
	s.crc = Util::calculateCRC(data, sizeof(Sensor) - 1);
	this->write(data, sizeof(Sensor));
}

void Simulator::sendResetSignal()
{
	SyncObject s;
	unsigned char* data = reinterpret_cast<unsigned char*>(&s);
	s.crc = Util::calculateCRC(data, sizeof(SyncObject) - 1);
	this->write(data, sizeof(SyncObject));
}

void Simulator::getConstants(float& kp, float& ki, float& kd)
{
	Constants c;
	unsigned char* data = reinterpret_cast<unsigned char*>(&c);
	ErrorInfo e = this->read(data, sizeof(Constants));
	while(e == ErrorInfo::nok)
	{
		e = this->reSynchRead(data, sizeof(Constants));
	}
	c.getValues(kp, ki, kd);
}

float Simulator::getSetPoint()
{
	SetPoint s;
	unsigned char* data = reinterpret_cast<unsigned char*>(&s);
	ErrorInfo e = this->read(data, sizeof(SetPoint));
	while(e == ErrorInfo::nok)
	{
		e = this->reSynchRead(data, sizeof(SetPoint));
	}

	return s.getValue();
}
float Simulator::getSensorData()
{
	Sensor temp;
	unsigned char* data = reinterpret_cast<unsigned char*>(&temp);
	ErrorInfo e = this->read(data, sizeof(Sensor));
	while(e == ErrorInfo::nok)
	{
		e = this->reSynchRead(data, sizeof(Sensor));
	}
	return temp.getValue();
}

void Simulator::write(unsigned char* data, size_t size)
{
	for(size_t i = 0; i < size; i++)
		Serial.write(data[i]);
}

ErrorInfo Simulator::read(unsigned char* data, size_t size)
{
	ErrorInfo e;
	unsigned char* temp = new unsigned char[size];
	for(size_t i = 1; i < size; i++)
	{
		while(Serial.available() <= 0);
		temp[i] = Serial.read();
	}	
	if(temp[0] == data[0] && temp[size - 1] == Util::calculateCRC(temp, size - 1))
	{	
		e = ErrorInfo::ok;
		memcpy(data, temp, size);
	}
	else
	{
		e = ErrorInfo::nok;
	}
	
	delete[] temp;
	return e;
}

ErrorInfo Simulator::reSynchRead(unsigned char* data, size_t size)
{
	ErrorInfo e;
	unsigned char* temp = new unsigned char[size];
	while((temp[0] = Serial.read()) != data[0])
	{
		temp[0] = Serial.read();
	}
	for(size_t i = 1; i < size; i++)
	{
		while(Serial.available() <= 0);
		temp[i] = Serial.read();
	}	
	if(temp[0] == data[0] && temp[size - 1] == Util::calculateCRC(temp, size - 1))
	{	
		e = ErrorInfo::ok;
		memcpy(data, temp, size);
	}
	else
	{
		e = ErrorInfo::nok;
	}
	
	delete[] temp;
	return e;
}
