#include "hm51.h"
#include <intrins.h>
#include <rtx51tny.h>

#define CHECKED_NORMAL 0
#define CHECKED_INCONSISTENT_RX_VALUE 1
#define CHECKED_RX_TIMED_OUT 2

#define TID_LED_INFO                 1
#define TID_VERIFY_UART_RX_TIMED_OUT 2
#define TID_VERIFY_UART              3
volatile char check_state = CHECKED_NORMAL;
volatile char p0value = 1;


void start_tasks() _task_ 0
{
#ifdef HM51_HARDWARE
    P0DRV = 0xFF;
#endif
    os_create_task(TID_LED_INFO);                 /* start task 1                         */
    os_create_task(TID_VERIFY_UART_RX_TIMED_OUT);                 /* start task 2                         */
    os_create_task(TID_VERIFY_UART);                 /* start task 2                         */
    P0 = 2;
    os_delete_task(0);
}



void flow_lights() _task_ TID_LED_INFO
{
    while(1)
    {
        if(check_state != CHECKED_NORMAL)
        {
            p0value = check_state;
#ifndef HM51_HARDWARE
            ASTR=ASSERT_FAIL;
#endif       
        }
            
        else
            p0value = _cror_(p0value, 1);  
        P0 = p0value;
        os_wait2(K_IVL | K_SIG, 10);
    }
}

void verifyUART_rx_timed_out() _task_ TID_VERIFY_UART_RX_TIMED_OUT
{       
    char ms_10times = 0;
    while(1){
        
    switch(os_wait2(K_IVL | K_SIG, 1))
    {
        case TMO_EVENT:
            ++ms_10times;
            break;
        case SIG_EVENT:
            ms_10times = 0;
            os_reset_interval(1);
            break;
    }
    if(ms_10times == 100) // not data from SBUF for 1s
    {
        
        check_state = CHECKED_RX_TIMED_OUT;
        os_send_signal(TID_LED_INFO);        

        os_delete_task(TID_VERIFY_UART);
        os_delete_task(TID_VERIFY_UART_RX_TIMED_OUT);
    }
}
    
}

void verifyUART() _task_ TID_VERIFY_UART
{
    int i = 0;
    // setup RX-TX
    char ssent = 0;
    char srecverify = 0;
#ifdef HM51_HARDWARE
    LOAD_TIMMER(TUARTL,TUARTH, 2);     
#endif
    REN = 1;
    TI = 1;

    // loop;
    while(1)
    {
        while(!TI);
        {
            SBUF = ssent; 
            ++ssent;
        }
        
        while(!RI);
        {
            os_send_signal(TID_VERIFY_UART_RX_TIMED_OUT);
            if(SBUF != srecverify)
            {
                check_state = CHECKED_INCONSISTENT_RX_VALUE;    
                os_send_signal(TID_LED_INFO);  
                
                os_delete_task(TID_VERIFY_UART_RX_TIMED_OUT);
                os_delete_task(TID_VERIFY_UART);
            }
            RI = 0;
            ++srecverify;
        }
        
    }
}

