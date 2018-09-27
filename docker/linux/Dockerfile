FROM ubuntu:16.04

ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
      apt-get -q -y --no-install-recommends install \
              wget git file g++ cmake \
              python python3 python3-pip python3-setuptools python3-wheel \
              apt-transport-https locales && \
    locale-gen en_US.UTF-8 && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/man && \
    python3 -m pip install --upgrade pip && \
    pip3 install conan==1.9.0 && \
    conan --version

ARG GIT_COMMIT

RUN cd /opt && \
    git clone https://github.com/status-im/status-conan.git && \
    cd /opt/status-conan && \
    GIT_COMMIT=${GIT_COMMIT} \
    git reset --hard ${GIT_COMMIT} && \
    rm /usr/bin/python && \
    ln $(which python3) /usr/bin/python && \
    cd && rm -rf .git && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/man

WORKDIR /opt/status-conan
ENV CONAN_LOG_RUN_TO_FILE 1
ENV CONAN_LOGGING_LEVEL 10
ENV CONAN_PRINT_RUN_COMMANDS 1
ENV CONAN_NON_INTERACTIVE 1
ENV CONAN_COLOR_DISPLAY 1
ENV CONAN_SYSREQUIRES_SUDO 0
ENV CONAN_TRACE_FILE /tmp/conan_trace.log
ENV CONAN_VERBOSE_TRACEBACK 1
ENV CONAN_LOGIN_USERNAME_STATUS_IM status

# Export, build and test MXE toolchain
RUN conan create packages/mxetoolchain-x86_64-w64-mingw32/ mxetoolchain-x86_64-w64-mingw32/5.5.0-1@status-im/stable \
                 -pr ./profiles/status-mingw32-x86_64

# Generate profiles from templates
RUN conan install -g json mxetoolchain-x86_64-w64-mingw32/5.5.0-1@status-im/stable -pr ./profiles/status-mingw32-x86_64 && \
    python3 ./profiles/generate-profiles.py ./profiles conanbuildinfo.json

ARG QT_OPTIONS="webkit=False"

# Export, build and test Qt5 package
RUN conan create packages/qt5-mxe/ qt5-mxe/5.11.2@status-im/stable \
                 -pr ./profiles/status-mingw32-x86_64 \
                 -o ${QT_OPTIONS} && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/man

RUN conan remote add --insert 0 status-im https://conan.status.im

ENV CONAN_LOGGING_LEVEL 50
ENV CONAN_NON_INTERACTIVE 0

ADD Makefile-docker Makefile

# These are the UID and GID values used by Jenkins
RUN addgroup --gid 1002 jenkins && \
    adduser --shell /bin/bash \
      --disabled-password --gecos "" \
      --uid 1001 --gid 1002 \
      --home /var/tmp/jenkins jenkins

LABEL source="https://github.com/status-im/status-conan/tree/master/docker" \
      description="Image for building Conan packages." \
      maintainer="pedro@status.im"
