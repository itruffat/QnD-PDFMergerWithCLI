# QuickAndDirty-PDFMergerCLI
An small CLI interface done in Python to quickly merge PDF files

TL;DR I had to merge a few PDF files in order while leaving some bookmarks intact, so instead of downloading a program I wanted to make something simple in pure Python. I seized the opportunity to try 'curses', something I have been wanting to do for a long time.

In the end, the code to merge the PDF files itself is really short (somewhere between 5 and 15 lines in total), but I ended up using most of my time to create an (incredibly wonky) CommandLine interface. 

There a few bugs here and there, for example the program will raise an exeception if a symlinks is selected. There are also more features that I wanted to add, such as being able to manually pick which bookmarks you want to keep (instead of being "All or nothing"). But the tools does exactly what I need it to do for now.

The program uses Python3, and it requires PyPDF2 and Curses.