# Changelog

## [0.3.0](https://github.com/echohello-dev/transcribe-me/compare/0.2.6...v0.3.0) (2025-05-25)


### Features

* Add release-please for automated releases ([#19](https://github.com/echohello-dev/transcribe-me/issues/19)) ([e9cd3d8](https://github.com/echohello-dev/transcribe-me/commit/e9cd3d86e0888bccc4be6d674bcd99739c867f75))


### Bug Fixes

* Add additional workflow permissions for GitHub Actions ([b05946e](https://github.com/echohello-dev/transcribe-me/commit/b05946e48b160e5a5c3e7bda53c7dec88f2e1e12))
* Add id-token permission for GitHub Actions workflow ([7350930](https://github.com/echohello-dev/transcribe-me/commit/7350930815f50172351449e01a0f09162b66628f))
* Ask for confirmation before modifying shell profile files (fixes [#14](https://github.com/echohello-dev/transcribe-me/issues/14)) ([#18](https://github.com/echohello-dev/transcribe-me/issues/18)) ([fa32ccd](https://github.com/echohello-dev/transcribe-me/commit/fa32ccd879e13166968729b52ac4b1732f41067d))
* Dockerfile to reduce vulnerabilities ([#16](https://github.com/echohello-dev/transcribe-me/issues/16)) ([9837a82](https://github.com/echohello-dev/transcribe-me/commit/9837a825196704ce31750adcea4d7456c0916727))
* GitHub Actions workflow permissions and Docker publishing ([24c69c8](https://github.com/echohello-dev/transcribe-me/commit/24c69c8195db5b50ac9e0b88fa6ded987a8e0f3d))
* requirements.txt to reduce vulnerabilities ([#12](https://github.com/echohello-dev/transcribe-me/issues/12)) ([8aab777](https://github.com/echohello-dev/transcribe-me/commit/8aab777829ec918f1b0a94686dcb8fe2eeeb414e))

## 0.1.0 (2025-05-24)

### Features

* Initial release with support for OpenAI and AssemblyAI transcription
* Added optional dependencies for providers
* Added dynamic provider imports with proper error handling
* Added comprehensive unit tests
* Added Docker support
