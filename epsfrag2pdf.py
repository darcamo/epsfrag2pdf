#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""module docstring"""

import argparse
from eps2pdf_converter import psfrag_replace
import os
from glob import glob


def read_psfrags_file(name):
    """Read the file `name.psfrags` and return a string with the psfrag replacements and the includegraphics options (if any).

    The psfrag replacements and the includegraphics options are suitable to
    be passed to the psfrag_replace method in the eps2pdf_converter module.

    Arguments:
    - `name`: Name of the .psfrags file (without the extension)
    Output:
    - A tuple with the psfrag text (as a single string) and the
      includegraphics options.
    """
    psfrags_filename = name + ".psfrags"
    fId = open(psfrags_filename)
    psfrag_text = fId.read()
    if psfrag_text[0] == "[":
        # Lets change from a single multiline string to a list of
        # strings. The first element contains the string with the options
        # for the includegraphics package.
        all_replacements = psfrag_text.split("\n")
        psfrag_text = "\n".join(all_replacements[1:])
        includegraphics_options = all_replacements[0]
    else:
        includegraphics_options = ""
    
    return (psfrag_text, includegraphics_options)


def process_files(files):
    """Call the psfrag_replace method for each file in `files`.

    Arguments:
    - `files`: list with file names.
    """

    for filename in files:
        print("Process File: {0}".format(filename))
        (psfrag_text, includegraphics_options) = read_psfrags_file(filename)
        psfrag_replace(filename, psfrag_text, includegraphics_options)
        print("\n")


def process_folders(folders):
    """Call the psfrag_replace on every file (with a corresponding .psfrags file) in every folder in `folders`.

    Arguments:
    - `folders`: list with folder names
    """
    def get_absolute_path(path):
        """Expand '~', ".", "..", etc. and return the absolute path.
        """
        return os.path.expanduser(os.path.abspath(path))

    def get_psfrags_files(folder):
        "Get a list with the file names of all '*.psgrags' files."
        return glob("{0}/*.psfrags".format(folder))

    # Process each folder in fodlers
    for folder in folders:
        # Expand especial characters in folder (such as '~' or '.')
        folder = get_absolute_path(folder)

        # Get a list of all .psfrags files in that folder
        files = get_psfrags_files(folder)

        # Remove ".psfrags" from the filenames
        files = [i[:-8] for i in files]

        # Finally, process all the files
        process_files(files)


# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert an eps file to pdf while performing psfrag replacements.')

    parser.add_argument("-F", "--folder", help="Use folder mode instead of file mode. In folder mode the arguments are treated as folder names instead of file names and all the eps files in the folder that have a bundled .psfrags file are processed.", action="store_true", dest="folder_mode")

    # # nargs='+' means that one or more arguments are required
    # parser.add_argument("-f", "--file", help="Process the file FILE.eps. There must exist a FILE.psfrags text file.", nargs='+')

    parser.add_argument("NAMEs", help="Name(s) of the file(s) to be processed (without the extension). If the -f (--folder) option is passed then those names are actually treated as folder names instead of filenames. ", nargs="+")
    args = parser.parse_args()

    # If the folder option was passed, we treat the names as folder names
    # and process all eps files (with have a bundled psfrags file) in each
    # folder.
    if args.folder_mode == True:
        process_folders(args.NAMEs)
    # If the the folder option was not passes then we simple process all
    # files in NAMEs
    else:
        process_files(args.NAMEs)


    #parser.print_help()
