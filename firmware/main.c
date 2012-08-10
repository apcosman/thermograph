// F_CPU tells util/delay.h our clock frequency
#define F_CPU 20000000UL	// Baby Orangutan frequency (20MHz)

#define BAUD 9600
#define MYUBRR F_CPU/16/BAUD-1

#include <avr/io.h>
#include <math.h>
#include <util/delay.h>

extern asm_tx(unsigned char tx);
//extern second_USART_RX();

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

void PWM_Init(void) {

	//Make PWM Pins, Digital Outputs
	DDRD = (1 << DDD5) | (1 << DDD6) | (1 << DDD3);
	DDRB |= (1 << DDB3);

	//Set PWM Pins High
	PORTD = ( 1 << PORTD5 ) | ( 1 << PORTD6 ) | ( 1 << PORTD3 );
	PORTB |= ( 1 << PORTB3);

	//Setup PWM Registers
	//OC0A & B
	TCCR0A = ( 3 << COM0A0 ) | ( 3 << COM0B0 ) | ( 1 << WGM00); //Set OC0A & OC0B PWM to inverted output, tie to OCR0A(/B?)
	TCCR0B = ( 0 << WGM02 ) | ( 2 << CS00 ); //Set OC0A/B Pre-Scalar (WGM02 -> TOP?)

	OCR0A = 255;
	OCR0B = 255;

	//Setup PWM Registers
	//OC2A & B
	TCCR2A = ( 3 << COM2A0 ) | ( 3 << COM2B0 ) | ( 1 << WGM20); //Set OC2A & OC2B PWM to inverted output, tie to OCR2A(/B?)
	TCCR2B = ( 0 << WGM22 ) | ( 2 << CS20 ); //Set OC2A/B Pre-Scalar (WGM22 -> TOP?)

	//OC2A & B
	OCR2A = 255;
	OCR2B = 255;
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
	
	ADMUX    = (0 << ADLAR) | (0 << REFS0) | (0 << REFS1);
}

void ADC_set_pin(mux) {
	ADMUX = (0 << ADLAR) | (0 << REFS0) | (0 << REFS1) | ( mux << MUX0);
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

	DDRB  =  (1 << DDB1)   | (0 << DDB2);		// set PB1 to output, PB2 to input
	PORTB =  (0 << PORTB1) | (1  << PB2);		// write logic  (turn on), write logic high (pull-up)	

	USART_Init(MYUBRR);
	ADC_Initialize();
	PWM_Init();

	DDRC = (0 << DDC0) | (1 << DDC1) | (1 << DDC5) | (1 << DDC2) | (1 << DDC3); 
	PORTC = 0x00;
	PORTC = ( 1 << PC5 );  //Relay off

	DDRD &= ~( 1 << DDD4 );
	PORTD |= ( 1 << PD4 ) ;//internal pull-up

	uint16_t count = 0;
	double volts = 0;
	double resistance = 0;
	double temperature = 0;

	USART_Transmit(0x76);  //Reset Display

	while ( 1 ) {

		if (bit_is_set(PINC,PINC0)) {
			PORTC |= (1 << DDC3);
			OCR2B = 255;
			OCR0B = 0;	
			
			OCR2A = 0;
			OCR0A = 255;
		      
			//PORTC |= ( 1 << PC5 );
			//display_int(5, 0);
		}
		else {
			PORTC &= ~(1 << DDC3);
			OCR2B = 255;
			OCR0B = 255; //0;

			OCR2A = 255; //0;
			OCR0A = 255;
		       		
			//PORTC &= ~( 0 << PC5 );
			//display_int(70, 3);
		}

		if bit_is_clear(PIND, PIND4) {
			ADC_set_pin(7);
			PORTC |= (1 << DDC2);
		}
		else
		{
			ADC_set_pin(6);
			PORTC &= ~(1 << DDC2);
		}
	
		if (bit_is_clear(PINB,PINB2)) { //&& (temperature-273) < 70) {
			PORTC &= ~( 1 << PC5 ); //Relay On
			asm_tx('R');
			asm_tx('\t');
		}	
		if (bit_is_set(PINB,PINB2)) { // || (temperature-273) > 71) {
			PORTC |= ( 1 << PORTC5 );
			asm_tx('r');
			asm_tx('\t');
		}
		
		//Display Temperature
		count = adc_read();
		volts = ((count*5.02)/1024);	
		resistance = ( (5.02 - volts) / volts ) * 100000;
		temperature = 1 / (0.003354016 + 0.000256985*log(resistance/10000) + 0.000002620131*log(resistance/10000)*log(resistance/10000) );
		display_int( volts*1000, 0  );
		delayms(500);
		display_float( temperature - 273 );
		delayms(500);

		asm_tx(nthdigit(temperature - 273 ,2));
		asm_tx(nthdigit(temperature - 273 ,1));
		asm_tx(nthdigit(temperature - 273 ,0));
		asm_tx(nthdecimal(temperature - 273 ,0));
		asm_tx('\n');
		asm_tx('\r');	


	}


	return 0;
}
