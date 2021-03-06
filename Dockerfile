FROM fedora:27

ARG UID=1000

# Install the dev tools
RUN dnf install -y \
    fedora-packager \
    rpmdevtools

# system tools
RUN dnf install -y \
    git

# libchromiumcontent
RUN dnf install -y \
    bison \
    gperf \
    ncurses-compat-libs

# electron
RUN dnf install -y \
    alsa-lib-devel \
    clang \
    cups-devel \
    dbus-devel \
    GConf2-devel \
    glib2-devel \
    gtk2-devel \
    libatomic \
    libcap-devel \
    libffi-devel \
    libgnome-keyring-devel \
    libnotify-devel \
    libX11-devel \
    libXi-devel \
    libXrandr-devel \
    libXScrnSaver-devel \
    libxslt-devel \
    libXtst-devel \
    mesa-libGL-devel \
    npm \
    nss-devel \
    pciutils-devel \
    pulseaudio-libs-devel \
    which

# apm
RUN dnf install -y \
    coffee-script \
    libsecret-devel \
    nodejs-packaging

# https://github.com/npm/npm/issues/17858
RUN npx npmc@latest install

# Create a packager user
RUN useradd makerpm -o -u $UID \
  && usermod -a -G mock makerpm

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
VOLUME ["/home/makerpm/spec"]
WORKDIR /home/makerpm
ENTRYPOINT ["/entrypoint.sh"]

USER makerpm
COPY ./spec /home/makerpm/spec
# Create the directory, so that the RPMS and SRPMS folders can be mounted as local user
RUN mkdir /home/makerpm/rpmbuild
