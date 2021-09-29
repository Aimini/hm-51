#ifndef __HM51_H__
#define __HM51_H__

/*-------------------------------------------------------------------------
    AI copy it from sdcc at 2020-10-13 10:41:41。
    Some modifications have been made to be compatible with hm-51.
    ##################  Statement in the original file ##################
   8052.h: Register Declarations for the Intel 8052 Processor

   Copyright (C) 2000, Bela Torok / bela.torok@kssg.ch

   This library is free software; you can redistribute it and/or modify it
   under the terms of the GNU General Public License as published by the
   Free Software Foundation; either version 2, or (at your option) any
   later version.

   This library is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License 
   along with this library; see the file COPYING. If not, write to the
   Free Software Foundation, 51 Franklin Street, Fifth Floor, Boston,
   MA 02110-1301, USA.

   As a special exception, if you link this library with other files,
   some of which are compiled with SDCC, to produce an executable,
   this library does not by itself cause the resulting executable to
   be covered by the GNU General Public License. This exception does
   not however invalidate any other reasons why the executable file
   might be covered by the GNU General Public License.
-------------------------------------------------------------------------*/
#include "comtype.h"

/*  BYTE Register  */
DEFSFR(0x80, P0)
DEFSFR(0x81, SP)
DEFSFR(0x82, DPL)
DEFSFR(0x83, DPH)
//DEFSFR(0x87, PCON)
DEFSFR(0x88, TCON)
DEFSFR(0x89, TMOD)
DEFSFR(0x8A, TL0)
DEFSFR(0x8B, TL1)
DEFSFR(0x8C, TH0)
DEFSFR(0x8D, TH1)
#ifdef HM51_HARDWARE
DEFSFR(0x90, P0DRV)
#else
DEFSFR(0x90, P1)
#endif
DEFSFR(0x98, SCON)
DEFSFR(0x99, SBUF)

#ifdef HM51_HARDWARE
//------- for hardware 
DEFSBIT(0x9A, TUARTL)
DEFSBIT(0x9B, TUARTH)
#endif
//-------  
//DEFSFR(0x9A, SITL)
//DEFSFR(0x9B, SITH)
DEFSFR(0xA8, IE)
DEFSFR(0xB8, IP)
DEFSFR(0xD0, PSW)
DEFSFR(0xE0, ACC)
DEFSFR(0xF0, B)

/*  BIT Register  */
/* P0 */
DEFSBIT(0x80, P0_0)
DEFSBIT(0x81, P0_1)
DEFSBIT(0x82, P0_2)
DEFSBIT(0x83, P0_3)
DEFSBIT(0x84, P0_4)
DEFSBIT(0x85, P0_5)
DEFSBIT(0x86, P0_6)
DEFSBIT(0x87, P0_7)

/*  TCON  */
DEFSBIT(0x88, IT0)
DEFSBIT(0x89, IE0)
DEFSBIT(0x8A, IT1)
DEFSBIT(0x8B, IE1)
DEFSBIT(0x8C, TR0)
DEFSBIT(0x8D, TF0)
DEFSBIT(0x8E, TR1)
DEFSBIT(0x8F, TF1)

#ifdef HM51_HARDWARE
/* P0 output strong current */
DEFSBIT(0x90, P0DV0)
DEFSBIT(0x91, P0DV1)
DEFSBIT(0x92, P0DV2)
DEFSBIT(0x93, P0DV3)
DEFSBIT(0x94, P0DV4)
DEFSBIT(0x95, P0DV5)
DEFSBIT(0x96, P0DV6)
DEFSBIT(0x97, P0DV7)
#else
/* P1 */
DEFSBIT(0x90, P1_0)
DEFSBIT(0x91, P1_1)
DEFSBIT(0x92, P1_2)
DEFSBIT(0x93, P1_3)
DEFSBIT(0x94, P1_4)
DEFSBIT(0x95, P1_5)
DEFSBIT(0x96, P1_6)
DEFSBIT(0x97, P1_7)
#endif

/*  SCON  */
DEFSBIT(0x98, RI)
DEFSBIT(0x99, TI)
DEFSBIT(0x9C, REN)
//DEFSBIT(0x9D, SM2)
//DEFSBIT(0x9E, SM1)
//DEFSBIT(0x9F, SM0)

