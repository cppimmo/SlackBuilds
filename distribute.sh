#!/bin/bash
# distribute.sh
# Use this script to create of tarballs of each SlackBuild folder.
# I'm using this to easily distribute these on my website.

SLACKBUILDS=( $(echo */) )
SIZE="${#SLACKBUILDS[@]}"
COMPRESSION="z"
BUILD_ALL=false
CURRENT_DIR=$(pwd)

PROGNAME="$(basename "$0")"
usage() {
	echo "$PROGNAME: usage: $PROGNAME [-c,--compression flag | -b,--build-all]"
	return
}

tarball_builds() {
	for ((i=0; i<"$SIZE"; ++i)); do
		tar -c"$COMPRESSION"f "$CURRENT_DIR"/build/$(echo "${SLACKBUILDS[i]}" | sed "s/\///").tar.gz \
				"${SLACKBUILDS[i]}"
	done
	return
}

build_all() {
	local current_prgm=
	mkdir --verbose "$CURRENT_DIR"/build
	# loop through every directory in CURRENT_DIR and build each into binary packages
	for ((i=0; i<"$SIZE"; ++i)); do
		cd "${SLACKBUILDS[i]}"
		echo "Current Directory is $(basename $(pwd))"
		current_prgm=$(echo "${SLACKBUILDS[i]}" | sed "s/\///")
		chmod +x "$current_prgm".info
	    source "$current_prgm".info
		if [ "$DOWNLOAD" ]; then
			wget "$DOWNLOAD"
		elif [ "$DOWNLOAD_x86_64" ]; then
			wget "$DOWNLOAD_86_64"
		fi
		chmod -x "$current_prgm".info
		chmod +x "$current_prgm".SlackBuild
		TMP="$CURRENT_DIR"/build OUTPUT="$CURRENT_DIR"/build ./"$current_prgm".SlackBuild
		cd ..
	done
	rm -f "$CURRENT_DIR"/build/build.*
	return
}

while [[ -n "$1" ]]; do
	case "$1" in
		-c | --compression)
			shift
			COMPRESSION="$1"
			;;
		-b | --build-all)
			BUILD_ALL=true
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
		if [[ "${SLACKBUILDS[i]}" = "build/" || "${SLACKBUILDS[i]}" = "build" ]]; then
			# unset "SLACKBUILDS[$i]"
		fi
		echo "${SLACKBUILDS[i]}" | sed "s/\///"		
	done
	tarball_builds
fi

if [[ "$BUILD_ALL" = true ]]; then
	if [ $(id --user) -ne 0  ]; then
		echo "You must run this script as root to use this option!" >&2
		exit 1
	fi
	build_all
fi

