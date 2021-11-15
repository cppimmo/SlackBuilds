#!/bin/bash
# distribute.sh
# Use this script to create of tarballs of each SlackBuild folder.
# I'm using this to easily distribute these on my website.
SLACKBUILDS=( $(echo */) )
SIZE="${#SLACKBUILDS[@]}"
COMPRESSION="z"

PROGNAME="$(basename "$0")"
usage() {
	echo "$PROGNAME: usage: $PROGNAME [-c,--compression compression flag]"
	return
}

tarball_builds() {
	for ((i=0; i<"$SIZE"; ++i)); do
		tar -c"$COMPRESSION"f $(echo "${SLACKBUILDS[i]}" | sed "s/\///").tar.gz \
			"${SLACKBUILDS[i]}" 
	done
	return
}

while [[ -n "$1" ]]; do
	case "$1" in
		-c | --compression)
			shift
			COMPRESSION="$1"
			;;
	    * )
			usage >&2
			exit 1
			;;
	esac
    shift
done

if [[ "$SIZE" = 0 ]]; then   
	echo "No SlackBuilds were found!" >&2
	exit 1
else
	echo "The following SlackBuilds were found: "
	for ((i=0; i<"$SIZE"; ++i)); do
		echo "${SLACKBUILDS[i]}" | sed "s/\///"		
	done
	tarball_builds
fi

