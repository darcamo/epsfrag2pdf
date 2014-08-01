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

# Usage Instructions

For each eps file, create a file with the same name and the "psfrags"
extension. In this psfrag file, put the psfrag code you would normally put
in your latex document. Furthermore, if the first line in the psfrag file
starts with a bracket it will be considered as options to be passes to the
includegraphics command during conversion. See the `test.psfrags` file as
an example.

With the eps file and the corresponding psfrags file in the same folder,
run the `epsfrag2pdf.py` script and pass the name of the eps file without
extension. As an exemple, in the folder where you have all of the files
here you can convert the test.eps file eith the comand
```bash
./epsfrag2pdf.py test
```
You can also run the `eps2pdf_converter_gui.py` to use a simple gui, but it
is usually easier to convert running the `epsfrag2pdf.py` script in the
command line.
