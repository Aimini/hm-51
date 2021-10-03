# Example Code Documention  <!-- omit in toc -->
---
## Table of Cotents  <!-- omit in toc -->
- [Introduction](#introduction)
- [Folder Structure](#folder-structure)
## Introduction
 This folder provides some sample codes to show you how to write a program for this non-standard 8051 CPU.
 
 Although ISA is compatible, due to some distinction in hardware, we have some different declartion of SFR at header files.

  **from my practical experience, if there is example code that implement what you want,the best way is to get a copy and modify it.**

## Folder Structure
  - **common**
    - **IAP**
      - IAPboot.A51: provide IAP for hardware(it's not for simulator although you can try to run it in simulator)
    - **include:** the replacement of "reg51.h"
      - **comtype.h:** don't forget copy me!
      - **hm51.h:** yes, please include me!
    - **startup**
      - **CONF_TNY.A51:** configuration file for RTX-tiny51.
      - **STARTUP.A51:** just a start up file for bare hm51. 
  - **test_cmd:**  Test code running on bare hm51.
  - **test_RTX_tiny51:** Test code running based on RTX-tiny51.



