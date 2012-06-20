// F_CPU tells util/delay.h our clock frequency
#define F_CPU 20000000UL	// Baby Orangutan frequency (20MHz)

#define BAUD 9600
#define MYUBRR F_CPU/16/BAUD-1

#include <avr/io.h>
#include <math.h>
#include <util/delay.h>

extern void make_blue();  //make it blue

void delayms( uint16_t millis ) {
	while ( millis ) {
		_delay_ms( 1 );
		millis--;
	}
}

int main( void ) {

	DDRB  =  (1 << DDB1)   | (0 << DDB2);		// set PB1 to output, PB2 to input
	PORTB =  (0 << PORTB1) | (1 << PB2);		// write logic high (turn on), write logic high (pull-up)	

	DDRC =  (1 << DDC2) | (1 << DDC3); 

	while ( 1 ) {	
		PORTC = 0x00;
		PORTC |= (1 << PC3);
		delayms( 450 );	
		//PORTC |= (1 << PC2);
		make_blue();
		delayms( 450 );	
		
	}
	return 0;
}