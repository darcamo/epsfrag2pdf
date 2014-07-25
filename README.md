epsfrag2pdf
===========

Convert EPS files to PDF files while performing psfrag replacements.

When working with Latex it is usually easier to use pdflatex to
generate PDF files than going the long route of
latex->dvips->ps2pdf.

However, one very useful package, the psfrag package, uses
postscript commands and thus requires compiling the document with
the long route. One way to circumvent this limitation is to
compile a latex document with just the desired figure to create a
PDF file of the figure with the replacements already done by
psfrag. After that one can use pdflatex and use the PDF version
of the figure instead of the original EPS file.

This project was created simple to make this conversion easier.
