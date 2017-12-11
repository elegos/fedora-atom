%global version 1.22.1
%global electron_ver 1.8.2-beta.3
%global arch %(test $(rpm -E%?_arch) = x86_64 && echo "x64" || echo "ia32")
%global srcdir %{_builddir}/atom

%global __provides_exclude_from %{nodejs_sitelib}/.*/node_modules
%global __requires_exclude_from %{nodejs_sitelib}/.*/node_modules
%global __requires_exclude (npm)

Name:    atom-package-manager
Version: %{version}
Release: 1%{dist}
Summary: Atom package manager

Group:   Applications/System
License: MIT
URL:     https://github.com/atom/atom

BuildRequires: libsecret-devel
BuildRequires: node-gyp
BuildRequires: nodejs

%description
Atom is a text editor that's modern, approachable, yet hack-able to the core
- a tool you can customize to do anything but also use productively without
ever touching a config file.

%prep
if ! [ -d %{srcdir}/.git ]; then
  git clone %{url}.git %{srcdir}
fi

pushd %{srcdir}
  git reset --hard
  git fetch --all
  git checkout v%{version}
popd

%build
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags}"
export npm_config_cache="${HOME}/.atom/.npm"
export npm_config_disturl="https://atom.io/download/electron"
export npm_config_target="%{electron_ver}"
export npm_config_runtime="electron"
export ATOM_ELECTRON_VERSION="%{electron_ver}"
export ATOM_ELECTRON_URL="$npm_config_disturl"
export ATOM_RESOURCE_PATH=%{srcdir}
export ATOM_HOME="$npm_config_cache"
pushd %{srcdir}
  ./script/build --install=%{buildroot}/usr
popd
exit 1

%install
cd %{srcdir}
INSTALL_DIR=%{buildroot}%{nodejs_sitelib}/atom-package-manager

install -d $INSTALL_DIR
DIRS=`ls|grep -E "^(bin|lib|native-module|node_modules|templates)$"`
for DIR in $DIRS; do
  cp -prf $DIR $INSTALL_DIR/$DIR
done

FILES=`ls|grep -vE "^(bin|build|spec|src|script|lib|native-module|templates|etc|node_modules)$|.*\.md$|.*\.coffee$"`
for FILE in $FILES; do
  install -m644 $FILE $INSTALL_DIR/$FILE
done

BIN_DIR=%{buildroot}%{nodejs_sitelib}/atom-package-manager/bin
install -d $BIN_DIR
install -m755 %{srcdir}/build/bin/* $BIN_DIR/

install -d %{buildroot}%{_bindir}
ln -sfv %{nodejs_sitelib}/atom-package-manager/bin/apm %{buildroot}%{_bindir}

%files
%defattr(-,root,root,-)
%doc apm/README.md
%license apm/LICENSE.md
%{_bindir}/apm
%{nodejs_sitelib}/atom-package-manager/

%changelog
* Thu Dec 07 2017 Giacomo Furlan <elegos@fastwebnet.it> - 1.18.11
- Release v1.18.11
- https://github.com/atom/apm/releases/tag/v1.18.11
