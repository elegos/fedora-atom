%global version 1.18.8
%global atom_ver 1.22.1
%global electron_ver 1.8.1-beta1

%global srcdir %{_builddir}
%global arch x64
%global arch %(test $(rpm -E%?_arch) = x86_64 && echo "x64" || echo "ia32")

Name:    apm
Version: %{version}
Release: 1%{dist}
Summary: A hack-able text editor for the 21st century

Group:   Applications/Editors
License: MIT
URL:     https://github.com/atom/apm

Source0: apm.js

Patch0: no-scripts.patch
Patch1: use-local-node-devel.patch
Patch2: use-python2.patch
Patch3: use-system-node.patch
Patch4: use-system-npm.patch
Patch5: use-custom-launcher.patch

BuildRequires: git
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: npm
BuildRequires: nodejs-packaging
BuildRequires: libsecret-devel
BuildRequires: coffee-script
BuildRequires: python27

Requires: node-gyp

%description
apm - Atom Package Manager
Discover and install Atom packages powered by https://atom.io

%prep
git clone %{url}.git %{srcdir}
cd %{srcdir}
git checkout v%{version}

sed -i 's|<lib>|%{_lib}|' %{S:0} %{P:1}

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

# Install the custom launcher
install -m755 %{S:0} bin/apm

%build
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags}"

cd %{srcdir}

# Build apm
coffee -c --no-header -o lib src/*.coffee
npm install --loglevel info -g --prefix build/usr

%install
cd %{srcdir}
cp -pr build/. %{buildroot}
# Remove the symlink and copy the contents of node_modules
rm -rf %{buildroot}%{nodejs_sitelib}/atom-package-manager
cp -pr build/. %{buildroot}%{nodejs_sitelib}/atom-package-manager
# Delete the build dir, build scripts, the sources, the node modules of the node_modules package
rm -rf %{buildroot}%{nodejs_sitelib}/atom-package-manager/{build,node_modules,script,src}
for ext in js json node gypi; do
  find node_modules -regextype posix-extended \
      -iname "*.${ext}" \
    ! -name '.*' \
    ! -name 'config.gypi' \
    ! -path '*deps' \
    ! -path '*test*' \
    ! -path '*obj.target*' \
    ! -path '*html*' \
    ! -path '*example*' \
    ! -path '*sample*' \
    ! -path '*benchmark*' \
    ! -regex '.*(oniguruma|git-utils|keytar)/node.*' \
      -exec install -Dm644 '{}' '%{buildroot}%{nodejs_sitelib}/atom-package-manager/{}' \;
done

# Remove some files
find %{buildroot} -regextype posix-extended -type f \
    -regex '.*js$' -exec sh -c "sed -i '/^#\!\/usr\/bin\/env/d' '{}'" \; -or \
    -regex '.*node' -exec strip '{}' \; -or \
    -name '.*' -exec rm -rf '{}' \; -or \
    -name '*.md' -delete -or \
    -name 'appveyor.yml' -delete

%files
%defattr(-,root,root,-)
%doc README.md
%license LICENSE.md
%{_bindir}/%{name}
%{nodejs_sitelib}/atom-package-manager/

%changelog
* Sun Nov 26 2017 Giacomo Furlan <elegos@fastwebnet.it> - 1.18.8
- Release 1.18.8
