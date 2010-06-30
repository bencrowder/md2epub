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
