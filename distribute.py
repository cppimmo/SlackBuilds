#!/usr/bin/env python3
# distribute.py

# Use this script to create of tarballs of each SlackBuild folder.
# I'm using this script to easily distribute built packages on my website.

import argparse
from argparse import ArgumentParser
import hashlib
from os import geteuid, getcwd, walk, chdir, makedirs
from os.path import basename
import re
import requests
from requests.exceptions import RequestException
import shlex
import subprocess as sp
from subprocess import CalledProcessError
import sys
from sys import exit

# Constants:
CWD = getcwd()
PRGNAM = basename(__file__)
TMP_DIR = CWD + "/build"
OUTPUT_DIR = CWD + "/build"
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
# Cmdline arguments
compression = 'z'
build_all = False

def usage():
    '''Show usage for program.'''
    print(f'''{PRGNAM}: usage: {PRGNAM} [-c,--compression flag | -b,--build-all]''')

def init_argparse() -> ArgumentParser:
    """Intialize argparse ArgumentParse instance."""
    parser = ArgumentParser(
        usage="$(prog)s [OPTION]",
        description="Build tool for my SlackBuilds."
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version=f"{parser.prog} version 1.0.0"
    )
    return parser
    
def tarball_builds():
    """Placeholder docstring."""
    return 1

def retrieve_slackbuild_dirs(dirname='.'):
    """Placeholder docstring."""
    return list(filter(
        lambda dir: dir[0] != '.',
        next(walk(dirname))[1]
    ))

def info_var_to_list(line):
    """Create a list from a space-delimited variable in a single SlackBuild .info file LINE."""
    return list(filter(
        lambda item: item,
        line.split('="', maxsplit=1)[1:][0][:-1].split(' ')
    ))

def urls_from_info(slackbuild_name):
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
            filename = ""
            if "Content-Disposition" in r.headers.keys():
                filename = re.findall("filename=(.+)", r.headers["Content-Disposition"])[0]
            else:
                filename = url.split("/")[-1]
            print(filename)

            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)

            return filename
    except RequestException as e:
        print(e)
        return ""

def checksum_validate(filename, checksum):
    """If the md5 checksum of FILENAME does not match CHECKSUM, then prompt before continuing."""
    file_checksum = hashlib.md5(open(filename, 'rb').read()).hexdigest()
    # When the file's checksum is not the same as the given argument
    if file_checksum != checksum:
        # Prompt for exit
        proceed = input("""\nA downloaded file did not match its associated checksum.
Do you still want to continue? (y/n) """)
        if not proceed in 'yY':
            sys.exit("Exiting...")

def run_command(command):
    """Placeholder docstring."""
    process = sp.Popen(shlex.split(command), stdout=sp.PIPE, stderr=sp.PIPE)
    
    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        if output:
            print(output.decode('utf-8').strip())

    rc = process.poll()
    return rc

def build_all():
    """Placeholder docstring."""
    # Create tmp/output directory
    makedirs(OUTPUT_DIR, exist_ok=True)

    # Retrieve immediate subdirectories.
    #slackbuild_dirs = retrieve_slackbuild_dirs()
    slackbuild_dirs = ["cglm"]
    
    for dirname in slackbuild_dirs:
        print(dirname)
        # Change to the SlackBuild's directory
        chdir(dirname)
        # Download the package source(s)
        
        for url, checksum in zip(*urls_from_info(dirname)):
            print(url, checksum)
            checksum_validate(download_file(url), checksum)

        try:
            print("Current dir:", getcwd())

            #run_command("python3 -h")
            #process = sp.Popen([
                #f"TMP={TMP_DIR}", f"OUTPUT={OUTPUT_DIR}",
            #   "bash", dirname + ".SlackBuild"
            #], stdout=sp.PIPE, stderr=sp.PIPE)


            #print("Return code:", result.stdout)
        except CalledProcessError as e:
            print("SlackBuild failed:", e.returncode, e.stderr, file=sys.stderr)
            exit(EXIT_FAILURE)
        # Move back into the parent directory
        chdir("..")

def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()

    print("Current working directory:", CWD)

    build_all()
    
    if not geteuid() == 0:
        print("You must run this script as root to use this option!", file=sys.stderr)
        exit(EXIT_FAILURE)

    exit(EXIT_SUCCESS)

if __name__ == "__main__":
    main()
