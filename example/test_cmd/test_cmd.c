#include "test_cmd.h"
#include "hm51.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

volatile bit cmd_flag_int = 0;

volatile unsigned char cmd_cnt_int_IE0 = 0;
volatile unsigned char cmd_cnt_int_TF0 = 0;
volatile unsigned char cmd_cnt_int_IE1 = 0;
volatile unsigned char cmd_cnt_int_TF1 = 0;
void cmd_rw_sfr(_BOOL is_write);
void cmd_monitor_interrupt();

char cmd_buf[CMD_BUF_MAX_SIZE];
char cmd_buf_size = 0;

const char * int_trigger_methods[2] = {"low level",  "falling edge"};
const char * timer_functions[2] = {"timer",  "counter"};

/*
const char *const dbg_char = 
    "set IE 0x8F\n"
    "set TMOD 0xDD\n"
    "set TCON 0x11\n"
    "monitor\nq"
    "monitor\n";
char dbg_i = 0;

char getchar()
{
    if (dbg_char[dbg_i] != 0)
        return dbg_char[dbg_i++];
    
    while (1)
        ;
}    */  

void cmd_get_line()
{
    char *ptr = cmd_buf;
    char dummy = 0;
    cmd_buf_size = 0;
    printf("\n>>");
    while (1)
    {         
        dummy = _getkey();
        if (dummy == '\b')
        {
            if (ptr > cmd_buf)
            {
                --ptr;
                --cmd_buf_size;
                putchar('\b');
                putchar(' '); 
                putchar('\b');
            }        
        }
        else if (dummy == '\n' || dummy == '\r')
        {               
            *ptr = 0;
            putchar('\n');
            return;
        }
        else if (cmd_buf_size < CMD_BUF_MAX_SIZE - 1)
        {      
            *ptr = dummy;
            ++ptr;
            ++cmd_buf_size; 
            putchar(dummy);
        }
        else
        {    
        }
    }
}

void cmd_execute()
{
    char *psfrname = strtok(cmd_buf, CMD_TOKEN_SPILT);
    if (strcmp(psfrname, "set") == 0)
    {
        cmd_rw_sfr(_TRUE);
        return;
    }

    if (strcmp(psfrname, "read") == 0)
    {
        cmd_rw_sfr(_FALSE);
        return;
    }

    if (strcmp(psfrname, "monitor") == 0)
    {
        cmd_monitor_interrupt();
        return;
    }

    printf("[error] unknow command \"%s\"", psfrname);
}

void cmd_rw_sfr(_BOOL is_set)
{
    char *psfrname = strtok(NULL, CMD_TOKEN_SPILT);
    char *pstrvalue;
    char *convert_end;
    unsigned int value;

    if (is_set)
    {
        pstrvalue = strtok(NULL, CMD_TOKEN_SPILT);
        value = strtoul(pstrvalue, &convert_end, 0);
        if (convert_end == pstrvalue)
        {
            printf("[error] invalid numeric argument \"%s\".", pstrvalue);
            return;
        }
    }

#ifndef __TRY_RW_SFR
#define __TRY_RW_SFR(_SFR)                               \
    if (strcmp(psfrname, #_SFR) == 0)                    \
    {                                                    \
        if (is_set)                                      \
        {                                                \
            _SFR = value;                                \
            printf("set %s to %#04X.", psfrname, value); \
        }                                                \
        else                                             \
        {                                                \
            value = _SFR;                                \
            printf("%s = %#04X.", psfrname, value);      \
        }                                                \
        return;                                          \
    }
#endif
    __TRY_RW_SFR(TCON)
    __TRY_RW_SFR(TMOD)
    __TRY_RW_SFR(P0)
    __TRY_RW_SFR(IE)
    __TRY_RW_SFR(IP)
    __TRY_RW_SFR(TL0)
    __TRY_RW_SFR(TH0)
    __TRY_RW_SFR(TL1)
    __TRY_RW_SFR(TH1)
#ifdef HM51_HARDWARE
    __TRY_RW_SFR(P0DRV)
#else
    __TRY_RW_SFR(P1)
#endif
    printf("[error] \"%s\" is not a valid SFR.", psfrname);
}

void cmd_monitor_interrupt()
{
    unsigned int valSFR = IE;
    char i = 0;
    printf(
        "<press any key to quit>\n"
        "IE %#04X\n"
        "EA:%u\n",
        valSFR,
        GETBIT(valSFR, BIDX_EA));
     printf(
        "EX0:%u, ET0:%u, EX1:%u, ET1:%u, ES:%u  \n",
        GETBIT(valSFR, BIDX_EX0),
        GETBIT(valSFR, BIDX_ET0),
        GETBIT(valSFR, BIDX_EX1),
        GETBIT(valSFR, BIDX_ET1),
        GETBIT(valSFR, BIDX_ES));

    valSFR = TCON;
        printf(
        "IT0:%u(%s), IT1:%u(%s)\n",
        GETBIT(valSFR, BIDX_IT0),
        int_trigger_methods[GETBIT(valSFR, BIDX_IT0)],
        GETBIT(valSFR, BIDX_IT1),
        int_trigger_methods[GETBIT(valSFR, BIDX_IT1)]);
        
       valSFR = TMOD;     
        printf(
        "TR0:%u\tGATE0:%u\tC/~T0:%u(%s)\n",
        GETBIT(valSFR, BIDX_TR0),
        GETBIT(valSFR, BIDX_GATE0),
        GETBIT(valSFR, BIDX_CnT0),
        timer_functions[GETBIT(valSFR, BIDX_CnT0)]);
        
        printf(                                                                     
        "TR1:%u\tGATE1:%u\tC/~T1:%u(%s)\n",
        GETBIT(valSFR, BIDX_TR1),
        GETBIT(valSFR, BIDX_GATE1),
        GETBIT(valSFR, BIDX_CnT1),
        timer_functions[GETBIT(valSFR, BIDX_CnT1)]);
    cmd_cnt_int_IE0 = 0;
    cmd_cnt_int_TF0 = 0;
    cmd_cnt_int_IE1 = 0;
    cmd_cnt_int_TF1 = 0;
    
    i= 0;
    while(!RI)
    {
        if(cmd_flag_int)
        {
            while(i-- > 0)
            {
                putchar('\b');
            }
            i = printf("IE0:%#04x TF0:%#04x IE1:%#04x TF1:%#04x",
                (unsigned int)cmd_cnt_int_IE0,
                (unsigned int)cmd_cnt_int_TF0,
                (unsigned int)cmd_cnt_int_IE1,
                (unsigned int)cmd_cnt_int_TF1);
            cmd_flag_int = 0;
        }
    }
    getchar();
    
}