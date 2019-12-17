  # verification
  verification have three stage
   1.  set compiler environment
   2.  generate assembly file(.a51)
   3.  compile assembly file(.a51) to manchine code file.
   4.  run test case with manchine code file.
   ## set compiler environment
   in this project, I use keil A51.exe to compile assembly file. we using two environment variable: `PATH` and `C51INC`. `PATH` include the path of A51.exe, `C51INC` is the path of C51's include files.

   ## generate assembly file
   /test/temp/compile_all.py just complie the test.a51 and gnerate the `.obj` file with the same name as the assembly file.