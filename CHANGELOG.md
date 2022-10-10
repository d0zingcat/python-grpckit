# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- [Flask](https://flask.palletsprojects.com/en/2.2.x/) like app/request context.
- App `teardonw_request` supported.
- Reflection for gRPC option.
- Wrapped client call procedure.
- TODO. consider to wrap non-dict result when using reflection


## [0.1.1] - 2022-10-10
### Added
- Complex route registration which read func name as grpc method.
- Transparent convert request and response to Python Dict.
- Exception handle.


### Changed
- Rename `@app.route` to `@app.legacy_route`.

### Removed
- Middleware. 


## [0.1.0] - 2022-09-30
### Added
- A [Mask](https://github.com/Eastwu5788/Mask) like grpckit launched.
- Route registration, configurion, service control and interceptor compatible.
- Auto read and import proto module.



[Unreleased]:
[0.1.0]: 
[0.1.1]:
