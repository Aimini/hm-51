#if !defined(__TEST_CMD__)
#define __TEST_CMD__

#include <stdio.h>



extern volatile bit cmd_flag_int;

extern volatile unsigned char cmd_cnt_int_IE0;
extern volatile unsigned char cmd_cnt_int_TF0;
extern volatile unsigned char cmd_cnt_int_IE1;
extern volatile unsigned char cmd_cnt_int_TF1;

#define CMD_BUF_MAX_SIZE 32
#define CMD_TOKEN_SPILT " \n\r\t"
void cmd_get_line();
void cmd_execute();


#endif // __TEST_CMD__

