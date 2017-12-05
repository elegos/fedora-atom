%global version 1.8.2_beta.2
%global e_dir %{_builddir}/electron
%global arch %(test $(rpm -E%?_arch) = x86_64 && echo "x64" || echo "ia32")

# Required for missing function references in linking process
%global compile_cc 1
%global cc_dir %{_builddir}/libchromiumcontent

Name:    electron
Version: %{version}
Release: 1%{dist}
Summary: A hack-able text editor for the 21st century

Group:   Applications/System
License: MIT
URL:     https://github.com/electron/electron

Patch0: libcc-use-system-root.patch
Patch1: libcc-v8-use-system-root.patch
Patch2: libcc-readdir-r-fix.patch
Patch3: libcc-third-party-libdrm-multifix.patch
Patch4: libcc-client-native-pixmap-dmabuf.patch
Patch5: libcc-third-party-webkit-missing-functional-import.patch
Patch6: electron-use-system-root.patch
Patch7: electron-ucontext-fix.patch
Patch8: electron-create-dist-chromium-dir.patch

BuildRequires: alsa-lib-devel
BuildRequires: bison
BuildRequires: clang
BuildRequires: cups-devel
BuildRequires: dbus-devel
BuildRequires: GConf2-devel
BuildRequires: glib2-devel
BuildRequires: gperf
BuildRequires: gtk2-devel
BuildRequires: libatomic
BuildRequires: libcap-devel
BuildRequires: libffi-devel
BuildRequires: libgnome-keyring-devel
BuildRequires: libnotify-devel
BuildRequires: libX11-devel
BuildRequires: libXi-devel
BuildRequires: libXrandr-devel
BuildRequires: libXScrnSaver-devel
BuildRequires: libxslt-devel
BuildRequires: libXtst-devel
BuildRequires: mesa-libGL-devel
BuildRequires: ncurses-compat-libs
BuildRequires: npm
BuildRequires: nss-devel
BuildRequires: pciutils-devel
BuildRequires: pulseaudio-libs-devel
BuildRequires: which

%description
The Electron framework lets you write cross-platform desktop applications using
JavaScript, HTML and CSS. It is based on Node.js and Chromium and is used by
the Atom editor and many other apps.

Visit https://electron.atom.io to learn more.

%prep
# libchromiumcontent
%if 0%{?compile_cc}
  if ! [ -d %{cc_dir}/.git ]; then
    git clone https://github.com/electron/libchromiumcontent.git %{cc_dir}
  fi

  pushd %{cc_dir}
    git reset --hard
    git checkout electron-1-8-x
  popd
%endif

if ! [ -d %{e_dir}/.git ]; then
  git clone https://github.com/electron/electron.git %{e_dir}
fi

pushd %{e_dir}
  git reset --hard
  git checkout v1.8.2-beta.2
  git submodule update --init --recursive
  # Reset the submodules to apply the patches multiple times
  pushd %{e_dir}/vendor/node && git reset --hard && popd
  pushd %{e_dir}/vendor/breakpad/src && git reset --hard && popd
  # Patch: system root
  patch -p1 -i %{P:6}
  # Patch: ucontext fix (node / breakpad vendors)
  patch -p1 -i %{P:7}
  # create-dist.py: add chromium_dir argument
  patch -p1 -i %{P:8}
popd

%build
E_BOOTSTRAP_EXTRA_PARAMS=""
# libchromiumcontent
%if 0%{?compile_cc}
  E_BOOTSTRAP_EXTRA_PARAMS="--libcc_static_library_path %{cc_dir}/dist/main/static_library"
  E_BOOTSTRAP_EXTRA_PARAMS+=" --libcc_shared_library_path %{cc_dir}/dist/main/shared_library"
  E_BOOTSTRAP_EXTRA_PARAMS+=" --libcc_source_path %{cc_dir}/dist/main/src"
  E_CREATE_DIST_EXTRA_PARAMS="--chromium_dir %{cc_dir}/dist/main/static_library"

  CC_COMPILED_VERSION_FILE=%{_builddir}/cc_compiled_version
  CURRENT_VERSION=`cd %{cc_dir} && git log -n1|grep commit|awk '{ print $2 }'`

  # avoid compiling the same version multiple times
  if ! [ -f $CC_COMPILED_VERSION_FILE ] || ! [ "$CURRENT_VERSION" = "`cat $CC_COMPILED_VERSION_FILE`" ]; then
    pushd %{cc_dir}
      # place the patches
      cp %{P:0} patches/000-system-root.patch
      cp %{P:1} patches/v8/000-system-root.patch
      cp %{P:2} patches/000-readdir-r-fix.patch
      cp %{P:4} patches/000-dmabuf-fix.patch
      mkdir -p patches/third_party/libdrm
      cp %{P:3} patches/third_party/libdrm/000-multi-fix.patch
      mkdir -p patches/third_party/WebKit
      cp %{P:5} patches/third_party/WebKit/000-missing-functional-import.patch
      # one-time setup
      ./script/bootstrap
      # build
      ./script/update --target_arch %{arch}
      ./script/build --target_arch %{arch} --no_shared_library
      ./script/create-dist --target_arch=%{arch} --no_zip --component=static_library

      echo $CURRENT_VERSION > $CC_COMPILED_VERSION_FILE
    popd
  fi
%endif

pushd %{e_dir}
  export LDFLAGS="%{__global_ldflags} -latomic"
  ./script/bootstrap.py $E_BOOTSTRAP_EXTRA_PARAMS \
    --clang_dir /usr \
    --target_arch %{arch} \
    --verbose

  ./script/build.py -c Release

  ./script/create-dist.py $E_CREATE_DIST_EXTRA_PARAMS
popd

%install

%files

%changelog
* Thu Nov 23 2017 Giacomo Furlan <elegos@fastwebnet.it> - 1.8.1
- Release v1.8.1
- https://github.com/electron/electron/releases/tag/v1.8.1
