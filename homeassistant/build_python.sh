#!/bin/bash
PY_VER=${1}
FOLDER=Python-${PY_VER}
FILE=${FOLDER}.tar.xz
URL=https://www.python.org/ftp/python/${PY_VER}/${FILE}
HA_USER=homeassistant
VENV_BASE=/srv/homeassistant

INSTALLED=$(find /usr/lib -name libjemalloc.so -print|wc -l)
if [ ${INSTALLED} -eq 0 ]; then
	echo "Updating and installing required packages"
	sudo apt update

	echo "Assuming required packages may not be installed"
	sudo apt -y install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline-dev \
		libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev \
		zlib1g-dev libudev-dev libc-dev libffi-dev libbluetooth-dev libtirpc-dev libjemalloc-dev \
		cargo

	sudo ldconfig
fi

if [ ! -f ${FILE} ]; then
	echo "Getting ${URL}"
	wget ${URL}
	if [ ${?} -ne 0 ]; then
		echo "Couldn't get Python ${PY_VER}, aborting"
		exit
	fi
fi

if [ ! -d ${FOLDER} ]; then
	echo "Extracting ${FILE}"
	tar xf ${FILE}
fi

echo "Preparing to compile"
cd ${FOLDER}

## Taken from https://github.com/home-assistant/docker-base/blob/cde15391fb3cee45200357d850905410162f9e6b/python/3.8/Dockerfile
## set thread stack size to 1MB so we don't segfault before we hit sys.getrecursionlimit()
## https://github.com/alpinelinux/aports/commit/2026e1259422d4e0cf92391ca2d3844356c649d0
nproc=$(cat /proc/cpuinfo|egrep -c "^processor")
echo "Configuring, then making, then installing" \
    && ./configure \
        --enable-optimizations \
        --enable-shared \
        --with-lto \
        --with-system-expat \
        --with-system-ffi \
        --without-ensurepip \
    && make -j "$(nproc)" \
        LDFLAGS="-Wl,--strip-all" \
        CFLAGS="-fno-semantic-interposition -fno-builtin-malloc -fno-builtin-calloc -fno-builtin-realloc -fno-builtin-free -ljemalloc" \
        EXTRA_CFLAGS="-DTHREAD_STACK_SIZE=0x100000" \
    && sudo make alt install

# Create the venv
if [ ! -d ${VENV_BASE} ]; then
  mkdir ${VENV_BASE}
  chown ${HA_USER} ${VENV_BASE}
fi
if [ ! -d ${VENV_BASE}/venv_${PY_VER} ]; then
  sudo -u ${HA_USER} -H -s <<-EOM
  python$(echo ${PY_VER}|rev|cut -d. -f2-|rev) -m venv ${VENV_BASE}/venv_${PY_VER}
  source ${VENV_BASE}/venv_${PY_VER}/bin/activate
  pip3 install --upgrade homeassistant
  # This installs a bunch of relevant packages automatically, speeding up first startup
  hass --script check_config
  # Now we install requirements
  wget --quiet https://raw.githubusercontent.com/home-assistant/docker/master/requirements.txt -O - | while read LINE
  do
    pip3 install --upgrade ${LINE}
  done
  EOM
fi
