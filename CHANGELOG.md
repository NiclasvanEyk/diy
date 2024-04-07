# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `RuntimeContainer`s receive a `Specification` object, that maps abstract types to builder functions.
  The container then tries to build types or call functions based on the information contained in its specification.
  To know what to supply for each parameter, the parameters of the constructor or function are reflected using `inspect.signature).
