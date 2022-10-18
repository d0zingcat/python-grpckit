# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- TODO Reflection for gRPC option.
- TODO Wrapped client call procedure.
- TODO Consider to wrap non-dict result when using reflection.
- TODO Wrap data into WrapperResponse.
- TODO Compatible to gevent.

## [0.1.4] - 2022-10-18
### Added
- Customized exception handler.
- Allow gRPC threadpool pass through.
- Fully implement `@app.teardown_request` and `@app.teardown_app_context`.

### Changed
- Fix app context leak.

## [0.1.3] - 2022-10-14
### Added
- Wrap gRPC client call procedure in an easy-use way.

## [0.1.2] - 2022-10-13
### Added
- App/Request context management added.
- [Flask](https://flask.palletsprojects.com/en/2.2.x/) like app/request context.
- Local and proxy management for app added, added global `g`/`request`/`current_app`.
- App `teardonw_request` added.
- Debug would reraise exception.
- Thanks to app/request context implementation, the hacking in service to read current_app state could be achieved, now the decorator `@app.armed` could be used without any params, but providing ability to transparently parse request/response.

### Changed
- Move exception handler to outest round.
- Rename `grpckit.wrapper` to `grpckit.client`.
- Rename `grpckit.wrapper.GrpcKitClient` to `grpckit.client.GrpcKitClient`
- Change status_code of common exception from `grpc.StatusCode.UNKNOWN` to `grpc.StatusCode.INTERNAL`

## [0.1.1] - 2022-10-10 ### Added
- Complex route registration `@app.armed` which reads func name as grpc method.
- Transparent convert request and response to Python Dict.
- Global excetion catch logic added.

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
[0.1.3]: https://github.com/d0zingcat/python-grpckit/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/d0zingcat/python-grpckit/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/d0zingcat/python-grpckit/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/d0zingcat/python-grpckit/releases/tag/v0.1.0
