#!/usr/bin/env bash

EXTERNAL_SRC=""
DOCKER_BUILD_QUIET="-q"
IMG=fedora_build_atom

mkdir -p build/RPMS
mkdir -p build/SRPMS

while [[ "$1" == --* ]]; do
	case "$1" in
		"--verbose-docker-build")
			DOCKER_BUILD_QUIET=""
		;;
		"--docker-image-name")
			if ! [ "$2" = "" ]; then
				IMG="$2"
				shift
			fi
		;;
		"--external-src")
			EXTERNAL_SRC="--volume `pwd`/build/BUILD:/home/makerpm/rpmbuild/BUILD --volume `pwd`/build/BUILDROOT:/home/makerpm/rpmbuild/BUILDROOT"

			if ! [ "$2" = "--no-erase" ]; then
				if [ -d build/BUILD ]; then
					rm -rf build/BUILD
				fi

				if [ -d build/BUILDROOT ]; then
					rm -rf build/BUILDROOT
				fi
			fi

			mkdir -p build/BUILD
			mkdir -p build/BUILDROOT
	esac
	shift
done

function say {
	echo -e "$@" | sed \
		-e "s/\(\(@\(red\|green\|yellow\|blue\|magenta\|cyan\|white\|reset\|b\|u\)\)\+\)[[]\{2\}\(.*\)[]]\{2\}/\1\4@reset/g" \
		-e "s/@red/$(tput setaf 1)/g"     \
		-e "s/@green/$(tput setaf 2)/g"   \
		-e "s/@yellow/$(tput setaf 3)/g"  \
		-e "s/@blue/$(tput setaf 4)/g"    \
		-e "s/@magenta/$(tput setaf 5)/g" \
		-e "s/@cyan/$(tput setaf 6)/g"    \
		-e "s/@white/$(tput setaf 7)/g"   \
		-e "s/@reset/$(tput sgr0)/g"      \
		-e "s/@b/$(tput bold)/g"          \
		-e "s/@u/$(tput sgr 0 1)/g"
}

say "@b[[Building docker image...]]"
docker build -t ${IMG} $DOCKER_BUILD_QUIET \
 	--build-arg UID=`id -u` .

say "@b[[Building...]]"
mkdir -p build/RPMS
mkdir -p build/SRPMS
docker run --rm -ti ${EXTERNAL_SRC} \
	--volume `pwd`/build/RPMS:/home/makerpm/rpmbuild/RPMS \
	--volume `pwd`/build/SRPMS:/home/makerpm/rpmbuild/SRPMS \
	${IMG} -v 1.22.1
