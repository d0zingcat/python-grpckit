# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- TODO Reflection for gRPC option.
- TODO app logger.
- TODO Wrapped client call procedure.
- TODO Consider to wrap non-dict result when using reflection.
- TODO Wrap data into WrapperResponse.
- TODO Compatible to gevent.
- TODO remaked cli.
- TODO parser or hook to pre pre-process params.
- TODO client legacy method wrapper which supports native grpc call procedure
- TODO client init with timeout param.
- TODO prometheus monitoring.
- TODO rich status code.
- TODO Allow options control when instantiate a new `GrpcKitClient`.

## [0.1.8] - 2022-10-24
### Added
- Sentry integrated.
- Prometheus integrated.
- Builtin logger.

## [0.1.7] - 2022-10-21
### Added
- Allow timeout control when instantiate a new `GrpcKitClient`.

### Changed
- Fix Interceptor typo.
- Fix App Config load.
- GrpckitClient return dict directly, would not catch RpcError.

## [0.1.6] - 2022-10-20
### Added
- Wrap client response to `GrpcKitResponse`, giving caller the experience to control the data in which way they like.
- Server return no longer need `return dict(foo=bar)`, returning `key, value` tuple instead is also supported.
- Add `msg=` for customized exceptions `__init__` as alias for `message=`.

### Changed
- Client call no longer need `request=dict()`, use kwargs directly and wrap all the process args in `_args=dict()`.

## [0.1.5] - 2022-10-19
### Added
- Decorator `@service.armed` will wrap original dict to WrappedDict which supports `__getattr__`.
- Enhance `@service.route` to a brand new decorator which inherit from `@service.armed`, providing ability to register a router, parse request/response like a native function, and it's the complete version and final edition for route registeration.

### Changed
- Rename _global.py to globals.py.
- Rename `@service.armed` to `@service.route_reduced`.

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
- Thanks to app/request context implementation, the hacking in service to read current_app state could be achieved, now the decorator `@service.armed` could be used without any params, but providing ability to transparently parse request/response.

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
- Rename `@service.route` to `@service.legacy_route`.

### Removed
- Middleware. 

## [0.1.0] - 2022-09-30
### Added
- A [Mask](https://github.com/Eastwu5788/Mask) like grpckit launched.
- Route registration, configurion, service control and interceptor compatible.
- Auto read and import proto module.

[Unreleased]:
[0.1.8]: https://github.com/d0zingcat/python-grpckit/compare/v0.1.7...v0.1.8
[0.1.7]: https://github.com/d0zingcat/python-grpckit/compare/v0.1.6...v0.1.7
[0.1.6]: https://github.com/d0zingcat/python-grpckit/compare/v0.1.5...v0.1.6
[0.1.5]: https://github.com/d0zingcat/python-grpckit/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/d0zingcat/python-grpckit/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/d0zingcat/python-grpckit/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/d0zingcat/python-grpckit/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/d0zingcat/python-grpckit/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/d0zingcat/python-grpckit/releases/tag/v0.1.0
