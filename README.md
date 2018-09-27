# status-conan

This repository serves as the repository for Conan package recipes and configuration.

## Introduction to Conan

> The open source, decentralized and multi-platform
package manager to create and share all your native binaries.

[Conan](https://conan.io/) is an elegant and flexible way to describe, build and manage your whole software toolchain, from compiler, to libraries, to the application.

With it, you are able to declare a given library with certain options, and a consumer can specify the options it needs for its usage. If a library has already been built with those options, it will be present in the cache and will be used. Otherwise, Conan will look in a remote repository. If it still can't find it, it will build the library package, repeating the process for any packages required by the first package

## Status.im remote

The status.im remote lives at https://conan.status.im.