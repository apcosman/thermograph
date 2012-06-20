CC=/usr/bin/avr-gcc
MEGA=328p
CFLAGS=-g -Os -Wall -mcall-prologues -mmcu=atmega$(MEGA) 
OBJ2HEX=/usr/bin/avr-objcopy 
PROG=/usr/bin/avrdude
TARGET=main
ASMFLAGS =-mmcu=atmega$(MEGA) -c -x assembler-with-cpp

program : $(TARGET).hex
	$(PROG) -c avrispv2 -p m$(MEGA) -P /dev/ttyACM0 -e
	$(PROG) -c avrispv2 -p m$(MEGA) -P /dev/ttyACM0 -U flash:w:$(TARGET).hex

# asm from hand coded asm 
asm_func.o : asm_func.S
	$(CC) $(ASMFLAGS) $^ -o $@

%.o : %.c 
	$(CC) -c $(CFLAGS) $^ -o $@	

main.obj : main.o asm_func.o 
	$(CC) $(CFLAGS) $^ -o $@ -lm

%.hex : %.obj
	$(OBJ2HEX) -R .eeprom -O ihex $< $@

clean :
	rm -f *.hex *.obj *.o *.s
