// F_CPU tells util/delay.h our clock frequency
#define F_CPU 20000000UL	// Baby Orangutan frequency (20MHz)

#define BAUD 9600
#define MYUBRR F_CPU/16/BAUD-1

#include <avr/io.h>
#include <math.h>
#include <util/delay.h>

void delayms( uint16_t millis ) {
	while ( millis ) {
		_delay_ms( 1 );
		millis--;
	}
}

//TODO: replace sprintf ( char * str, const char * format, ... )
char nthdigit(uint32_t x, unsigned int n)
{
    static uint16_t powersof10[] = {1, 10, 100, 1000};
    return ((x / powersof10[n]) % 10) + '0';
}

char nthdecimal(double x, unsigned int n)
{
    static uint16_t powersof10[] = {10, 100, 1000, 10000};
    return ( (int)(x * powersof10[n]) % 10) + '0';
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

void display_int(uint32_t x, int pt)
{
	USART_Transmit(0x76);  //Reset Display

	//if (x < 1) {
	//	USART_Transmit('e');
	//	USART_Transmit('e');
	//	USART_Transmit('e');
	//	USART_Transmit('e');	
	//}
	//else
	//{
		USART_Transmit(0x77); //Turn on Decimal Point
		USART_Transmit(1<<pt); 

		USART_Transmit(nthdigit(x,3));
		USART_Transmit(nthdigit(x,2));
		USART_Transmit(nthdigit(x,1));
		USART_Transmit(nthdigit(x,0));
	//}

}

void display_float(double x)
{
	USART_Transmit(0x76);  //Reset Display

		USART_Transmit(0x77); //Turn on Decimal Point
		USART_Transmit(1<<2); 

		USART_Transmit(nthdigit(x,2));
		USART_Transmit(nthdigit(x,1));
		USART_Transmit(nthdigit(x,0));
		USART_Transmit(nthdecimal(x,0));

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

	DDRB |= (1 << DDB1) | (0 << DDB2);		// set PB1 to output, PB2 to input
	PORTB |=  1 << PORTB1 | 1 << PB2 ;		// write logic high (turn on), write logic high (pull-up)	

	USART_Init(MYUBRR);
	ADC_Initialize();

	DDRC &= ~(1 << DDC0); 

	//DDRC |=  (0 << DDC5); // set PC0 to input, PC5 to output

	uint16_t count = 0;
	double volts = 0;
	double resistance = 0;
	double temperature = 0;

	USART_Transmit(0x76);  //Reset Display


	while ( 1 ) {
		delayms( 450 );	

		if (bit_is_set(PINC,PINC0)) {
			//PORTC |= ( 1 << PC5 );
			display_int(5, 0);
		}
		else {
			//PORTC &= ~( 0 << PC5 );
			display_int(70, 3);
		}
	
		//if (bit_is_clear(PINB,PINB2) && (temperature-273) < 70) {
		//	PORTC |= ( 1 << PC5 ); //Relay On
		//}	
		//if (bit_is_set(PINB,PINB2) || (temperature-273) > 71) {
		//	PORTC &= ~ ( 1 << PORTC5 );	
		//}
	
	
		//Display Temperature
		//count = adc_read();
		//volts = ((count*4.97)/1024);	
		//resistance = ((volts*1000)/(5-volts)); 
		//temperature = 1 / (0.003354016 + 0.000256985*log(resistance/10000) + 0.000002620131*log(resistance/10000)*log(resistance/10000) );
		//temperature = temperature - 273;
		//display_float( temperature  );

	}


	return 0;
}
