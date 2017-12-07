%global version 1.18.11
%global e_dir %{_builddir}/electron
%global arch %(test $(rpm -E%?_arch) = x86_64 && echo "x64" || echo "ia32")
%global srcdir %{_builddir}/apm

%global __provides_exclude_from %{nodejs_sitelib}/.*/node_modules
%global __requires_exclude_from %{nodejs_sitelib}/.*/node_modules
%global __requires_exclude (npm)

Name:    atom-package-manager
Version: %{version}
Release: 1%{dist}
Summary: Atom package manager

Group:   Applications/System
License: MIT
URL:     https://github.com/atom/apm

BuildRequires: coffee-script
BuildRequires: git
BuildRequires: libsecret-devel
BuildRequires: nodejs-packaging
BuildRequires: npm

%description
apm - Atom Package Manager
Discover and install Atom packages powered by https://atom.io

%prep
if ! [ -d %{srcdir}/.git ]; then
  git clone %{url}.git %{srcdir}
fi

pushd %{srcdir}
  git reset --hard
  git fetch --all
  git checkout v%{version}
  rm package-lock.json
popd

%build
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags}"

pushd %{srcdir}
  # Compile the coffee sources
  ${Coffee:-coffee} -c --no-header -o lib src/*.coffee
  # Install the node dependencies
  npm install --loglevel info -g --prefix build
popd

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
