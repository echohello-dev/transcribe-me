# Changelog

## [1.0.1](https://github.com/echohello-dev/transcribe-me/compare/transcribe-me-1.0.0...transcribe-me-1.0.1) (2025-05-25)


### Bug Fixes

* add build-essential to Dockerfile for native dependency compilation ([388eac9](https://github.com/echohello-dev/transcribe-me/commit/388eac92fd912f3654ba279ea433878e3e850b67))
* resolve package publishing issues - Add missing [build-system] section to pyproject.toml - Update setuptools version requirement to &gt;=70.0 - Fix license format to use modern SPDX expression - Add TWINE_USERNAME environment variable to GitHub Actions - Add debugging steps to workflow for better error diagnosis - Make twine check non-blocking in Makefile due to false positive errors - Exclude tests from package distribution ([72a73de](https://github.com/echohello-dev/transcribe-me/commit/72a73de3817b2d32c27a9f1d27a0f52a6096cf7e))

## [1.0.0](https://github.com/echohello-dev/transcribe-me/compare/transcribe-me-0.2.6...transcribe-me-1.0.0) (2025-05-25)


### ⚠ BREAKING CHANGES

* Force 1.0

### Features

* Add command line argument parsing and installation target. ([be7e012](https://github.com/echohello-dev/transcribe-me/commit/be7e012ea0ce9e5dca3a2e129e079e526b68744a))
* Add detailed catalog information using backstage.io/v1alpha1 model ([2723d67](https://github.com/echohello-dev/transcribe-me/commit/2723d6777872697609eb3702e600342ecdeca9f3))
* add fix-release workflow for handling failed releases - Created comprehensive fix-release.yaml workflow with validation and safety checks - Added options to selectively republish package, container, or both - Included dry-run mode for testing without actual publishing - Added checks for existing versions on PyPI and container registry - Fixed PYPI_PASSWORD -&gt; PYPI_TOKEN in manual release workflow - Provides detailed summary of fix operations ([431c91f](https://github.com/echohello-dev/transcribe-me/commit/431c91fd7eb07bf2db0f78b705e40c1b5c9fcfe2))
* Add release-please for automated releases ([#19](https://github.com/echohello-dev/transcribe-me/issues/19)) ([e9cd3d8](https://github.com/echohello-dev/transcribe-me/commit/e9cd3d86e0888bccc4be6d674bcd99739c867f75))
* Add release-please manifest and fix config ([9821a64](https://github.com/echohello-dev/transcribe-me/commit/9821a64a078264dcebd7b9b46d494287fdbfe964))
* Added publish GitHub Action ([2b2a7d6](https://github.com/echohello-dev/transcribe-me/commit/2b2a7d604ba65c8401c91fde8250703ee3e50d51))
* configure automatic package and container publishing on release - Modified release-please workflow to trigger publishing when release is created - Added publish-package and publish-image jobs that run after successful release - Changed existing release.yaml to manual workflow to avoid conflicts - Publishing now happens automatically when release-please PR is merged ([4752f75](https://github.com/echohello-dev/transcribe-me/commit/4752f75af624fe6d1c52b258918a671cbf88ad07))
* configure release-please to force initial version 1.0.0 ([bd4cc4b](https://github.com/echohello-dev/transcribe-me/commit/bd4cc4bc2d731e76996cb63ec1228f44d684ddbd))
* Enhance user experience with colorful output and messaging ([f842ee6](https://github.com/echohello-dev/transcribe-me/commit/f842ee6fc43d64bea82de0590f2754340c50c479))
* Enhance user experience with improved messages ([7bc483a](https://github.com/echohello-dev/transcribe-me/commit/7bc483a6bcfcb91c21618ce23e06a29a28e0109e))
* Force 1.0 ([ffd86b2](https://github.com/echohello-dev/transcribe-me/commit/ffd86b20b9838f087c15556aa7d9e0f2e8d2a9ce))
* Implement timestamped file archiving feature ([c83bd2c](https://github.com/echohello-dev/transcribe-me/commit/c83bd2c40a6c3e22c94e642a7d9081e885f76421))
* Implement transcription and summarization Python script ([bd1ad1b](https://github.com/echohello-dev/transcribe-me/commit/bd1ad1beefb1e94765160c5db0b7ec0de8fff455))
* Improve audio transcription accuracy via new config. ([9413b3d](https://github.com/echohello-dev/transcribe-me/commit/9413b3d171a790b1f7875cf07f50d568587c295b))
* Improve file processing flow in main script ([827d9de](https://github.com/echohello-dev/transcribe-me/commit/827d9de8a7c62394d0a88c8af6ded2bb29852d05))
* Improve reliability with retry logic and exponential backoff ([9c00b0f](https://github.com/echohello-dev/transcribe-me/commit/9c00b0f0ce8fc725cb15bcdf28afe74b7198e376))
* Improve user input and YAML key sorting in main.py ([102a8eb](https://github.com/echohello-dev/transcribe-me/commit/102a8eb0d174e9d0df984355808f5a7be4c3ec61))
* Integrate AssemblyAI for transcription services ([690c376](https://github.com/echohello-dev/transcribe-me/commit/690c376cf2da50f3daeb68e46cc25fbf142a7666))
* Optimize performance by refactoring key components ([d26512e](https://github.com/echohello-dev/transcribe-me/commit/d26512ec26db583c18c321dac9c5130b2f6354c3))
* Refactor `generate_summary` function for platform argument. ([56fb0f2](https://github.com/echohello-dev/transcribe-me/commit/56fb0f2303720abc933f86f510a029976a3c7e64))
* Refactor calculation of max_tokens in main.py ([4244f39](https://github.com/echohello-dev/transcribe-me/commit/4244f3935777c2729afb7da052e4271dcfdf36b2))
* Refactor file handling for audio transcriptions ([eec6cc9](https://github.com/echohello-dev/transcribe-me/commit/eec6cc9d84f9cfc8cc09ce9601bdf674795467a4))
* Refactor file handling in main script ([eafe976](https://github.com/echohello-dev/transcribe-me/commit/eafe976aeb95862f6ab6fd10a246d47da9e530ef))
* Refactor project structure and workflow. ([3abd4b6](https://github.com/echohello-dev/transcribe-me/commit/3abd4b68a3bd40d005094242d6a86e69b16f7873))
* Refactor release process in Makefile ([a33ccb5](https://github.com/echohello-dev/transcribe-me/commit/a33ccb5ed2c8e4a2b281e635f5529b85172e7643))
* Refactor transcription options and key phrase extraction ([96e8c22](https://github.com/echohello-dev/transcribe-me/commit/96e8c22c446992f15750b39b30f8e798728450e6))
* Standardize default paths and config file creation ([4db8972](https://github.com/echohello-dev/transcribe-me/commit/4db8972636a3530fa63402705ddc32be60661478))
* Update `get_changelog` function to include `cz version -p` command ([63de359](https://github.com/echohello-dev/transcribe-me/commit/63de359bb1dc3d2e68322774a9b1cb2e93e8a3f3))
* Update API key instructions and configurations. ([6382e50](https://github.com/echohello-dev/transcribe-me/commit/6382e50e1e89f1bfbaceddc71862d39cc031f6ac))
* Update calculation of max_tokens using model_config value ([94b3aa7](https://github.com/echohello-dev/transcribe-me/commit/94b3aa763df0e2f712d983a243e43951383404e3))
* Update file formats and installation instructions ([522fb84](https://github.com/echohello-dev/transcribe-me/commit/522fb84dd39c48482f1e32aa8622d7e2daee3945))
* Update version handling and validation in transcribe_me module ([a293bcb](https://github.com/echohello-dev/transcribe-me/commit/a293bcb3a2a10ed6ac55fe08e4f227fdd6028330))


### Bug Fixes

* Add additional workflow permissions for GitHub Actions ([b05946e](https://github.com/echohello-dev/transcribe-me/commit/b05946e48b160e5a5c3e7bda53c7dec88f2e1e12))
* Add id-token permission for GitHub Actions workflow ([7350930](https://github.com/echohello-dev/transcribe-me/commit/7350930815f50172351449e01a0f09162b66628f))
* add issues write permission to release-please workflow ([6d224bd](https://github.com/echohello-dev/transcribe-me/commit/6d224bd5ae50fc14d7313602458412347a806acd))
* Ask for confirmation before modifying shell profile files (fixes [#14](https://github.com/echohello-dev/transcribe-me/issues/14)) ([#18](https://github.com/echohello-dev/transcribe-me/issues/18)) ([fa32ccd](https://github.com/echohello-dev/transcribe-me/commit/fa32ccd879e13166968729b52ac4b1732f41067d))
* Dockerfile setup ([bd9f05a](https://github.com/echohello-dev/transcribe-me/commit/bd9f05a7e2ea03afb60a415e61e1f869a179ad3a))
* Dockerfile to reduce vulnerabilities ([#16](https://github.com/echohello-dev/transcribe-me/issues/16)) ([9837a82](https://github.com/echohello-dev/transcribe-me/commit/9837a825196704ce31750adcea4d7456c0916727))
* Dockerfile to reduce vulnerabilities ([#3](https://github.com/echohello-dev/transcribe-me/issues/3)) ([016a874](https://github.com/echohello-dev/transcribe-me/commit/016a8743b0dd5e6cfa2a931f34c23d2cf98a61d6))
* Dockerfile to reduce vulnerabilities ([#7](https://github.com/echohello-dev/transcribe-me/issues/7)) ([d527504](https://github.com/echohello-dev/transcribe-me/commit/d527504ac46696ea822f71f3170435687f49df72))
* Dockerfile to reduce vulnerabilities ([#8](https://github.com/echohello-dev/transcribe-me/issues/8)) ([cc81910](https://github.com/echohello-dev/transcribe-me/commit/cc8191014f3bd3aa80b26fff6e175567edda1b8d))
* Fix conditional for including specific files ([f85925a](https://github.com/echohello-dev/transcribe-me/commit/f85925ac429a19100fce12813c58b5f7f0452704))
* GitHub Actions workflow permissions and Docker publishing ([24c69c8](https://github.com/echohello-dev/transcribe-me/commit/24c69c8195db5b50ac9e0b88fa6ded987a8e0f3d))
* Improve error handling in summarizer module ([3c20e16](https://github.com/echohello-dev/transcribe-me/commit/3c20e16321894ff8bdd303621c567ba0ff8f82b5))
* Refactor Dockerfile setup for improved execution ([c13fa1c](https://github.com/echohello-dev/transcribe-me/commit/c13fa1cf5a81ee25690db004de80366ecf2d3204))
* requirements.txt to reduce vulnerabilities ([#12](https://github.com/echohello-dev/transcribe-me/issues/12)) ([8aab777](https://github.com/echohello-dev/transcribe-me/commit/8aab777829ec918f1b0a94686dcb8fe2eeeb414e))
* requirements.txt to reduce vulnerabilities ([#2](https://github.com/echohello-dev/transcribe-me/issues/2)) ([7c9d6d6](https://github.com/echohello-dev/transcribe-me/commit/7c9d6d6e8313baa743d363b9e9840408e84fbd55))
* requirements.txt to reduce vulnerabilities ([#4](https://github.com/echohello-dev/transcribe-me/issues/4)) ([0d3c0c8](https://github.com/echohello-dev/transcribe-me/commit/0d3c0c8a5554df07cb9321fd4367301f8de77bc9))
* requirements.txt to reduce vulnerabilities ([#5](https://github.com/echohello-dev/transcribe-me/issues/5)) ([3064cc7](https://github.com/echohello-dev/transcribe-me/commit/3064cc7793c08d83a99ce794fac637600a3b7c09))
* requirements.txt to reduce vulnerabilities ([#6](https://github.com/echohello-dev/transcribe-me/issues/6)) ([b9021c0](https://github.com/echohello-dev/transcribe-me/commit/b9021c0dd673820a01d15c81da04e96b6f9f816e))
* requirements.txt to reduce vulnerabilities ([#9](https://github.com/echohello-dev/transcribe-me/issues/9)) ([bc0a264](https://github.com/echohello-dev/transcribe-me/commit/bc0a264ec2f215e59677a9975b5d289956e51ee8))
* Update environment variable name typo and improve file handling ([f939c06](https://github.com/echohello-dev/transcribe-me/commit/f939c067898dbe6fa9c77e5878279bc17459d5e8))
* Use config file for release-please action ([9783b82](https://github.com/echohello-dev/transcribe-me/commit/9783b827d5a6337cc41b268154d5fb5f9e5e1c80))


### Documentation

* Enhance project documentation and cleanup codebase ([fd713f2](https://github.com/echohello-dev/transcribe-me/commit/fd713f2616c72dbd39b2668727f37c4d6e22246c))
* Improve automation and release process with GitHub Actions ([e804bcf](https://github.com/echohello-dev/transcribe-me/commit/e804bcf930ac8a7631a00953652e5e4e7542c11f))
* Improve GitHub release documentation formatting ([1d152ba](https://github.com/echohello-dev/transcribe-me/commit/1d152ba2ac44dce614da4cf071becbcd1fa40a8f))
* Improve GitHub release template and contributor section ([21bfbc8](https://github.com/echohello-dev/transcribe-me/commit/21bfbc823ada3c7f2c1d443faba2e1bacf67ed0c))
* Improve setup instructions in README ([74d5ca3](https://github.com/echohello-dev/transcribe-me/commit/74d5ca327b69aa15f15b0086359f58b9471c94e1))
* Refactor project documentation and installation steps ([4d22d0a](https://github.com/echohello-dev/transcribe-me/commit/4d22d0ad9e9bcca32c112519bd4914878d8a77ae))
* Revamp project documentation and dependencies ([967682d](https://github.com/echohello-dev/transcribe-me/commit/967682d4f754cec1729ecf9ff8ab54bbf5f575de))
* Update application documentation for Docker deployment. ([2704c59](https://github.com/echohello-dev/transcribe-me/commit/2704c599a955a527db327ff8e48e5dc9d50706f5))
* Update application setup instructions and requirements ([ba86710](https://github.com/echohello-dev/transcribe-me/commit/ba8671054117ae5c272ffc647337a41094daf90d))
* Update configuration file naming conventions and references ([238f57c](https://github.com/echohello-dev/transcribe-me/commit/238f57c87074c80889fefd5cda0685427cd1d26f))
* Update installation instructions and Python version for different OSs ([32f4e6b](https://github.com/echohello-dev/transcribe-me/commit/32f4e6b3aef2828c5bfec43647b851e10f263d38))
* Update project documentation ([8d85189](https://github.com/echohello-dev/transcribe-me/commit/8d85189e800ffae0899235e1b1a89a4904f0cef0))
* Update README with macOS testing note ([b36d904](https://github.com/echohello-dev/transcribe-me/commit/b36d904a9aee650146c971e52ff3cecbb4a94162))
* Update README.md with installation and contribution info ([5c9cd08](https://github.com/echohello-dev/transcribe-me/commit/5c9cd089dd89098d8761a630a48df291a7f2047e))

## 0.1.0 (2025-05-24)

### Features

* Initial release with support for OpenAI and AssemblyAI transcription
* Added optional dependencies for providers
* Added dynamic provider imports with proper error handling
* Added comprehensive unit tests
* Added Docker support
