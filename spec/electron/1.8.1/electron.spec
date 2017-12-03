%global version 1.8.1
%global node_ver electron-v1.8.1
%global srcdir %{_builddir}/electron
%global arch %(test $(rpm -E%?_arch) = x86_64 && echo "x64" || echo "ia32")

# Required for missing function references in linking process
%global compile_cc 1
%global cc_dir %{srcdir}/vendor/libchromiumcontent
%global depot_tools_dir %{srcdir}/vendor/depot_tools

Name:    electron
Version: %{version}
Release: beta1%{dist}
Summary: A hack-able text editor for the 21st century

Group:   Applications/System
License: MIT
URL:     https://github.com/electron/electron

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

# libchromiumcontent
BuildRequires: bison
BuildRequires: gperf
BuildRequires: gyp
BuildRequires: libffi-devel
BuildRequires: libgnome-keyring-devel
BuildRequires: mesa-libGL-devel
BuildRequires: ninja-build
BuildRequires: pulseaudio-libs-devel
BuildRequires: v8

# System's clang: otherwise it will complain about missing header files
Patch0: use-system-clang.patch
# Ucontext fix: recently struct ucontext was renamed to ucontext_t
Patch1: ucontext-fix.patch
# libchromiumcontent: use the system's tools
Patch2: libchromiumcontent-use-system-tools.patch
# libchromiumcontent: apply patches between the update and the build process
Patch3: libchromiumcontent-build-with-patches.patch
# libchromiumcontent v8: use the system's root
Patch4: libchromiumcontent-v8-use-system-root.patch
# libchromiumcontent: readdir_r has been deprecated and breaks the build
Patch5: libchromiumcontent-readdir-fix.patch
# libchromiumcontent > libdrm: makes use of makedev without importing sys/sysmacros.h
# libchromiumcontent > libdrm: readdir_r has been deprecated and breaks the build
Patch6: libchromiumcontent-libdrm-multifix.patch
# libchromiumcontent: fix local_dma_buf_sync => dma_buf_sync
Patch7: libchromiumcontent-client-native-pixmap-dmabuf.patch
# libchromiumcontent > v8: if using their mksnapshot, an unknown symbol exception will raise
Patch8: libchromiumcontent-v8-use-system-mksnapshot.patch
# libchromiumcontent > v8: fix for missing GetArrayBufferAllocator call
Patch9: libchromiumcontent-v8-get-array-buffer-allocator-fix.patch
# libchromiumcontent > webkit: missing functional import
Patch10: libchromiumcontent-webkit-fix.patch

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
git reset --hard
git checkout v%{version}
# System clang
patch -Np1 -i %{P:0}
git submodule update --init --recursive
# Ucontext fix
pushd %{srcdir}/vendor/node && git reset --hard && popd
pushd %{srcdir}/vendor/breakpad && git reset --hard && popd
if [ -d "%{srcdir}/vendor/breakpad/src" ]; then
  pushd %{srcdir}/vendor/breakpad/src && git reset --hard && popd
fi
patch -Np1 -i %{P:1}
# Ucontext fix end

%if 0%{?compile_cc}
pushd %{cc_dir}
# use system's tools
git reset --hard
git submodule update --init --recursive
if [ -d "%{cc_dir}/src/v8" ]; then
  pushd %{cc_dir}/src/v8 && git reset --hard && popd
fi
patch -Np1 -i %{P:2}
# use system's tools end
popd
# patch the build script to apply the patch between the steps
patch -Np1 -i %{P:3}
%endif

%build
cd %{srcdir}

# Configure
%if 0%{?compile_cc}
  export PATH="${PATH}:%{depot_tools_dir}"
  sed -i 's|<use-system-root-patch>|%{P:4}|' %{srcdir}/script/build-libchromiumcontent.py
  sed -i 's|<readdir-fix-patch>|%{P:5}|' %{srcdir}/script/build-libchromiumcontent.py
  sed -i 's|<libdrm-makedev-fix-patch>|%{P:6}|' %{srcdir}/script/build-libchromiumcontent.py
  sed -i 's|<dma-buf-sync-patch>|%{P:7}|' %{srcdir}/script/build-libchromiumcontent.py
  sed -i 's|<v8-use-system-mksnapshot>|%{P:8}|' %{srcdir}/script/build-libchromiumcontent.py
  sed -i 's|<v8-get-array-buffer-allocator>|%{P:9}|' %{srcdir}/script/build-libchromiumcontent.py
  sed -i 's|<webkit-fix>|%{P:10}|' %{srcdir}/script/build-libchromiumcontent.py

  # reset the previously src patched files
  if [ -d "%{cc_dir}/src" ]; then
    pushd %{cc_dir}/src
      git checkout base/files/file_enumerator_posix.cc
      git checkout build/config/sysroot.gni
      git checkout net/disk_cache/simple/simple_index_file_posix.cc
      git checkout sandbox/linux/services/proc_util.cc
      git checkout third_party/WebKit/Source/platform/graphics/gpu/SharedGpuContext.h
      git checkout ui/gfx/linux/client_native_pixmap_dmabuf.cc

      if [ -d third_party/libdrm/src ]; then
        pushd third_party/libdrm/src
          git checkout xf86drm.c
        popd
      fi
    popd
  fi

  ./script/bootstrap.py \
    --build_release_libcc \
    --clang_dir=/usr \
    --target_arch=%{arch} \
    --verbose
%else
  ./script/bootstrap.py \
    --clang_dir=/usr \
    --target_arch=%{arch} \
    --verbose
%endif

# Build electron
cd %{srcdir}
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
