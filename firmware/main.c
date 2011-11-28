// F_CPU tells util/delay.h our clock frequency
#define F_CPU 20000000UL	// Baby Orangutan frequency (20MHz)

#define BAUD 9600
#define MYUBRR F_CPU/16/BAUD-1

#include <avr/io.h>
#include <util/delay.h>

void delayms( uint16_t millis ) {
	while ( millis ) {
		_delay_ms( 1 );
		millis--;
	}
}

char nthdigit(uint16_t x, unsigned int n)
{
    static uint16_t powersof10[] = {1, 10, 100, 1000, 10000};
    return ((x / powersof10[n]) % 10) + '0';
}

void USART_Init( unsigned int ubrr) {
	
	/*Set baud rate */ 
	UBRR0H = (unsigned char)(ubrr>>8); 
	UBRR0L = (unsigned char)ubrr; 

	/*Enable receiver and transmitter */ 
	//UCSR0B = (1<<RXEN0)|(1<<TXEN0); 
	
	//Enable just transmit
	UCSR0B =  (0 << RXEN0)  | (1 << TXEN0);

	/* Set frame format: 8data, 1stop bit */ 
	UCSR0C = (0<<USBS0)|(3<<UCSZ00);
}

void USART_Transmit( unsigned char data ) {

	/* Wait for empty transmit buffer */ 
	while ( !( UCSR0A & (1<<UDRE0)) );

	/* Put data into buffer, sends the data */ 
	UDR0 = data;
}

void display_int(uint16_t x, int pt)
{
	USART_Transmit(0x76);  //Reset Display

	USART_Transmit(0x77); //Turn on Decimal Point
	USART_Transmit(1<<pt); 

	USART_Transmit(nthdigit(x,3));
	USART_Transmit(nthdigit(x,2));
	USART_Transmit(nthdigit(x,1));
	USART_Transmit(nthdigit(x,0));

}

void ADC_Initialize(void) {
		
	ADCSRA   = (1 << ADEN) | (7 << ADPS0) ;  //Enable ADC, divide-by-128 for prescaler 
	
	ADMUX    = (0 << ADLAR) | (0 << REFS0) | (0 << REFS1) | ( 6 << MUX0);

}

uint16_t adc_read(void)
{
	uint16_t result = 0;
	uint8_t low;
	uint8_t high;

	ADCSRA  |= (1<<ADSC);					// Start ADC Conversion

	while((ADCSRA & (1<<ADIF)) != 0x10);	// Wait till conversion is complete

	low = ADCL;
	high = ADCH;

	result   = ADCL;                        // Read the ADC Result
	result = ADCL + (ADCH << 8);			

	ADCSRA  |= (1 << ADIF);					// Clear ADC Conversion Interrupt Flag

	return result;
}


int main( void ) {


	USART_Init(MYUBRR);
	ADC_Initialize();

	DDRC |= 1 << DDC2; // set PC2 to output
	DDRC |= 1 << DDC3; // set PC3 to output

	DDRD |= 1 << DDD1;

	uint16_t count = 0;
	uint16_t volts = 0;
	uint16_t resistance_10 = 0;
	//uint32_t temp;
	uint16_t temperature = 0;

	USART_Transmit(0x76);  //Reset Display

	while ( 1 ) {

		delayms( 450 );	

		//PORTC &= ( 1 << PORTC2 );	// LED off
		//PORTC &= ( 1 << PORTC1 );	// LED off		
		//c2
		//PORTC |= ~( 1 << PORTC2 );	// LED on
		//PORTD |= 1 << PORTD1; 		// LED on
		//delayms( 450 );
		//c1
		//PORTC |= ~( 1 << PORTC1 );	// LED on
		//PORTC &= ( 1 << PORTC2 );	// LED off
		//delayms( 450 );			
		//c2&c1
		//PORTC |= ~( 1 << PORTC2 );	// LED on
		//delayms( 450 );	

		//Display Temperature
		count = adc_read();
		volts = ((count*4.97)/1024)*100;	
		//display_int(volts, 1);
		//delayms(450);
		resistance_10 = ((volts*100)/(506-volts)); //(5-count);
		//display_int(resistance_10, 6);
		//delayms(450);
		temperature = 25 - ( (resistance_10-1000)/10 )/4.25;
		display_int(temperature*10, 2);



	}	


	return 0;
}
