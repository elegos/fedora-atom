%global version 1.8.1
%global node_ver electron-v1.8.1
%global srcdir %{_builddir}/electron
%global arch %(test $(rpm -E%?_arch) = x86_64 && echo "x64" || echo "ia32")

Name:    electron
Version: %{version}
Release: beta1%{dist}
Summary: A hack-able text editor for the 21st century

Group:   Applications/System
License: MIT
URL:     https://github.com/electron/electron

Patch0: use-system-clang.patch
Patch1: ucontext-fix.patch

# script requirements
BuildRequires: binutils
BuildRequires: coreutils-single
BuildRequires: findutils
BuildRequires: git
BuildRequires: ncurses-compat-libs
BuildRequires: nodejs
BuildRequires: npm
BuildRequires: pkgconf-pkg-config
BuildRequires: python2
BuildRequires: which

# system clang
BuildRequires: alsa-lib-devel
BuildRequires: clang
BuildRequires: cups-devel
BuildRequires: dbus-devel
BuildRequires: GConf2-devel
BuildRequires: glib2-devel
BuildRequires: gtk2-devel
BuildRequires: libcap-devel
BuildRequires: libnotify-devel
BuildRequires: libX11-devel
BuildRequires: libXi-devel
BuildRequires: libXrandr-devel
BuildRequires: libXScrnSaver-devel
BuildRequires: libxslt-devel
BuildRequires: libXtst-devel
BuildRequires: nss-devel
BuildRequires: pciutils-devel

%description
The Electron framework lets you write cross-platform desktop applications using
JavaScript, HTML and CSS. It is based on Node.js and Chromium and is used by
the Atom editor and many other apps.

Visit https://electron.atom.io to learn more.

%prep
if ! [ -d %{srcdir}/.git ]; then
  git clone %{url}.git %{srcdir}
fi
cd %{srcdir}
git checkout v%{version}
patch -p1 < %{_sourcedir}/use-system-clang.patch

%build
cd %{srcdir}

# Configure
./script/bootstrap.py \
  --clang_dir=/usr \
  --target_arch=%{arch} \
  --verbose

# Ucontext fix
patch -p1 < %{_sourcedir}/ucontext-fix.patch

# Build
./script/create-dist.py

%install
# Install Electron
cd %{srcdir}/out/R
# These libraries are provided with the bundle
strip ${name} libffmpeg.so
strip ${name} libnode.so

install -d %{buildroot}%{_libdir}/%{name}
install -m644 *.pak *.dat *.bin libffmpeg.so libnode.so \
  %{buildroot}%{_libdir}/%{name}
install -m755 %{name} %{buildroot}%{_libdir}/%{name}
install -d %{buildroot}%{_bindir}
ln -sfv %{_libdir}/%{name}/%{name} %{buildroot}%{_bindir}
cp -r locales resources %{buildroot}%{_libdir}/%{name}
echo -n "v%{version}" > %{buildroot}%{_libdir}/%{name}/version

# Install Node headers
_headers_dest="%{buildroot}%{_libdir}/%{name}/node"
install -d -m755 ${_headers_dest}

cd %{srcdir}/vendor/node
find src deps/http_parser deps/zlib deps/uv deps/npm \
  -name "*.gypi" \
    -exec install -D -m644 '{}' "${_headers_dest}/{}" \; -or \
  -name "*.h" \
    -exec install -D -m644 '{}' "${_headers_dest}/{}" \;
install -m644 {common,config}.gypi "${_headers_dest}"
echo '%{node_ver}' > "${_headers_dest}/installVersion"

%files
%defattr(-,root,root,-)
%{_bindir}/%{name}
%{_libdir}/%{name}/

%changelog
* Thu Nov 23 2017 Giacomo Furlan <elegos@fastwebnet.it> - 1.8.1
- Release v1.8.1
- https://github.com/electron/electron/releases/tag/v1.8.1
