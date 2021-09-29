#ifndef __COMTYPE_H__
#define __COMTYPE_H__

#if defined(SDCC) || defined(__SDCC)
#define _BOOL __bit
#define _TRUE 1
#define _FALSE 0
#define _XDATA __xdata
#define _IDATA __idata
#define _DATA __data
#define DEFSFR(addr, name) __sfr __at(addr) name;
#define DEFSBIT(addr, name) __sbit __at(addr) name;
#define _INTERRUPT(NO) __interrupt(NO)
#define _USING(REGBANK) __using(REGBANK)
#else


#define _BOOL bit
#define _TRUE 1
#define _FALSE 0
#define _XDATA xdata
#define _IDATA idata
#define _DATA data

#define DEFSFR(addr, name) sfr name = addr;
#define DEFSBIT(addr, name) sbit name = addr;
#define _INTERRUPT(NO) interrupt NO
#define _USING(REGBANK) using REGBANK

#endif

#endif