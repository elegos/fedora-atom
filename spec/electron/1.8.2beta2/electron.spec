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

# libchromiumcontent dependencies
BuildRequires: bison
BuildRequires: gperf
BuildRequires: ncurses-compat-libs

# electron dependencies
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
popd

%build
E_BOOTSTRAP_EXTRA_PARAMS=""
# libchromiumcontent
%if 0%{?compile_cc}
  E_BOOTSTRAP_EXTRA_PARAMS="--libcc_static_library_path %{cc_dir}/src/out-%{arch}/static_library"
  E_BOOTSTRAP_EXTRA_PARAMS+=" --libcc_source_path %{cc_dir}"

  CC_COMPILED_VERSION_FILE=%{_builddir}/cc_compiled_version
  CURRENT_VERSION=`cd %{cc_dir} && git log -n1|grep commit|awk '{ print $2 }'`

  # avoid compiling the same version multiple times
  if ! [ -f $CC_COMPILED_VERSION_FILE ] || ! [ "$CURRENT_VERSION" = "`cat $CC_COMPILED_VERSION_FILE`" ]; then
    pushd %{cc_dir}
    # one-time setup
    ./script/bootstrap
    # build
    ./script/update --target_arch %{arch}
    ./script/build --target_arch %{arch} --no_shared_library
    echo $CURRENT_VERSION > $CC_COMPILED_VERSION_FILE
    popd
  fi
%endif

pushd %{e_dir}
./script/bootstrap.py $E_BOOTSTRAP_EXTRA_PARAMS \
  --clang_dir /usr \
  --target_arch %{arch} \
  --verbose
popd

%install

%files

%changelog
* Thu Nov 23 2017 Giacomo Furlan <elegos@fastwebnet.it> - 1.8.1
- Release v1.8.1
- https://github.com/electron/electron/releases/tag/v1.8.1
