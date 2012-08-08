;**** A P P L I C A T I O N   N O T E   A V R 3 0 5 ************************
;*
;* Title		: Half Duplex Interrupt Driven Software UART
;* Version		: rev. 1.2 (24-04-2002), reset vector added
;*			: rev. 1.1 (27.08.1997)
;* Last updated		: 24-04-2002
;* Target		: AT90Sxxxx (All AVR Device)
;*
;* Support email	: avr@atmel.com
;*
;* Code Size		: 32 Words
;* Low Register Usage	: 0
;* High Register Usage	: 4
;* Interrupt Usage	: None
;*
;* DESCRIPTION
;* This Application note contains a very code efficient software UART.
;* The example program receives one character and echoes it back.
;***************************************************************************

;.include "1200def.inc"
#define __SFR_OFFSET 0
#include <avr/io.h>
.global asm_tx

;***** Pin definitions

.equ	RxC,4	 		;Receive (mega328p's) pin is PD7
.equ	TxC,1			;Transmit (mega328p's) pin is PD4

;***** Global register variables

#define	bitcnt R21			;bit counter
#define	temp R23			;temporary storage register

#define	Txbyte	R18			;Data to be transmitted
#define	Rxbyte	R19			;Received data

;.cseg
#.org 0
#	rjmp	reset
;*************************************************************************
;*
;* "putchar"
;*
;* This subroutine transmits the byte stored in the "Txbyte" register
;* The number of stop bits used is set with the sb constant
;*
;* Number of words	:14 including return
;* Number of cycles	:Depens on bit rate
;* Low registers used	:None
;* High registers used	:2 (bitcnt,Txbyte)
;* Pointers used	:None
;*
;***************************************************************************
.equ		sb,1		
;***************Number of stop bits (1, 2, ...)

putchar:	
		ldi R21 , 9+sb 
;***********************1+8+sb (sb is # of stop bits) [R16 is bitcnt]

		com	Txbyte		;Inverte everything
		sec			;Start bit

putchar0:	brcc	putchar1	;If carry set
		cbi	PORTC,TxC	;    send a '0'
		rjmp	putchar2	;else	

putchar1:	sbi	PORTC,TxC	;    send a '1'
		nop

putchar2:	rcall UART_delay	;One bit delay
		rcall UART_delay

		lsr	Txbyte		;Get next bit
		dec	bitcnt		;If not all bit sent
		brne	putchar0	;   send next
					;else
		ret			;   return


;***************************************************************************
;*
;* "getchar"
;*
;* This subroutine receives one byte and returns it in the "Rxbyte" register
;*
;* Number of words	:14 including return
;* Number of cycles	:Depens on when data arrives
;* Low registers used	:None
;* High registers used	:2 (bitcnt,Rxbyte)
;* Pointers used	:None
;*
;***************************************************************************

getchar:	ldi 	R21,9	;8 data bit + 1 stop bit

getchar1:	sbic 	PINC,RxC	;Wait for start bit
		rjmp 	getchar1

		rcall UART_delay	;0.5 bit delay

getchar2:	rcall UART_delay	;1 bit delay
		rcall UART_delay		

		clc			;clear carry
		sbic 	PINC,RxC	;if RX pin high
		sec			;

		dec 	bitcnt		;If bit is stop bit
		breq 	getchar3	;   return
					;else
		ror 	Rxbyte		;   shift bit into Rxbyte
		rjmp 	getchar2	;   go get next

getchar3:	ret


;***************************************************************************
;*
;* "UART_delay"
;*
;* This delay subroutine generates the required delay between the bits when
;* transmitting and receiving bytes. The total execution time is set by the
;* constant "b":
;*
;*	3·b + 7 cycles (including rcall and ret)
;*
;* Number of words	:4 including return
;* Low registers used	:None
;* High registers used	:1 (temp)
;* Pointers used	:None
;*
;***************************************************************************


;.equ	b, 42	;57600 (for 16mhz)
.equ   b, 54   ;57600 (for 20mhz)

UART_delay:	ldi	R23 ,b
UART_delay1:	dec	temp
		brne	UART_delay1
		ret

asm_tx:		mov     R18, R24 
		;ldi    R18, 87
		rcall	putchar
		;ldi    R18, 32
		;rcall	putchar
		ret
