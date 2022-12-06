# !/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This script collects all DBLP citation keys from all .tex files in a given
# directory and downloads missing BibTeX records from DBLP to a given BibTeX
# file. Tested with Python 3.10.
#
# Copyright (c) 2014 Sebastian Abshoff <sebastian@abshoff.it>
#           (c) 2022 Greta Tanudjaja
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from pathlib import Path
import urllib.request as req
import os
import os.path
import re
import argparse

TEX_FILES_DIRECTORY = './'  # (sub)directory containing the .tex files
ignore_tex_files = set()  # files within the directory that should be ignored

known_keys = set([])
unused_keys = set([])

cogprints_keys = set([])
fetched_cogprints_keys = set([])

dblp_keys = set([])
fetched_dblp_keys = set([])

microsoft_keys = set([])
fetched_microsoft_keys = set([])

springer_keys = set([])
fetched_springer_keys = set([])

unknown_cogprints_keys = cogprints_keys - known_keys
unknown_dblp_keys = dblp_keys - known_keys
unknown_microsoft_keys = microsoft_keys - known_keys
unknown_springer_keys = springer_keys - known_keys

parser = argparse.ArgumentParser(description='Create BibTeX input and output files.')
parser.add_argument('--c', default='cogprints.bib', type=str, help='Cogprints BibTeX input and output file; always ends in .bib and only accepts strings.')
parser.add_argument('--d', default='dblp.bib', type=str, help='DBLP BibTeX input and output file; always ends in .bib and only accepts strings.')
parser.add_argument('--m', default='microsoft.bib', type=str, help='Microsoft BibTeX input and output file; always ends in .bib and only accepts strings.')
parser.add_argument('--s', default='springer.bib', type=str, help='Springer BibTeX input and output file; always ends in .bib and only accepts strings.')
args = parser.parse_args()

cogprints_bibtex_file = args.c
dblp_bibtex_file = args.d
microsoft_bibtex_file = args.m
springer_bibtex_file = args.s


def return_bibtex():
    """This function compiles and returns the BibTeX file citations"""
    re_bibtex_citations = re.compile(r'@.*\{([^,]*),')
    return re_bibtex_citations


def read_existing_file(bibtex_file):
    """This function reads the existing BibTeX file or create a new one if it is not found"""
    if os.path.isfile(bibtex_file):
        print(f'\nReading existing BibTeX file {bibtex_file}')
        with (open(bibtex_file, encoding="utf-8")) as file:
            for _, line in enumerate(file):
                for match in re.finditer(return_bibtex(), line):
                    for key in match.groups():
                        known_keys.add(key)

    else:
        print(f'\nBibTeX file {bibtex_file} not found, will try to create it.')


def read_all_existing_files():
    """This function compiles and reads all of the existing bibliography BibTex files"""
    read_existing_file(cogprints_bibtex_file)
    read_existing_file(dblp_bibtex_file)
    read_existing_file(microsoft_bibtex_file)
    read_existing_file(springer_bibtex_file)
    print('\nThe following keys have been found in your BibTeX files:')
    for key in known_keys:
        print (f'{key}')

read_all_existing_files()


def return_tex_citation():
    """This function compiles and returns the LateX citations"""
    re_tex_citation = re.compile(r'(?:cite|citep|citet|fullciteown|autocite|textcite)\{([^}]+)}')
    return re_tex_citation


def find_keys(name, bibliography_keys):
    """This function finds the bibliography keys in the LaTeX files"""
    print(f"\nThe following {name} keys have been found in your LaTeX files:")
    for key in bibliography_keys:
        print (f'{key}')


def find_all_keys():
    """This function calls on the previous functions of finding the keys of all the bibliographies"""
    find_keys('Cogprints', cogprints_keys)
    find_keys('DBLP', dblp_keys)
    find_keys('Microsoft', microsoft_keys)
    find_keys('Springer', springer_keys)
    find_keys('unused', unused_keys)


def read_latex():
    """This function reads the LateX documents and adds the corresponding keys"""
    print('\nReading your LaTeX documents:')

    return_tex_citation()

    for dirpath, dirnames, filenames in os.walk(TEX_FILES_DIRECTORY):
        exclude = set([])
        list(set(dirnames) - exclude)

        for filename in [f for f in filenames if f.endswith('.tex') and
                         f not in ignore_tex_files]:
            print (f'{filename}')
            with open(Path(dirpath) / filename, encoding="utf-8") as file:
                for _, line in enumerate(file):
                    for match in re.finditer(return_tex_citation(), line):
                        for group in match.groups():
                            for key in group.split(','):
                                if key.strip().startswith('Cogprints:'):
                                    cogprints_keys.add(key.strip())
                                elif key.strip().startswith('DBLP:'):
                                    dblp_keys.add(key.strip())
                                elif key.strip().startswith('Microsoft:'):
                                    microsoft_keys.add(key.strip())
                                elif key.strip().startswith('Springer:'):
                                    springer_keys.add(key.strip())
                                else:
                                    unused_keys.add(key.strip())

    find_all_keys()