/* P2 */
//DEFSBIT(0xA0, P2_0)
//DEFSBIT(0xA1, P2_1)
//DEFSBIT(0xA2, P2_2)
//DEFSBIT(0xA3, P2_3)
//DEFSBIT(0xA4, P2_4)
//DEFSBIT(0xA5, P2_5)
//DEFSBIT(0xA6, P2_6)
//DEFSBIT(0xA7, P2_7)

/*  IE   */
DEFSBIT(0xA8, EX0)
DEFSBIT(0xA9, ET0)
DEFSBIT(0xAA, EX1)
DEFSBIT(0xAB, ET1)
DEFSBIT(0xAC, ES)
DEFSBIT(0xAF, EA)

#define BIDX_EX0 0
#define BIDX_ET0 1
#define BIDX_EX1 2
#define BIDX_ET1 3
#define BIDX_ES  4
#define BIDX_EA  7

#define MASK_EX0  0x1
#define MASK_ET0  0x2
#define MASK_EX1  0x4
#define MASK_ET1  0x8
#define MASK_ES  0x10
#define MASK_EA  0x80


/*  IP   */
DEFSBIT(0xB8, PX0)
DEFSBIT(0xB9, PT0)
DEFSBIT(0xBA, PX1)
DEFSBIT(0xBB, PT1)
DEFSBIT(0xBC, PS)

/*  PSW   */
DEFSBIT(0xD0, P)
DEFSBIT(0xD1, PRF)
DEFSBIT(0xD2, OV)
DEFSBIT(0xD3, RS0)
DEFSBIT(0xD4, RS1)
DEFSBIT(0xD5, F0)
DEFSBIT(0xD6, AC)
DEFSBIT(0xD7, CY)

/* TCON bits */
#define BIDX_IT0 0  
#define BIDX_IE0 1  
#define BIDX_IT1 2  
#define BIDX_IE1 3  
#define BIDX_TR0 4  
#define BIDX_TF0 5  
#define BIDX_TR1 6  
#define BIDX_TF1 7  

/* TMOD bits */
#define BIDX_CnT0    2
#define BIDX_GATE0   3
#define BIDX_CnT1    6
#define BIDX_GATE1   7
//#define MASK_M0 0x01
//#define MASK_M1 0x02
#define MASK_CnT0   0x04
#define MASK_GATE0  0x08
//#define T1_M0 0x10
//#define T1_M1 0x20
#define MASK_CnT1   0x40
#define MASK_GATE1  0x80

#define T0_MASK 0x0F
#define T1_MASK 0xF0

/* Interrupt numbers: address = (number * 8) + 3 */
#define VECTOR_IE0 0 /* 0x03 external interrupt 0 */
#define VECTOR_TF0 1 /* 0x0b timer 0 */
#define VECTOR_IE1 2 /* 0x13 external interrupt 1 */
#define VECTOR_TF1 3 /* 0x1b timer 1 */
#define VECTOR_SI0 4 /* 0x23 serial port 0 */

#ifndef HM51_HARDWARE
// hm-51 specified , debug purpose only 
DEFSFR(0xFF, ASTR)
DEFSFR(0xFE, ASTP1R)
DEFSFR(0xFD, ASTP0R)
DEFSFR(0xFC, EXITR)
#define ASSERT_FAIL 4
#endif

// hm-51 infomation
#define F_CPU (1000000)


#define TIMMER_VAL(CNT) (0xFFFF - (CNT) + 1)
#define TL_VAL(CNT) (TIMMER_VAL(CNT) & 0xFF)
#define TH_VAL(CNT) (TIMMER_VAL(CNT)>> 8)
#define LOAD_TIMMER(TL, TH, CNT) TL = TL_VAL(CNT); TH = TH_VAL(CNT);


#define CLRMARK(var, mask)   var = var & (0xFF ^ (mask));
#define SETMASK(var ,mask)   var = var | mask;

#define CLRBIT(var, b) var = var & (0xFF ^ (1 << b));
#define SETBIT(var, b) var = var | (1 << b);

#define GETBIT(var, b) ((var >> b) & 1)
#endif