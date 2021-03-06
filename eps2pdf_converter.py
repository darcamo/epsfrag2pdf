#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""The main function in this module is the psfrag_replace function, which
is where the actual job is done.

 * Executing the module

When this module is executed as a script, it will receive an argument,
which is the NAME of the eps file without the extension. A file with the
same name, but with extensions 'psfrags' is expected. This file should have
all the psfrag text that you would normally use in latex. For instance
    \psfrag{Something}[cc][cc]{replacement}
    \psfrag{Original text}{Replaced text}

 * Passing Options to the includegraphics command

The first line in the NAME.psfrags file may contain options (inside brackets)
to be passed to the includegraphics command. For instance,
    [width=\textwidth]

 * Including Extra packages

If you need to use commands in the psfrag replacements that require extra
latex packages, then create a file called 'extra_latex_packages.tex' or
'NAME_extra_packages.tex' (the later will take precedence on the former if
both exist) and put the '\usepackage{some package}' lines there.
"""

import os
from subprocess import call


def get_extra_packages(name):
    """Try to get the extra latex packages from the file
    'extra_latex_packages.tex' or the file 'NAME_extra_packages.tex'.

    Return a string containing all the usepackage commands in one of these
    files. If none of the files exist, return an empty string.

    Parameters
    ----------
    name : str
        Name of the eps file without the ".eps" extension.
    """
    extra_packages = ""

    # If the file extra_latex_packages.tex exists, then extra_packages will
    # get its content
    try:
        fId = open('extra_latex_packages.tex')
        extra_packages = fId.read()
        fId.close()
    except IOError:
        # File extra_latex_packages.tex does not exist
        pass

    # If the file NAME_latex_packages.tex exists, then extra_packages will
    # get its content (overwriting previous content)
    try:
        filename = '{0}_extra_packages.tex'.format(name)
        fId = open(filename)
        extra_packages = fId.read()
        fId.close()
    except IOError:
        # File NAME_extra_packages.tex does not exist
        pass

    return extra_packages


def prepareLatexCode(figureName, psfrags, includegraphics_options=""):
    """
    Prepare the latex code used in the eps2pdf conversion.

    This method is charged of creating the template Latex code that will be
    used to include and process the eps file.

    Parameters
    ----------
    figureName : str
        Name of the eps file (without extension)
    psfrags : string or a list of strings
        It can be either a string with the psfrag commands or a list. If it
        is a list, each element in the list must be a list with 3
        elements. The first element is the original text, the second
        element is the replacement text and the third element has the
        parameters to be passed to psfrag command (Ex: "[cc][cc]" - without
        the quotes).
        Ex:
        [['BER', 'BER', '[cc][cc]']
         ['Title', '\\"Interference Alignment\\" for the SVD case', '']
         ['Eb/N0', '$Eb/N_0$', '']]
    includegraphics_options : str
        Options that should be passed to the includegraphics package
        (INCLUDING THE BRACKETS).
        Ex:
        [width=\textwidth]
    """
    if(isinstance(psfrags, list)):
        psfrag_replacements = psfragListToString(psfrags)
    else:
        psfrag_replacements = psfrags

    latex_code = """
\\documentclass{{article}}
\\usepackage{{graphicx,psfrag,color}}
\\usepackage[english]{{babel}}
\\usepackage[utf8]{{inputenc}}
{EXTRAPACKAGES}
\\setlength{{\\topmargin}}{{0in}}
\\setlength{{\\headheight}}{{0pt}}
\\setlength{{\\headsep}}{{0pt}}
\\setlength{{\\topskip}}{{0pt}}
\\setlength{{\\textheight}}{{\\paperheight}}
\\setlength{{\\oddsidemargin}}{{0in}}
\\setlength{{\\evensidemargin}}{{0in}}
\\setlength{{\\textwidth}}{{\\paperwidth}}
\\setlength{{\\parindent}}{{0pt}}
\\usepackage{{tikz}}
%%\\special{{! TeXDict begin /landplus90{{true}}store end }}
%%\\special{{! statusdict /setpage undef }}
%%\\special{{! statusdict /setpageparams undef }}
\\pagestyle{{empty}}
%%\\newsavebox{{\\pict}}

