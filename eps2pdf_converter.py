#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main function in this module is the psfrag_replace function, which
is where the actual job is done.

When this module is executed as a script, it will receive an argument,
which is the name of the eps file without the extension. A file with the
same name, but with extensions 'psfrags' is expected. This file should have
all the psfrag text that you would normally use in latex. For instance
    \psfrag{Something}[cc][cc]{replacement}
    \psfrag{Original text}{Replaced text}

Alternatively, the first line in this file may contain options (inside
brackets) to be passed to the includegraphics command. For instance,
    [width=\textwidth]
"""

import os


def prepareLatexCode(figureName, psfrags, includegraphics_options=""):
    """Prepare the latex code used in the eps2pdf conversion.

    Arguments:
    `figureName`:
      Nome do arquivo eps (sem extensao).

    `psfrags`:
      Substituicoes do psfrag. Pode ser uma string contendo os comandos do
      psfrag ou uma lista.

      Caso seja uma lista, cada elemento da lista deve deve ser uma lista
      com 3 elementos onde o primeiro elemento e o texto original, o
      segundo elemento e a substituicao e o terceiro elemento sao
      parametros para o psfrag (por exemplo, "[cc][cc]" - sem aspas).
      Ex:
      [['BER', 'BER', '[cc][cc]']
       ['\\"Interference Alignment\\" for the SVD case', 'Title', '']
       ['Eb/N0', '$Eb/N_0$', '']]
      Caso

    `includegraphics_options`:
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
\\setlength{{\\topmargin}}{{-1in}}
\\setlength{{\\headheight}}{{0pt}}
\\setlength{{\\headsep}}{{0pt}}
\\setlength{{\\topskip}}{{0pt}}
\\setlength{{\\textheight}}{{\\paperheight}}
\\setlength{{\\oddsidemargin}}{{-1in}}
\\setlength{{\\evensidemargin}}{{-1in}}
\\setlength{{\\textwidth}}{{\\paperwidth}}
\\setlength{{\\parindent}}{{0pt}}
\\usepackage{{tikz}}
\\special{{! TeXDict begin /landplus90{{true}}store end }}
%%\\special{{! statusdict /setpage undef }}
%%\\special{{! statusdict /setpageparams undef }}
\\pagestyle{{empty}}
\\newsavebox{{\\pict}}

\\begin{{document}}
\\begin{{lrbox}}{{\\pict}}
{PSFRAG}
\\includegraphics{INCLUDEGRAPHICS_OPTIONS}{{{FILENAME}}}
\\end{{lrbox}}
\\special{{papersize=\\the\\wd\\pict,\\the\\ht\\pict}}
\\usebox{{\\pict}}
\\end{{document}}"""
    if includegraphics_options == "":
        includegraphics_options = "[scale=1]"

    all_replacements = {"PSFRAG": psfrag_replacements,
                        "FILENAME": figureName,
                        "INCLUDEGRAPHICS_OPTIONS": includegraphics_options}
    #IPython.embed()
    latex_code = latex_code.format(**all_replacements)
    return latex_code


def psfragListToString(psfragList):
    """
    Convert a list of lists of strings with the psfrag replacements to a
    single string with the psfrag commands.

    As an example, suppose we have the list bellow
    : [['BER', 'BER', '[cc][cc]']
    :  ['\\"Interference Alignment\\" for the SVD case', 'Title', '']
    :  ['Eb/N0', '$Eb/N_0$', '']]
    It will be converted to
    : \psfrag{BER}[cc][cc]{BER}
    : \psfrag{\"Interference Alignment\" for the SVD case}{Title}
    : \psfrag{Eb/N0}{$Eb/N_{0}$}
    """
    psfragText = ""
    for i in psfragList:
        psfragText = psfragText + "\\psfrag{{{0}}}{1}{{{2}}}".format(i[0], i[2], i[1]) + "\n"
    return psfragText.strip()


def psfrag_replace(figureFullName, psfrags, includegraphics_options=""):
    """Efetua as subistituioes do psfrag em um arquivo eps.

    figureFullName:
      Nome do arquivo eps (sem extensao).
    psfrags:
      Lista contendo as substituicoes do psfrag. Cada elemento deve
      ser uma lista com 3 elementos onde o primeiro elemento e o texto
      original, o segundo elemento e a substituicao e o terceiro elemento
      sao parametros para o psfrag (por exemplo, "[cc][cc]" - sem aspas).
    includegraphics_options: Options that should be passed to the
                             includegraphics package (INCLUDING THE
                             BRACKETS)
    """
    (directory, filename) = os.path.split(figureFullName)
    # If the file name is a full path, change current working directory to
    # the directory containing the eps file
    if (directory):
        os.chdir(directory)

    latex_code = prepareLatexCode(filename, psfrags, includegraphics_options)

    # Open file to save latex code
    fileName = "psfrag_replace.tex"
    f = open(fileName, 'w')
    #f.write(latex_code.encode('utf-8'))
    f.write(latex_code)
    f.close()

    shell_command_latex = "latex -halt-on-error -interaction=batchmode psfrag_replace > /dev/null"
    # Option '-q' in dvips is for the quiet mode
    shell_command_dvi_to_pdf = "dvips -q psfrag_replace.dvi && ps2pdf psfrag_replace.ps %s.pdf" % filename
    shell_command_remove_temporary_files = "rm psfrag_replace*"

    print ("xxxxxxxxxx RUNNING LATEX xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    exit_code = os.system(shell_command_latex)
    print("Latex exit code is: {0}".format(exit_code))
    if(exit_code != 0):  # Latex file could not be processed
        os.system("mv psfrag_replace.tex epsfrag2pdf.tex")
        print("The tex file could not be compiled. Compile the file epsfrag2pdf.tex manually to get some clue about the problem.")
        os.system(shell_command_remove_temporary_files)
        return exit_code
    else:
        # Remove the epsfrag2pdf.* files if it they were left by a previous
        # unsuccessful compilation.
        os.system("rm -f epsfrag2pdf.*")

    # If latex processing was ok we just need to convert to ps and then to
    # pdf (as well as removing the temporary files)
    print ("xxxxxxxxxx RUNNING DVIPS AND PS2PDF xxxxxxxxxxxxxxxxxxxxxxxx")
    exit_code = os.system(shell_command_dvi_to_pdf)

    if exit_code != 0:
        os.system("mv psfrag_replace.tex epsfrag2pdf.tex")
        print("The dvips of the ps2pdf command could not be performed by some reason. Compile the file epsfrag2pdf.tex manually to get some clue about the problem.")

    print("dvips or ps2pdf exit code: {0}".format(exit_code))
    print ("xxxxxxxxxx REMOVING TEMPORARY FILES xxxxxxxxxxxxxxxxxxxxxxxx")
    os.system(shell_command_remove_temporary_files)
    return exit_code


def print_help():
    help = """Usage: eps2pdf_converter fileName psfragsFileName
       - filename is the name of the eps file (without extension)
       - psfragsFileName is the name of a file containing the psfrag replacements."""
    print(help)
# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

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
