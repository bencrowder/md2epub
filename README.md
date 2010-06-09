## md2epub

md2epub is a Python script for making ePubs out of Markdown files.

The ePub-generation code is based off Matt Turner's [GetBook.py](http://staff.washington.edu/mdturner).

### Dependencies

* [python-markdown2](http://code.google.com/p/python-markdown2/)

### Usage

0. Install python-markdown2 if you haven't already done so.
1. Create a book file. See sample.book for an example. (It's pretty simple.)
2. Run <code>md2epub.py [myfile.book]</code>.

### Notes

* The book file can be called anything and doesn't have to end in ".book".
* <code>sample.book</code> has the Markdown files and images in separate subdirectories, but that's optional.
* There are several Dublin Core features I haven't included. Someday...
* Hierarchical navmaps aren't supported yet.
