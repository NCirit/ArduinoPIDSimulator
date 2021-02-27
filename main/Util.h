#ifndef __UTIL__H
#define __UTIL__H

class Util{

public:
	static unsigned char calculateCRC(unsigned char* data, size_t size){
		unsigned char crc = 0, temp = 0, bit = 0;
		for (short i = 0; i < size; i++)
		{
			temp = data[i];
			for(unsigned char j = 0; j < 8; j++)
			{
				bit = (crc ^ temp) & 0x1;
				crc >>= 1;
				if(bit)
				{
					crc ^= 0x8C;
				}
				temp >>= 1;
			}
		}
		return crc;
	}
};

#endif
