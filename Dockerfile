FROM fedora:27

ARG UID=1000

# Install the dev tools
RUN dnf install -y \
    fedora-packager \
    rpmdevtools

# Install electron build dependencies
RUN dnf install -y --allowerasing \
  binutils \
  coreutils-single \
  findutils \
  git \
  ncurses-compat-libs \
  nodejs \
  npm \
  pkgconf-pkg-config \
  python2 \
  which

# Build electron with system's clang
RUN dnf install -y \
  alsa-lib-devel \
  clang \
  cups-devel \
  dbus-devel \
  GConf2-devel \
  glib2-devel \
  gtk2-devel \
  libcap-devel \
  libnotify-devel \
  libX11-devel \
  libXi-devel \
  libXrandr-devel \
  libXScrnSaver-devel \
  libxslt-devel \
  libXtst-devel \
  nss-devel \
  pciutils-devel

RUN dnf install -y \
  xcb-util-devel libXdamage-devel libXcursor-devel \
  libXcomposite-devel libXext-devel libXfixes-devel \
  libXrender-devel

# Install APM build dependencies
RUN dnf install -y \
  gcc \
  gcc-c++ \
  git \
  npm \
  nodejs-packaging \
  libsecret-devel \
  coffee-script \
  python27

# Create a packager user
RUN useradd makerpm -o -u $UID \
  && usermod -a -G mock makerpm

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
WORKDIR /home/makerpm
ENTRYPOINT ["/entrypoint.sh"]

USER makerpm
COPY ./.wgetrc /home/makerpm/.wgetrc
COPY ./spec /home/makerpm/spec
COPY ./patch /home/makerpm/patch
# Create the directory, so that the RPMS and SRPMS folders can be mounted as local user
RUN mkdir /home/makerpm/rpmbuild
