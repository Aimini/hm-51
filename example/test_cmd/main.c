#include "test_cmd.h"
#include "hm51.h"
#include <stdio.h>
void int_IE0() _INTERRUPT(VECTOR_IE0)
{
	++cmd_cnt_int_IE0;
	cmd_flag_int = 1;
}

void int_TF0() _INTERRUPT(VECTOR_TF0)
{
	++cmd_cnt_int_TF0;
	cmd_flag_int = 1;
}

void int_IE1() _INTERRUPT(VECTOR_IE1)
{
	++cmd_cnt_int_IE1;
	cmd_flag_int = 1;
}

void int_TF1() _INTERRUPT(VECTOR_TF1)
{
	++cmd_cnt_int_TF1;
	cmd_flag_int = 1;
}
 


void main()
{
    TI = 1;
    REN = 1;
	while (1)
	{
		cmd_get_line();
		cmd_execute();
	}
}