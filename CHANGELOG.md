# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- TODO [Flask](https://flask.palletsprojects.com/en/2.2.x/) like app/request context.
- TODO App `teardonw_request` supported.
- TODO Reflection for gRPC option.
- TODO Wrapped client call procedure.
- TODO Consider to wrap non-dict result when using reflection.
- TODO Wrap data into WrapperResponse.
- TODO Compatible to gevent.

### Changed
- Rename `grpckit.wrapper` to `grpckit.client`.
- rename `grpckit.wrapper.GrpcKitClient` to `grpckit.client.GrpcKitClient`
- Change status_code of common exception from `grpc.StatusCode.UNKNOWN` to `grpc.StatusCode.INTERNAL`

## [0.1.1] - 2022-10-10
### Added
- Complex route registration `@app.armed` which read func name as grpc method.
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
[0.1.1]: https://github.com/d0zingcat/python-grpckit/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/d0zingcat/python-grpckit/releases/tag/v0.1.0
