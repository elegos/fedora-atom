#!/usr/bin/env bash
WDIR=`pwd`

EXIT_NO_SPEC=1

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

function sayreplace {
  say \\e[1A$@
}

TARGET=
TARGET_VERSION=

while [ $# -ne 0 ]; do
  case $1 in
    --target|-t)
      TARGET=$2
      shift
    ;;
    --version|-v)
      if ! [ "$2" = "" ]; then
        TARGET_VERSION=$2
        shift
      fi
      shift
    ;;
  esac
  shift
done

if [ "${TARGET}" = "" ] || [ "${TARGET_VERSION}" = "" ]; then
  say ""
  say "@b[[Usage:]]"
  say "$0 --target[|-t] <application> --version[|-v] <version>"
  say ""

  exit 0
fi

say ""
say "@b@green[[TARGET : @b@red${TARGET}]]"
say "@b@green[[VERSION: @b@red${TARGET_VERSION}]]"

SPEC_FOLDER="${WDIR}/spec/${TARGET}/${TARGET_VERSION}"
SPEC_FILE="${TARGET}.spec"
SPEC_PATH="${SPEC_FOLDER}/${SPEC_FILE}"
if ! [ -f "${SPEC_PATH}" ]; then
  say ""
  say "@b@red[[${SPEC_PATH} was not found]]"
  say ""
  exit ${EXIT_NO_SPEC}
fi

# Create the build folders tree
RPMDIR="${WDIR}/rpmbuild"
rpmdev-setuptree
cd "${RPMDIR}"

cp ${SPEC_PATH} "${RPMDIR}/SPECS/"
cp ${SPEC_FOLDER}/*.patch "${RPMDIR}/SOURCES/"

cd SPECS
spectool -g -R ${SPEC_FILE}
rpmbuild -ba ${SPEC_FILE}
