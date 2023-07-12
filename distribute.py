#!/usr/bin/env python3
# distribute.py

# Use this script to create of tarballs of each SlackBuild folder.
# I'm using this script to easily distribute built packages on my website.

import argparse
from argparse import ArgumentParser
import hashlib
from os import geteuid, getcwd, walk, chdir, makedirs
from os import EX_OK, EX_USAGE, EX_SOFTWARE, EX_NOPERM, EX_DATAERR
from os.path import basename
import re
import requests
from requests.exceptions import RequestException
import shlex
import subprocess as sp
from subprocess import CalledProcessError
import sys
from sys import exit
from urllib.parse import urlparse

# Constants:
CWD = getcwd()
PRGNAM = basename(__file__)
DEF_TMP_DIR = CWD + "/build"
DEF_OUTPUT_DIR = CWD + "/build"
# Globals:
ignore_checksums = False

def check_root() -> bool:
    if not geteuid() == 0:
        print("You must run this script as root to use this option!", file=sys.stderr)
        exit(EX_NOPERM)    

def init_argparse() -> ArgumentParser:
    """Intialize argparse ArgumentParse instance."""
    parser = ArgumentParser(usage=f"{PRGNAM} [OPTION(s)]",
                            description="Build tool for my SlackBuilds.")
    parser.add_argument("-s", "--build-single",
                        help="build only the SlackBuild named BUILD_SINGLE")
    parser.add_argument("-a", "--build-all", action="store_true",
                        help="build every available SlackBuild")
    parser.add_argument("-o", "--options", action="store_true",
                        help="supply options for each script when using --build-single or --build-all")
    parser.add_argument("--tmp-dir", default=DEF_TMP_DIR,
                        help="directory where package source will be extracted")
    parser.add_argument("--output-dir", default=DEF_OUTPUT_DIR,
                        help="directory which package tarball will be placed")
    parser.add_argument("--ignore-checksums", action="store_true",
                        help="do not perform checks on downloaded package sources")
    parser.add_argument("-v", "--version", action="version",
                        version=f"{parser.prog} version 1.0.0")
    return parser

def retrieve_slackbuild_dirs(dirname='.') -> list:
    """Retrieve all visible immediate directorys in DIRNAME."""
    excludes = ["build", "__pycache__"]
    return list(filter(
        lambda dir: (dir[0] != '.') and (not dir in excludes),
        next(walk(dirname))[1]
    ))

def info_var_to_list(line) -> list:
    """Create a list from a space-delimited variable in a single SlackBuild .info file LINE."""
    return list(filter(
        lambda item: item,
        line.split('="', maxsplit=1)[1:][0][:-1].split(' ')
    ))

def urls_from_info(slackbuild_name) -> tuple:
    """Return a tuple of url and checksum lists from a SLACKBUILD_NAME.info file."""
    urls = []
    checksums = []
    # Open SLACKBUILD_NAME.info file for reading
    fin = open(f"{slackbuild_name}.info", "rt")
    while True:
        line = fin.readline()
        if not line:
            break
        # Strip trailing newlines/whitespace from input line
        line = line.rstrip()
        # Splice results of info_var_to_list() into url & checksum lists
        if line.startswith('DOWNLOAD'):
            urls.extend(info_var_to_list(line))
        elif line.startswith('MD5SUM'):
            checksums.extend(info_var_to_list(line))
    # Return tuple of urls & checksums
    return (urls, checksums)

def download_file(url) -> str:
    """Download file at URL and preserve the original filename."""
    try:
        with requests.get(url, stream=True) as r:
            # Use basename of url path instead of Content-Disposition
            filename = basename(urlparse(url).path)

            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)

            return filename
    except RequestException as e:
        print(e)

def checksum_validate(filename, checksum) -> None:
    """If the md5 checksum of FILENAME does not match CHECKSUM, then prompt before continuing."""
    file_checksum = hashlib.md5(open(filename, 'rb').read()).hexdigest()
    # When the file's checksum is not the same as the given argument
    if file_checksum != checksum:
        # Prompt for exit
        proceed = input("""\nA downloaded file did not match its associated checksum.
Do you still want to continue? (y/n) """)
        if not proceed in 'yY':
            print("Exiting...")
            exit(EX_OK)
          
def build(slackbuild_dirs, tmp_dir, output_dir, supply_options=False) -> None:
    """Build SlackBuilds determined by SLACKBUILD_DIRS.
    TMP_DIR The TMP path variable of a SlackBuild.
    OUTPUT_DIR The OUTPUT path variable of a SlackBuild.
    SUPPLY_OPTIONS Whether or not the user will be prompted for options."""
    print(f"TMP_DIR: {tmp_dir}\nOUTPUT_DIR: {output_dir}\n")
    # Convert slackbuild_dirs to a list if it is a string
    if isinstance(slackbuild_dirs, str):
        slackbuild_dirs = [ slackbuild_dirs ]
        
    slackbuild_options = dict.fromkeys(slackbuild_dirs)

    if supply_options: 
        print("""Supply build options for each SlackBuild
Options use the following format: OPTION1=VALUE OPTION2=VALUE
See the README for each SlackBuild for more information.\n""")
        for dirname in slackbuild_dirs:
            options = input(f"Options for {dirname}: ")
            slackbuild_options[dirname] = options
    
    for dirname in slackbuild_dirs:
        print(f"Fetching package sources for {dirname}...")
        # Change to the SlackBuild's directory
        chdir(dirname)
        # Download the package source(s):
        for url, checksum in zip(*urls_from_info(dirname)):
            print(f"URL: {url}, CHECKSUM: {checksum}")

            filename = download_file(url)
            if not ignore_checksums:
                checksum_validate(filename, checksum)

        try:
            print(f"\nNow building {dirname}...\n")
            
            options = slackbuild_options[dirname] or ""
            # Run slackbuild with options, if given:
            sp.check_call(f"{options} TMP={tmp_dir} OUTPUT={output_dir} bash {dirname}.SlackBuild",
                          shell=True)

            print(f"Build of {dirname} now complete.\n")
        except CalledProcessError as e:
            print("SlackBuild failed with exitcode: ", e.returncode, file=sys.stderr)
            exit(EX_SOFTWARE)
        # Move back into the parent directory
        chdir("..")

    print("All SlackBuild packages created successfully.")

def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()

    tmp_dir = args.tmp_dir if args.tmp_dir else DEF_TMP_DIR
    output_dir = args.output_dir if args.output_dir else DEF_OUTPUT_DIR
    # Retrieve immediate subdirectories.
    slackbuild_dirs = retrieve_slackbuild_dirs()
    
    # Operate on given arguments:
    if args.ignore_checksums:
        ignore_checksums = True
    
    if args.build_single:
        check_root()

        if not args.build_single in slackbuild_dirs:
            print("A SlackBuild with the provided name does not exist!", file=sys.stderr)
            exit(EX_DATAERR)

        print(f"Creating SlackBuild package: {args.build_single}...\n")
        build(args.build_single, tmp_dir, output_dir, args.options)
    elif args.build_all:
        check_root()

        print("Creating all SlackBuild packages...\n")
        build(slackbuild_dirs, tmp_dir, output_dir, args.options)
    else:
        parser.print_help()
        exit(EX_USAGE)

    exit(EX_OK)

if __name__ == "__main__":
    main()
