#!/usr/bin/env python3
# distribute.py

# Use this script to create of tarballs of each SlackBuild folder.
# I'm using this script to easily distribute built packages on my website.

import argparse
from argparse import ArgumentParser
import glob
from os import geteuid, getcwd, walk, chdir, makedirs
from os.path import basename
import re
import requests
from requests.exceptions import RequestException
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

def url_from_info(slackbuild_name):
    """Placeholder docstring."""
    return sp.check_output(
        f"source {slackbuild_name}.info && echo -n $DOWNLOAD",
        shell=True
    ).decode('utf-8')

def download_file(url) -> str:
    """Placeholder docstring."""
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

def build_all():
    """Placeholder docstring."""
    # Create tmp/output directory
    makedirs(OUTPUT_DIR, exist_ok=True)

    # Retrieve immediate subdirectories.
    #slackbuild_dirs = retrieve_slackbuild_dirs()
    slackbuild_dirs = ["sdorfehs"]
    
    for dirname in slackbuild_dirs:
        print(dirname)
        # Change to the SlackBuild's directory
        chdir(dirname)
        # Download the package source(s)
        download_file(url_from_info(dirname))

        try:
            print("Current dir:", getcwd())
            process = sp.Popen([
                #f"TMP={TMP_DIR}", f"OUTPUT={OUTPUT_DIR}",
                "bash", dirname + ".SlackBuild"
            ], stdout=sp.PIPE, stderr=sp.PIPE)

            while True:
                out = process.stdout.read(1)
                if out == '' and process.poll() != None:
                    break
                if out != '':
                    sys.stdout.write(out.decode('utf-8'))
                    sys.stdout.flush()
            print("Return code:", result.stdout)
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
