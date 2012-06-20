#define __SFR_OFFSET 0
#include <avr/io.h>

.global make_blue
make_blue:
	#CBI PORTC,3
	SBI PORTC,2
	ret
