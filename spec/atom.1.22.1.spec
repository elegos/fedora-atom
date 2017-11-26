%global version 1.22.1
%global electron_ver 1.8.1-beta1
%global srcdir %{_builddir}/atom
%global arch x64
%global arch %(test $(rpm -E%?_arch) = x86_64 && echo "x64" || echo "ia32")

Name:    atom
Version: %{version}
Release: 1.22.1
Summary: A hack-able text editor for the 21st century

Group:   Applications/Editors
License: MIT
URL:     https://github.com/atom/atom

Requires: electron = %{electron_ver}

%description
Atom is a text editor that's modern, approachable, yet hack-able to the core
- a tool you can customize to do anything but also use productively without
ever touching a config file.

Visit https://atom.io to learn more.

%prep

# TODO
