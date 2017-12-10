#!/usr/bin/env bash

EXTERNAL_SRC=""
DOCKER_BUILD_QUIET="-q"
#IMG=fedora_build_atom
IMG=fedora_build_atom_atom

mkdir -p build/RPMS
mkdir -p build/SRPMS

TARGET=
VERSION=

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
		;;
		"--target")
			if ! [ "$2" = "" ]; then
				TARGET=$2
				shift
			fi
		;;
		"--version")
			if ! [ "$2" = "" ]; then
				VERSION=$2
				shift
			fi
		;;
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

function build {
	mkdir -p build/RPMS
	mkdir -p build/SRPMS
	docker run --rm -ti ${EXTERNAL_SRC} \
	  --volume `pwd`/spec:/home/makerpm/spec:ro \
		--volume `pwd`/build/RPMS:/home/makerpm/rpmbuild/RPMS \
		--volume `pwd`/build/SRPMS:/home/makerpm/rpmbuild/SRPMS \
		${IMG} --target $1 --version $2
}

function buildElectron {
	say "@b[[Building electron (version $1)...]]"
	build electron $1
}

function buildApm {
	say "@b[[Building apm (version $1)...]]"
	build apm $1
}

function buildAtom {
	say "@b[[Building atom (version $1)...]]"
	build atom $1
}

say "@b[[Building docker image...]]"
#docker build -t ${IMG} ${DOCKER_BUILD_QUIET} \
# 	--build-arg UID=`id -u` .
docker build -t ${IMG} ${DOCKER_BUILD_QUIET} \
 	--build-arg UID=`id -u` --file Dockerfile.atom .

if ! [ "${TARGET}" = "" ] && [ "${VERSION}" ]; then
	if ! [ -d `pwd`/spec/${TARGET} ]; then
		say "@b@red[[Invalid target ${TARGET}]]"
		exit 1
	fi

	if ! [ -d `pwd`/spec/${TARGET}/${VERSION} ]; then
		say "@b@red[[Invalid version ${VERSION}]]"
		exit 1
	fi

	build ${TARGET} ${VERSION}
else
	buildElectron 1.8.2beta3
	buildApm 1.18.11
	buildAtom 1.22.1
fi
