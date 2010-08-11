## md2epub

md2epub is a Python script for making ePubs out of Markdown files.

The ePub-generation code is based on Matt Turner's [GetBook.py](http://staff.washington.edu/mdturner/personal.htm).

### Dependencies

* [python-markdown2](http://code.google.com/p/python-markdown2/)

### Usage

0. Install <code>python-markdown2</code> if you haven't already done so.
1. Create a book file. See <code>sample.book</code> for an example. (It's pretty simple.)
2. Run <code>md2epub.py myfile.book</code> and voila, instant ePub.

### Notes

* The book file can be called anything and doesn't have to end in ".book".
* <code>sample.book</code> has the Markdown files and images in separate subdirectories, but that's optional.
* <code>sample2.book</code> shows how to do a hierarchical table of contents
* There are several Dublin Core features I haven't included. Someday...

### Copyright and License

This only applies to the function that creates curly quotes, which I borrowed from Chad Miller's [smartypants.py](http://web.chad.org/projects/smartypants.py/).

#### SmartyPants

Copyright (c) 2003 John Gruber  
(http://daringfireball.net/)  
All rights reserved.  

See below ("Redistribution...")

#### smartypants.py

smartypants.py is a derivative work of SmartyPants.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

*   Redistributions of source code must retain the above copyright
		notice, this list of conditions and the following disclaimer.

*   Redistributions in binary form must reproduce the above copyright
		notice, this list of conditions and the following disclaimer in
		the documentation and/or other materials provided with the
		distribution.

*   Neither the name "SmartyPants" nor the names of its contributors
		may be used to endorse or promote products derived from this
		software without specific prior written permission.

This software is provided by the copyright holders and contributors "as
is" and any express or implied warranties, including, but not limited
to, the implied warranties of merchantability and fitness for a
particular purpose are disclaimed. In no event shall the copyright
owner or contributors be liable for any direct, indirect, incidental,
special, exemplary, or consequential damages (including, but not
limited to, procurement of substitute goods or services; loss of use,
data, or profits; or business interruption) however caused and on any
theory of liability, whether in contract, strict liability, or tort
(including negligence or otherwise) arising in any way out of the use
of this software, even if advised of the possibility of such damage.
