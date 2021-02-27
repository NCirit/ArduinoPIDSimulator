#ifndef __SIMULATOR__H
#define __SIMULATOR__H

typedef unsigned int size_t;

union union_uf
{
	unsigned char* u;
	float f;
};

enum MessageID{
	constants = 0x15,
	controlSignal = 0x20,
	pidSignals = 0x19,
	sensorData = 0x45,
	setPoint = 0x11,
	syncObject = 0x51
};

enum ErrorInfo{
	nok = 0,
	ok = 1
};

struct SyncObject
{
	unsigned char header;
	unsigned char crc;

	SyncObject()
	:header(MessageID::syncObject)
	{}
};

struct SetPoint
{
	unsigned char header;
	unsigned char setPoint[sizeof(float)];
	unsigned char crc;

	SetPoint()
	: header(MessageID::setPoint)
	{}

	void setValue(float& value);
	
	float getValue() {
		float* temp = reinterpret_cast<float *>(setPoint);
		return *temp;
	}
};

struct Sensor
{
	unsigned char header;
	unsigned char data[sizeof(float)];
	unsigned char crc;

	Sensor()
	:header(MessageID::sensorData)
	{

	}
	void setValue(float& _kp);
	float getValue() {
		float* temp = reinterpret_cast<float *>(data);
		return *temp;
	}
};


struct Constants
{
	unsigned char header; 
	unsigned char kp[sizeof(float)];
	unsigned char ki[sizeof(float)];
	unsigned char kd[sizeof(float)];
	unsigned char crc;
	Constants()
	: header(MessageID::constants)
	{

	}

	void setValues(float& _kp, float& _ki, float& _kd);
	void getValues(float& _kp, float& _ki, float& _kd)
	{
		float* temp = reinterpret_cast<float *>(kp);
		_kp = *temp;

		temp = reinterpret_cast<float *>(ki);
		_ki = *temp;

		temp = reinterpret_cast<float *>(kd);
		_kd = *temp;

	}
};

struct ControlSignal{
	unsigned char header;
	unsigned char controlSignal[sizeof(float)];
	unsigned char crc;

	ControlSignal()
	: header(MessageID::controlSignal)
	{	}
	void setValue(float signal);
};

struct PIDSignals{
	unsigned char header;
	unsigned char p[sizeof(float)];
	unsigned char i[sizeof(float)];
	unsigned char d[sizeof(float)];
	unsigned char crc;

	PIDSignals()
	: header(MessageID::pidSignals)
	{}

	void setValue(float& _p, float& _i, float& _d);
	void getValues(float& _p, float& _i, float& _d)
	{
		float* temp = reinterpret_cast<float *>(p);
		_p = *temp;

		temp = reinterpret_cast<float *>(i);
		_i = *temp;

		temp = reinterpret_cast<float *>(d);
		_d = *temp;

	}
};

class Simulator
{

public:
	Simulator();
	void sendConstans(float kp, float ki, float kd);
	void sendControlSignal(float control);
	void sendPIDInfo(float p, float i, float d);
	void sendSensorData(float f);
	void sendSetPoint(float setPoint);
	void sendResetSignal();

	void getConstants(float& kp, float& ki, float& kd);
	float getSetPoint();
	float getSensorData();
	void syncCommunication();
	void write(unsigned char* data, size_t size);
	ErrorInfo read(unsigned char* data, size_t size);
	ErrorInfo reSynchRead(unsigned char* data, size_t size);

};

#endif
