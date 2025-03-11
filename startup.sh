#!/bin/bash
set -e

# Install dependencies
apt-get update && apt-get install -y --no-install-recommends software-properties-common

# Add a compatible GLIBC version
add-apt-repository ppa:ubuntu-toolchain-r/test -y
apt-get update && apt-get install -y --no-install-recommends \
    gcc-13 \
    g++-13 \
    libc6-dev

# Set default GCC version
update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-13 100
update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-13 100

# Verify GLIBC version
ldd --version
