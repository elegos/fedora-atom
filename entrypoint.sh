#!/usr/bin/env bash
EXIT_NO_SOURCE=1
EXIT_NO_SPEC=2
EXIT_NO_ELECTRON_VERSION=3
EXIT_NO_APM_VERSION=4

ATOM_VERSION=1.22.1

declare -A ELECTRON_VERSIONS
ELECTRON_VERSIONS=(
  [1.22.1]=1.8.1
)

declare -A APM_VERSIONS
APM_VERSIONS=(
  [1.22.1]=1.18.8
)

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

while [ $# -ne 0 ]; do
  case $1 in
    --version|-v)
      if ! [ "$2" = "" ]; then
        ATOM_VERSION=$2
        shift
      fi
      shift
    ;;
  esac
  shift
done

ELECTRON_VERSION=${ELECTRON_VERSIONS[${ATOM_VERSION}]}
APM_VERSION=${APM_VERSIONS[${ATOM_VERSION}]}

if [ "$ELECTRON_VERSION" = "" ]; then
	exit ${EXIT_NO_ELECTRON_VERSION}
fi

if [ "$APM_VERSION" = "" ]; then
  exit ${EXIT_NO_APM_VERSION}
fi

say "@b@green[[APM VERSION     : @b@red${APM_VERSION}]]"
say "@b@green[[ATOM VERSION    : @b@red${ATOM_VERSION}]]"
say "@b@green[[ELECTRON VERSION: @b@red${ELECTRON_VERSION}]]"

if ! [ -f "spec/atom.${ATOM_VERSION}.spec" ]; then
  say "@b@red[[There is no such spec file for Atom]]"
  say "@b[[`ls spec/atom.*`]]"
  exit ${EXIT_NO_SPEC}
fi

# Create the build folders tree
rpmdev-setuptree
cd rpmbuild

cp ~/spec/atom.${ATOM_VERSION}.spec SPECS/atom.spec
cp ~/spec/electron.${ELECTRON_VERSION}.spec SPECS/electron.spec
cp ~/spec/apm.${APM_VERSION}.spec SPECS/apm.spec

# BUILD ELECTRON
if [ -d "/home/makerpm/patch/electron.${ELECTRON_VERSION}" ]; then
  cp -r /home/makerpm/patch/electron.${ELECTRON_VERSION}/* SOURCES/
fi

cd SPECS
spectool -g -R electron.spec
rpmbuild -ba electron.spec

# BUILD APM
cd ~/rpmbuild
rm -rf SOURCES/*
if [ -d "/home/makerpm/patch/apm.${APM_VERSION}" ]; then
  cp -r /home/makerpm/patch/apm.${APM_VERSION}/* SOURCES/
fi

cd SPECS
#spectool -g -R apm.spec
#rpmbuild -ba apm.spec

# BUILD ATOM