read_latex()


def compile_bibtex_items():
    """This function compiles the BibTeX items"""
    re_bibtex_items = re.compile(r'(@[a-zA-Z]+\{[^@]*\n})', re.DOTALL)
    return re_bibtex_items


def compile_bibtex_item_key():
    """This function compiles the BibTeX item key"""
    re_bibtex_item_key = re.compile(r'@[a-zA-Z]+\{([^,]+),\s*', re.DOTALL)
    return re_bibtex_item_key


def find_missing_keys(name):
    """This function finds the missing keys from the bibliography"""
    print(f'\nFetching BibTeX records for missing keys from {name}:')
    compile_bibtex_items()
    compile_bibtex_item_key()


def find_unknown_keys(bibtex_file, unknown_name_keys, name):
    """This function finds the unknown bibliography keys"""
    if not os.path.isfile(bibtex_file) and unknown_name_keys == set():
        print (f'\nYou do not have a {name} BibTeX file, nothing needs to be fetched. :-)')
    elif unknown_name_keys == set():
        print(f'\nYour {name} BibTeX file is up to date, nothing needs to be fetched. :-)')
    else:
        find_missing_keys(name)
    return unknown_name_keys


def open_bibtex_file(name_bibtex_file, name_bibtex_file_content, fetched_name_keys, name):
    """This function opens the BibTeX file for the bibliography and writes it to our BibTeX file if it is not already there"""
    with open(name_bibtex_file, 'a', encoding="utf8") as file:
        for match in re.finditer(compile_bibtex_items(), name_bibtex_file_content):
            for bibtex_item in match.groups():
                    key = re.match(compile_bibtex_item_key(), bibtex_item).group(1)
                    if key not in fetched_name_keys | known_keys:
                        file.write(bibtex_item)
                        file.write('\n\n')
                        fetched_name_keys.add(key)
                    else:
                        print(f'(not adding {key} to {name} BibTeX file, it is already there.)')


def open_cogprints_url():
    """This function opens Cogprints BibTeX file from its website"""
    for unknown_cogprints_key in find_unknown_keys(cogprints_bibtex_file, cogprints_keys, 'Cogprints'):
        print (f'{unknown_cogprints_key}')
    
        cogprints_url = f'https://web-archive.southampton.ac.uk/cogprints.org/{unknown_cogprints_key[10:]}.bib.html'

        with req.urlopen(cogprints_url) as response:
            cogprints_bibtex_file_content = response.read().decode('utf-8')
            open_bibtex_file(cogprints_bibtex_file, cogprints_bibtex_file_content, fetched_cogprints_keys, 'Cogprints')


def open_dblp_url():
    """This function opens DBLP BibTeX file from its website"""
    for unknown_dblp_key in find_unknown_keys(dblp_bibtex_file, dblp_keys, 'DBLP'):
        print (f'{unknown_dblp_key}')

        dblp_url = f'https://dblp.org/rec/{unknown_dblp_key[5:]}.bib'

        with req.urlopen(dblp_url) as response:
            dblp_bibtex_file_content = response.read().decode('utf-8')
            open_bibtex_file(dblp_bibtex_file, dblp_bibtex_file_content, fetched_dblp_keys, 'DBLP')


def open_microsoft_url():
    """This function opens Microsoft Research BibTeX file from its website"""
    for unknown_microsoft_key in find_unknown_keys(microsoft_bibtex_file, microsoft_keys, 'Microsoft'):
        print (f'{unknown_microsoft_key}')

        microsoft_url = f'https://www.microsoft.com/en-us/research/publication/{unknown_microsoft_key[10:]}/bibtex/'

        with req.urlopen(microsoft_url) as response:
            microsoft_bibtex_file_content = response.read().decode('utf-8')
            open_bibtex_file(microsoft_bibtex_file, microsoft_bibtex_file_content, fetched_microsoft_keys, 'Microsoft')


def open_springer_url():
    """This function opens Springer BibTeX file from its website"""
    for unknown_springer_key in find_unknown_keys(springer_bibtex_file, springer_keys, 'Springer'):
        print (f'{unknown_springer_key}')

        springer_url = f'https://citation-needed.springer.com/v2/references/10.1007/{unknown_springer_key[9:]}'

        with req.urlopen(springer_url) as response:
            springer_bibtex_file_content = response.read().decode('utf-8')
            open_bibtex_file(springer_bibtex_file, springer_bibtex_file_content, fetched_springer_keys, 'Springer')


def open_url():
    """This function calls on the previous functions of opening the BibTeX files from their website"""
    open_cogprints_url()
    open_dblp_url()
    open_microsoft_url()
    open_springer_url()

open_url()


print('\nAll done. :-)')