\\begin{{document}}
%%\\begin{{lrbox}}{{\\pict}}
{PSFRAG}
\\includegraphics{INCLUDEGRAPHICS_OPTIONS}{{{FILENAME}}}
%%\\end{{lrbox}}
%%\\special{{papersize=\\the\\wd\\pict,\\the\\ht\\pict}}
%%\\usebox{{\\pict}}
\\end{{document}}"""
    if includegraphics_options == "":
        includegraphics_options = "[scale=1]"

    all_replacements = {"PSFRAG": psfrag_replacements,
                        "FILENAME": figureName,
                        "INCLUDEGRAPHICS_OPTIONS": includegraphics_options,
                        "EXTRAPACKAGES": get_extra_packages(figureName)}
    #IPython.embed()
    latex_code = latex_code.format(**all_replacements)
    return latex_code


def psfragListToString(psfragList):
    """
    Convert a list of lists of strings with the psfrag replacements to a
    single string with the psfrag commands.

    As an example, suppose we have the list bellow
    : [['BER', 'BER', '[cc][cc]']
    :  ['Title', '\\"Interference Alignment\\" for the SVD case', '']
    :  ['Eb/N0', '$Eb/N_0$', '']]
    It will be converted to
    : \psfrag{BER}[cc][cc]{BER}
    : \psfrag{Title}{\"Interference Alignment\" for the SVD case}
    : \psfrag{Eb/N0}{$Eb/N_{0}$}

    Parameters
    ----------
    psfragList : list of strings
    """
    psfragText = ""
    for i in psfragList:
        psfragText = psfragText + "\\psfrag{{{0}}}{1}{{{2}}}".format(i[0], i[2], i[1]) + "\n"
    return psfragText.strip()


def crop_pdf(filename):
    """Call the pdfcrop program to crop a PDF file.

    Parameters
    ----------
    filename : str
        The name of the PDF file (with the extension).
    """
    import os
    basename, extension = os.path.splitext(filename)
    aux_filename = ''.join([basename, '_aux', extension])

    # If the extension was not provided, assume .pdf
    if extension == '':
        extension = '.pdf'
        filename = ''.join([filename, extension])

    # Rename the file so that the output of pdfcrop later can have the
    # original name
    os.rename(filename, aux_filename)

    # Crop the PDF file
    SHELL_COMMAND_CROP_PDF_FILE = r"pdfcrop {0} {1} > /dev/null".format(aux_filename, filename)

    exit_code = call(SHELL_COMMAND_CROP_PDF_FILE, shell=True)
    os.remove(aux_filename)


def psfrag_replace(figureFullName, psfrags, includegraphics_options="", crop=True):
    """
    Perform the psfrag replacements in an eps file.

    Parameters
    ----------
    figureFullName : str
        Nome do arquivo eps (sem extensao).
    psfrags : list of strings
        List with the psfrag replacements. Each element must be a list with
        3 elements, where the first element is the original text to be
        replaced, the second element is the text replacement and the third
        element has the parameters to be passed to the pasfrag command (Ex:
        "[cc][cc]" - without the quotes).
        Ex:
        [['BER', 'BER', '[cc][cc]']
         ['Title', '\\"Interference Alignment\\" for the SVD case', '']
         ['Eb/N0', '$Eb/N_0$', '']]
    includegraphics_options : str
        Options that should be passed to the includegraphics package
        (INCLUDING THE BRACKETS).
    crop : boll
        If True, the final PDF will be cropped using the pdfcrop program.
    """
    (directory, filename) = os.path.split(figureFullName)
    # If the file name is a full path, change current working directory to
    # the directory containing the eps file
    if (directory):
        os.chdir(directory)

    latex_code = prepareLatexCode(filename, psfrags, includegraphics_options)

    # Open file to save latex code
    fileName = "{0}_psfrag_replace".format(filename)
    tex_fileName = "{0}.tex".format(fileName)
    tex_fileName_debug = "{0}_debug.tex".format(fileName) # This will only be used whem compilation fail
    dvi_fileName = "{0}.dvi".format(fileName)
    ps_fileName = "{0}.ps".format(fileName)
    f = open(tex_fileName, 'w')
    #f.write(latex_code.encode('utf-8'))
    f.write(latex_code)
    f.close()

    shell_command_latex = "latex -halt-on-error -interaction=batchmode {0} > /dev/null".format(tex_fileName)
    # Option '-q' in dvips is for the quiet mode
    shell_command_dvi_to_pdf = "dvips -q {0} && ps2pdf {1} {2}.pdf".format(dvi_fileName, ps_fileName, filename)

    # Called to remove the generated temporary (latex related) files.
    shell_command_remove_temporary_files = "rm -f {0}.*".format(fileName)

    # Called to remove the generated debug (latex related) files after a
    # successful compilation.
    shell_command_remove_debug_files = "rm -f {0}_debug.*".format(fileName)

    print ("xxxxxxxxxx RUNNING LATEX xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    exit_code = call(shell_command_latex, shell=True)
    print("Latex exit code is: {0}".format(exit_code))
    if(exit_code != 0):  # Latex file could not be processed
        os.rename(tex_fileName, tex_fileName_debug)
        print("The tex file could not be compiled. Compile the file {0} manually to get some clue about the problem.".format(tex_fileName_debug))

        # Remove temporary files
        call(shell_command_remove_temporary_files, shell=True)
        return exit_code
    else:
        # Remove debug files (from a possibly unsuccessful compilation)
        call(shell_command_remove_debug_files, shell=True)

        # # Remove the epsfrag2pdf.* files (except epsfrag2pdf.py) if it they
        # # were left by a previous unsuccessful compilation.
        # call("rm -f epsfrag2pdf.*[!py]", shell=True)

    # If latex processing was ok we just need to convert to ps and then to
    # pdf (as well as removing the temporary files)
    print ("xxxxxxxxxx RUNNING DVIPS AND PS2PDF xxxxxxxxxxxxxxxxxxxxxxxx")
    dvi_to_pdf_exit_code = call(shell_command_dvi_to_pdf, shell=True)

    if dvi_to_pdf_exit_code != 0:
        os.rename(tex_fileName, tex_fileName_debug)
        print("The dvips of the ps2pdf command could not be performed by some reason. Compile the file {0} manually to get some clue about the problem.".format(tex_fileName_debug))
    else:
        # If the PDF file was successfully generated all we need to do now
        # is to crop the PDF to remove the whitespace if the 'crop'
        # argument is True.
        if crop is True:
            crop_pdf(filename)

    print("dvips or ps2pdf exit code: {0}".format(dvi_to_pdf_exit_code))
    print ("xxxxxxxxxx REMOVING TEMPORARY FILES xxxxxxxxxxxxxxxxxxxxxxxx")
    rm_exit_code = call(shell_command_remove_temporary_files, shell=True)
    print("Remove files exit code: {0}".format(rm_exit_code))

    return dvi_to_pdf_exit_code


def print_help():
    help = """Usage: eps2pdf_converter fileName psfragsFileName
       - filename is the name of the eps file (without extension)
       - psfragsFileName is the name of a file containing the psfrag
         replacements. If not provided, the name 'fileName.psfrags' will be
         used"""

    print(help)
# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

if __name__ == '__main__1':
    print ("Extra packages:\n{0}".format(get_extra_packages('nome')))

if __name__ == '__main__1':
    fileName = "test.psfrags"
    fId = open(fileName)
    text = fId.read()
    text = text.split("\n")
    print(text)


if __name__ == '__main__':
    import sys
    if (len(sys.argv) < 2):
        print_help()
        sys.exit(1)

    fileName = sys.argv[1]
    if (len(sys.argv) < 3):
        repsFile = fileName + ".psfrags"
    else:
        repsFile = sys.argv[2]

    print("eps file: {0}.eps\npsgrag replacements file: {1}".format(fileName, repsFile))
    fId = open(repsFile)
    psfrag_text = fId.read()
    #print(psfrag_text)

    if psfrag_text[0] == "[":
        # Lets change from a single multiline string to a list of
        # strings. The first element contains the string with the options
        # for the includegraphics package.
        all_replacements = psfrag_text.split("\n")
        psfrag_text = "\n".join(all_replacements[1:])
        includegraphics_options = all_replacements[0]
        psfrag_replace(sys.argv[1], psfrag_text, includegraphics_options)
    else:
        psfrag_replace(sys.argv[1], psfrag_text)


# psfrag_replace_script ends here
