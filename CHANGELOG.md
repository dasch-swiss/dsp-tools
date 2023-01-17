# Changelog

## [2.0.1](https://github.com/dasch-swiss/dsp-tools/compare/v2.0.0...v2.0.1) (2023-01-17)


### Maintenance

* bump versions of start-stack, use dynamic project IRI in get command (DEV-1613) ([#282](https://github.com/dasch-swiss/dsp-tools/issues/282)) ([2ecf4f5](https://github.com/dasch-swiss/dsp-tools/commit/2ecf4f5c7ae7269f36bace5b6786975bb7088681))
* refactor project creation (DEV-1165) ([#280](https://github.com/dasch-swiss/dsp-tools/issues/280)) ([5e662a6]
  (https://github.com/dasch-swiss/dsp-tools/commit/5e662a6f59aeb6b6e84e4f56fd5f700eb12e93cb))
* use start-stack command for e2e tests, replace Makefile by poetry-exec-plugin (DEV-1597) ([#279](https://github.com/dasch-swiss/dsp-tools/issues/279)) ([6b85d15](https://github.com/dasch-swiss/dsp-tools/commit/6b85d15660da052e374814414dd20bae6880f68a))

## [2.0.0](https://github.com/dasch-swiss/dsp-tools/compare/v1.22.2...v2.0.0) (2023-01-09)


### ⚠ BREAKING CHANGES

* switch to src layout, use poetry, add developer docs (DEV-1523) ([#276](https://github.com/dasch-swiss/dsp-tools/issues/276))

### Maintenance

* adapt schema URLs, adapt title of release-please PR (DEV-1596) ([#278](https://github.com/dasch-swiss/dsp-tools/issues/278)) ([67f6475](https://github.com/dasch-swiss/dsp-tools/commit/67f6475e0059debe40f099d44d8fcfd3fd348b20))
* switch to src layout, use poetry, add developer docs (DEV-1523) ([#276](https://github.com/dasch-swiss/dsp-tools/issues/276)) ([6ae3b4f](https://github.com/dasch-swiss/dsp-tools/commit/6ae3b4fff7a050f3a3af9a2c38eab1d5d5dbb889))

### [1.22.2](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.22.1...v1.22.2) (2022-12-21)


### Bug Fixes

* **start-stack:** copy docker folder to user's home directory (DEV-1581) ([#274](https://www.github.com/dasch-swiss/dsp-tools/issues/274)) ([b0ebfc5](https://www.github.com/dasch-swiss/dsp-tools/commit/b0ebfc5a5861e22b79e1f8542497c1f52141201d))

### [1.22.1](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.22.0...v1.22.1) (2022-12-20)


### Bug Fixes

* **start-stack:** use TTL files from DSP-API v24.0.8 (DEV-1580) ([#273](https://www.github.com/dasch-swiss/dsp-tools/issues/273)) ([3ad96ba](https://www.github.com/dasch-swiss/dsp-tools/commit/3ad96ba2b7d833faeeea97548818d51a1d7902b0))


### Documentation

* improve documentation of DSP permission system (DEV-1561) ([#270](https://www.github.com/dasch-swiss/dsp-tools/issues/270)) ([33ab59d](https://www.github.com/dasch-swiss/dsp-tools/commit/33ab59d74134e61de9ce04053218cfa4e5938e48))

## [1.22.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.21.0...v1.22.0) (2022-12-19)


### Bug Fixes

* **excel2xml:** better standard permissions (permissions definitions at top of XML file) (DEV-1560) ([#268](https://www.github.com/dasch-swiss/dsp-tools/issues/268)) ([b0d30be](https://www.github.com/dasch-swiss/dsp-tools/commit/b0d30be9b2f5efe4f54c0a3ed6b7f6fdffff88a2))
* **xmlupload:** improve URL recognition (DEV-1557) ([#266](https://www.github.com/dasch-swiss/dsp-tools/issues/266)) ([60f8fe5](https://www.github.com/dasch-swiss/dsp-tools/commit/60f8fe5e3da898138d748bb7b3398b233b4c0e25))
* **xmlupload:** prevent crash + improve error message when cardinalities are wrong (DEV-1559) [#267](https://www.github.com/dasch-swiss/dsp-tools/issues/267) ([7bfd82f](https://www.github.com/dasch-swiss/dsp-tools/commit/7bfd82f98a49943442ab693c5d2aa5ed924bf210))


### Documentation

* **excel2json:** use rosetta as example data (DEV-1478) ([#254](https://www.github.com/dasch-swiss/dsp-tools/issues/254)) ([af192cb](https://www.github.com/dasch-swiss/dsp-tools/commit/af192cb45d7de44f66a53b4e3a5240bc47c7e61f))
* **readme:** explain handling of git submodules (DEV-1502) ([#256](https://www.github.com/dasch-swiss/dsp-tools/issues/256)) ([1dc8483](https://www.github.com/dasch-swiss/dsp-tools/commit/1dc84836adf68aaf1741dd50da05fb05b1230a06))
* text values: describe which combinations of gui_element and encoding are desirable (DEV-1521) ([#259](https://www.github.com/dasch-swiss/dsp-tools/issues/259)) ([21967c6](https://www.github.com/dasch-swiss/dsp-tools/commit/21967c67fbe6837b7bb77d8f0dfc4870272bcbf5))


### Enhancements

* use docker commands for stack handling (DEV-1530) ([#261](https://www.github.com/dasch-swiss/dsp-tools/issues/261)) ([c11edc5](https://www.github.com/dasch-swiss/dsp-tools/commit/c11edc5ddda72514b75776f8f14d1645e7bd38cd))


### Maintenance

* bump versions of GitHub actions (DEV-1532) [#263](https://www.github.com/dasch-swiss/dsp-tools/issues/263) ([efc9f51](https://www.github.com/dasch-swiss/dsp-tools/commit/efc9f514d0efd1bd33046d0cbf87e3cc9fdd7712))
* fix regex for PR title (DEV-1504) ([#257](https://www.github.com/dasch-swiss/dsp-tools/issues/257)) ([d4feb68](https://www.github.com/dasch-swiss/dsp-tools/commit/d4feb68963f4c5ff624bff05501f2a1b3a18bf87))
* **start-api:** adjust version numbers of DSP-API and DSP-APP according to 2022.11.01 (DEV-1579) [#271](https://www.github.com/dasch-swiss/dsp-tools/issues/271) ([10dcd2f](https://www.github.com/dasch-swiss/dsp-tools/commit/10dcd2f966063c0f2b7125a0061b50bcb4c75de3))
* **xmlupload:** add metrics flag (DEV-1512) ([#264](https://www.github.com/dasch-swiss/dsp-tools/issues/264)) ([f4822dc](https://www.github.com/dasch-swiss/dsp-tools/commit/f4822dc2ccd87d24c3ce787aef2b22f230bca184))
* **xmlupload:** handling of upload errors (DEV-1505) ([#250](https://www.github.com/dasch-swiss/dsp-tools/issues/250)) ([1507b21](https://www.github.com/dasch-swiss/dsp-tools/commit/1507b21834c83be52ab7a6810e0c773e493c5500))



## [1.21.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.20.0...v1.21.0) (2022-11-11)


### Bug Fixes

* bugs in json schema (DEV-1142) ([#252](https://www.github.com/dasch-swiss/dsp-tools/issues/252)) ([92af830](https://www.github.com/dasch-swiss/dsp-tools/commit/92af83084d82f0083714f4bfcf5f39f03e5b0077))
* **excel2xml:** prevent writing empty text-prop, make text-prop validation less restrictive (DEV-1440) [#243](https://www.github.com/dasch-swiss/dsp-tools/issues/243) ([ae777e4](https://www.github.com/dasch-swiss/dsp-tools/commit/ae777e48ee527457031a5c23f9605e92bfd8a992))


### Enhancements

* add command excel2json to create JSON project file from folder with Excel files (DEV-960) ([#248](https://www.github.com/dasch-swiss/dsp-tools/issues/248)) ([e8e05e4](https://www.github.com/dasch-swiss/dsp-tools/commit/e8e05e4d7fcbf8830ae5ef71c3c148fc13c01485))
* startup API and APP with dsp-tools (DEV-126) ([#246](https://www.github.com/dasch-swiss/dsp-tools/issues/246)) ([de182dc](https://www.github.com/dasch-swiss/dsp-tools/commit/de182dcdce0217635fd74320da1800ce71c47a9f))


### Documentation

* improve docs (DEV-1478) ([#249](https://www.github.com/dasch-swiss/dsp-tools/issues/249)) ([7947dec](https://www.github.com/dasch-swiss/dsp-tools/commit/7947dec863d46ee2a07622f116948e21e24346c4))



## [1.20.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.19.0...v1.20.0) (2022-10-18)


### Maintenance

* **xmlupload:** improve error message when syntax for referencing ontos is wrong (DEV-1399) ([#237](https://www.github.com/dasch-swiss/dsp-tools/issues/237)) ([df0bf33](https://www.github.com/dasch-swiss/dsp-tools/commit/df0bf33588ebae38d09756c73198d33a9ebaf867))


### Documentation

* user needs to be project member to become project admin (DEV-1383) ([#241](https://www.github.com/dasch-swiss/dsp-tools/issues/241)) ([1a13c02](https://www.github.com/dasch-swiss/dsp-tools/commit/1a13c02f05c74bf3642632a96828047ca8750fc4))
* **xmlupload:** improve examples, add documentation of geometry-prop JSON format ([#240](https://www.github.com/dasch-swiss/dsp-tools/issues/240)) ([7df1d86](https://www.github.com/dasch-swiss/dsp-tools/commit/7df1d867c5fe0c1ee634f06b237876988ffdbd1d))


### Enhancements

* **xmlupload:** enable migration of resource creation date (DEV-1402) ([#238](https://www.github.com/dasch-swiss/dsp-tools/issues/238)) ([83dd2de](https://www.github.com/dasch-swiss/dsp-tools/commit/83dd2de91a3b8a81db68da681d669fdd60651393))

## [1.19.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.18.0...v1.19.0) (2022-10-07)


### Bug Fixes

* fix command `dsp-tools xmlupload --validate` (DEV-1360) ([#230](https://www.github.com/dasch-swiss/dsp-tools/issues/230)) ([0b2bd40](https://www.github.com/dasch-swiss/dsp-tools/commit/0b2bd4037c224bd90147ea5fdfada379578eb369))


### Enhancements

* address feedback to `excel2xml`: remove param `values` in all `make_*_prop()` methods, and fix some bugs (DEV-1361) ([#232](https://www.github.com/dasch-swiss/dsp-tools/issues/232)) ([a7e9d85](https://www.github.com/dasch-swiss/dsp-tools/commit/a7e9d8544799efef45d33f6e4072ba7ea066eb4b))
* change input format of `excel` command: use 1 Excel file for all same-language lists, rename command to `excel2lists` (DEV-955) ([#228](https://www.github.com/dasch-swiss/dsp-tools/issues/228)) ([21cc6bc](https://www.github.com/dasch-swiss/dsp-tools/commit/21cc6bcbdac991742d86932a2a74c4a4267d67b6))


### Documentation

* improve docs and example data for excel2xml: create repo [0123-import-scripts](https://github.com/dasch-swiss/0123-import-scripts) (DEV-1370) ([#233](https://www.github.com/dasch-swiss/dsp-tools/issues/233)) ([9c6827e](https://www.github.com/dasch-swiss/dsp-tools/commit/9c6827ec2e89ebf94703188f1b81bd440d70c5da))


### Maintenance

* bump versions (DEV-1117) [#235](https://www.github.com/dasch-swiss/dsp-tools/issues/235) ([fc9c03c](https://www.github.com/dasch-swiss/dsp-tools/commit/fc9c03c58c09629ccd7d6ad0504e74614cac1075))
* fix release-please (DEV-1396) [#234](https://www.github.com/dasch-swiss/dsp-tools/issues/234) ([3bd92d8](https://www.github.com/dasch-swiss/dsp-tools/commit/3bd92d8d61c46ed23a3dca25e9914938750f1ff9))
* reduce GitHub workflow frequency (DEV-1344) [#227](https://www.github.com/dasch-swiss/dsp-tools/issues/227) ([a0722d8](https://www.github.com/dasch-swiss/dsp-tools/commit/a0722d8d2b601ab12154c327ecb3a743362044ea))
* **tests:** enforce JKD 17 (DEV-1366) ([#231](https://www.github.com/dasch-swiss/dsp-tools/issues/231)) ([1036acd](https://www.github.com/dasch-swiss/dsp-tools/commit/1036acd2c71bb6f5ed24086fcff4d091a5853e2e))
* tidy up excel2lists, excel2resources, excel2properties (DEV-1352) ([#229](https://www.github.com/dasch-swiss/dsp-tools/issues/229)) ([d2c2e08](https://www.github.com/dasch-swiss/dsp-tools/commit/d2c2e085813680007a5228c1ef5bab82b4f1a6c7))

## [1.18.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.17.1...v1.18.0) (2022-09-09)


### Enhancements

* add module csv2xml to convert tabular data to DSP-XML (DEV-134) ([#219](https://www.github.com/dasch-swiss/dsp-tools/issues/219)) ([19393aa](https://www.github.com/dasch-swiss/dsp-tools/commit/19393aa8035864755ba81a2d36bfcb0dec96c569))


### Maintenance

* tidy up makefile (DEV-1166) ([#223](https://www.github.com/dasch-swiss/dsp-tools/issues/223)) ([dca0854](https://www.github.com/dasch-swiss/dsp-tools/commit/dca085404c5a8c4ae85936dbabd4d95f4c0b1a77))


### Documentation

* clarify docs of onto creation (DEV-1164) ([#225](https://www.github.com/dasch-swiss/dsp-tools/issues/225)) ([f64d2cf](https://www.github.com/dasch-swiss/dsp-tools/commit/f64d2cf6d76adc90283920faebd9aa412756418e))

### [1.17.1](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.17.0...v1.17.1) (2022-08-22)


### Bug Fixes

* bugs in xmlupload and resource.py (DEV-1140) [#217](https://www.github.com/dasch-swiss/dsp-tools/issues/217) ([5e402e4](https://www.github.com/dasch-swiss/dsp-tools/commit/5e402e4dbe931641cc9fab080d92688c4cb9d589))
* PyPI deployment (DEV-1270) ([#220](https://www.github.com/dasch-swiss/dsp-tools/issues/220)) ([dafaa7e](https://www.github.com/dasch-swiss/dsp-tools/commit/dafaa7e30908aeeca4312cd0a99e7c8281cce723))

## [1.17.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.16.0...v1.17.0) (2022-08-16)


### Bug Fixes

* catch network interruptions during onto creation (DEV-1073) ([#210](https://www.github.com/dasch-swiss/dsp-tools/issues/210)) ([ab0e3b2](https://www.github.com/dasch-swiss/dsp-tools/commit/ab0e3b26936e53df49a3fa67e3564b7c16f168e0))


### Maintenance

* stop serving docs to dasch-swiss.github.io (DEV-826) ([#211](https://www.github.com/dasch-swiss/dsp-tools/issues/211)) ([f2d25f9](https://www.github.com/dasch-swiss/dsp-tools/commit/f2d25f9d0276a46c75754e06083e5e108a6116e8))


### Documentation

* add links from usage subpage to other subpages (DEV-812) ([#208](https://www.github.com/dasch-swiss/dsp-tools/issues/208)) ([92ac678](https://www.github.com/dasch-swiss/dsp-tools/commit/92ac678c824393838cb376054ba74b0b70781dc8))
* fix outdated links (DEV-1194) [#215](https://www.github.com/dasch-swiss/dsp-tools/issues/215) ([6849737](https://www.github.com/dasch-swiss/dsp-tools/commit/68497377f90ff28b350ff9bd474b9455702c7f0a))
* sort entries alphabetically (DEV-1184) ([#212](https://www.github.com/dasch-swiss/dsp-tools/issues/212)) ([75c6ae5](https://www.github.com/dasch-swiss/dsp-tools/commit/75c6ae5915de7432d7bb768f14a9ff9bdec9dfb2))


### Enhancements

* add isSequenceOf (DEV-746) ([#214](https://www.github.com/dasch-swiss/dsp-tools/issues/214)) ([991d424](https://www.github.com/dasch-swiss/dsp-tools/commit/991d4245fbd23a0b88b706b7e1e89859a5692d7a))

## [1.16.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.15.1...v1.16.0) (2022-07-18)


### Enhancements

* **xmlupload:** implement <annotation>, <region>, and <link> tags (DEV-855) ([#204](https://www.github.com/dasch-swiss/dsp-tools/issues/204)) ([5044a9e](https://www.github.com/dasch-swiss/dsp-tools/commit/5044a9ec5a238b250b74355da915e1bef5216cd4))

### [1.15.1](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.15.0...v1.15.1) (2022-06-23)


### Bug Fixes

* **excel2resources, excel2properties:** cover all cases (DEV-1040) ([#201](https://www.github.com/dasch-swiss/dsp-tools/issues/201)) ([4c6ed19](https://www.github.com/dasch-swiss/dsp-tools/commit/4c6ed19a8046671e0f9eefb31a4e4e6a82934f0a))
* xmlupload crashes without writing id2iri mapping (DEV-813) ([#194](https://www.github.com/dasch-swiss/dsp-tools/issues/194)) ([7948e75](https://www.github.com/dasch-swiss/dsp-tools/commit/7948e7546bb7e275980bb42b4d3dec3875d9279e))


### Maintenance

* unpin dependency versions (DEV-983) ([#200](https://www.github.com/dasch-swiss/dsp-tools/issues/200)) ([5c56601](https://www.github.com/dasch-swiss/dsp-tools/commit/5c566018af03aae85dd924a6ab0690674f888fac))
* **xmlupload:** refactor xmlupload, add unittest (DEV-1043) ([#203](https://www.github.com/dasch-swiss/dsp-tools/issues/203)) ([fcf8384](https://www.github.com/dasch-swiss/dsp-tools/commit/fcf838482822223569fd08428c53b5a7464232b3))

## [1.15.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.14.0...v1.15.0) (2022-06-02)


### Bug Fixes

* **onto validation:** correctly identify circular dependencies (DEV-769) ([#192](https://www.github.com/dasch-swiss/dsp-tools/issues/192)) ([ed35902](https://www.github.com/dasch-swiss/dsp-tools/commit/ed35902136759d17b47ebaaefd06a476fb6781f0))
* **testdata:** remove salsah-links from test-id2iri-data.xml (DEV-975) ([#199](https://www.github.com/dasch-swiss/dsp-tools/issues/199)) ([7548501](https://www.github.com/dasch-swiss/dsp-tools/commit/7548501426edb3845e513e9916533bb21f74ea17))
* **xmlupload:** prevent crash with incremental option (DEV-811) ([#197](https://www.github.com/dasch-swiss/dsp-tools/issues/197)) ([cccb5e8](https://www.github.com/dasch-swiss/dsp-tools/commit/cccb5e8698eb529f22b8260a2b011e8ed30b171c))


### Enhancements

* add romansh (DEV-867) ([#193](https://www.github.com/dasch-swiss/dsp-tools/issues/193)) ([86d3e6a](https://www.github.com/dasch-swiss/dsp-tools/commit/86d3e6a9810fe8827f06aa2ab5ba6bc3b139287a))


### Documentation

* **xmlupload:** better explanation of permissions (DEV-969) ([#196](https://www.github.com/dasch-swiss/dsp-tools/issues/196)) ([d3efde8](https://www.github.com/dasch-swiss/dsp-tools/commit/d3efde84aecea52ba4bcd08ad2551858a2395944))

## [1.14.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.13.0...v1.14.0) (2022-05-03)


### Enhancements

* **xmlupload:** support Baseclass MovingImageRepresentation ([#185](https://www.github.com/dasch-swiss/dsp-tools/issues/185)) ([7ebf588](https://www.github.com/dasch-swiss/dsp-tools/commit/7ebf588edd9d76d05e242a3add3fe735fac7f460))


### Documentation

* fix typos in documentation (DEV-849) ([#189](https://www.github.com/dasch-swiss/dsp-tools/issues/189)) ([f887edd](https://www.github.com/dasch-swiss/dsp-tools/commit/f887edd53c04cd615db755a91633aa756f46c6b6))


### Maintenance

* **json-schema:** change JSON schema version to draft-07 (DEV-848) ([#188](https://www.github.com/dasch-swiss/dsp-tools/issues/188)) ([8ca6f87](https://www.github.com/dasch-swiss/dsp-tools/commit/8ca6f8783599b68ddf0f4ca70d8869a8480c81f7))
* update lists.json (DEV-851) ([#190](https://www.github.com/dasch-swiss/dsp-tools/issues/190)) ([e0254be](https://www.github.com/dasch-swiss/dsp-tools/commit/e0254be372e90b2d0813128db34b1561f99405b2))
* update schema-files (DEV-449) ([#187](https://www.github.com/dasch-swiss/dsp-tools/issues/187)) ([9a5a50b](https://www.github.com/dasch-swiss/dsp-tools/commit/9a5a50b18f362f731c44bd31e8a056337be5a7df))

## [1.13.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.12.2...v1.13.0) (2022-04-25)


### Bug Fixes

* **get:** handle slash at end of server, improve docs (DEV-734) ([17c0a40](https://www.github.com/dasch-swiss/dsp-tools/commit/17c0a40ec918f20c7fea760aefa002a4dae4ce1e))
* **groups:** dsp-tools should not allow group creation if group name already in use (DEV-798) ([#183](https://www.github.com/dasch-swiss/dsp-tools/issues/183)) ([8f168ca](https://www.github.com/dasch-swiss/dsp-tools/commit/8f168cad4ac7399c18823a97d8471dad9af1417b))


### Enhancements

* add support for external ontologies (dev-512) ([#170](https://www.github.com/dasch-swiss/dsp-tools/issues/170)) ([ff36bc1](https://www.github.com/dasch-swiss/dsp-tools/commit/ff36bc164768e069281c637f3f4b479fa1bdac3c))
* **get:** get more infos from user (DEV-641) ([#181](https://www.github.com/dasch-swiss/dsp-tools/issues/181)) ([407f5c5](https://www.github.com/dasch-swiss/dsp-tools/commit/407f5c55229480bf372b874ffaac0b1b4e26e2d7))


### Maintenance

* bump dependencies (DEV-815) ([#184](https://www.github.com/dasch-swiss/dsp-tools/issues/184)) ([5d2d109](https://www.github.com/dasch-swiss/dsp-tools/commit/5d2d1096db383da9eaa7f9f50625377f9619dc83))
* change to pipenv (DEV-764) ([#177](https://www.github.com/dasch-swiss/dsp-tools/issues/177)) ([6c44688](https://www.github.com/dasch-swiss/dsp-tools/commit/6c44688841f9374c307ad4fb7aa94c2b4de7d3ad))
* improve XML and JSON Schemas (DEV-449) ([#180](https://www.github.com/dasch-swiss/dsp-tools/issues/180)) ([2c17b9d](https://www.github.com/dasch-swiss/dsp-tools/commit/2c17b9d82af92430fb109b8be685a865e0525d6a))

### [1.12.2](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.12.1...v1.12.2) (2022-03-31)


### Bug Fixes

* add missing dependency (DEV-763) ([1cda29e](https://www.github.com/dasch-swiss/dsp-tools/commit/1cda29ec34626d5806b9ad2d180c75956f93bbcd))

### [1.12.1](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.12.0...v1.12.1) (2022-03-31)


### Maintenance

* remove bazel (DEV-735) ([#172](https://www.github.com/dasch-swiss/dsp-tools/issues/172)) ([e12e9dd](https://www.github.com/dasch-swiss/dsp-tools/commit/e12e9dd3edb19b4b05f93605b55d4bbd50ffc9fc))

## [1.12.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.11.0...v1.12.0) (2022-03-25)


### Bug Fixes

* **onto creation:** prevent sorting algorith from modifying original ontology ([#169](https://www.github.com/dasch-swiss/dsp-tools/issues/169)) ([9a9e5f0](https://www.github.com/dasch-swiss/dsp-tools/commit/9a9e5f0cb2aaac1e6510aafd2aff0ed2c1a4eab9))


### Enhancements

* **onto creation:** allow that resources and properties are not sorted by inheritance (DEV-626) ([#167](https://www.github.com/dasch-swiss/dsp-tools/issues/167)) ([2ebece3](https://www.github.com/dasch-swiss/dsp-tools/commit/2ebece39311a3d816bc136e521692c6cc327a68c))
* **xmlupload:** allow circular references (DEV-577) ([#165](https://www.github.com/dasch-swiss/dsp-tools/issues/165)) ([75a444f](https://www.github.com/dasch-swiss/dsp-tools/commit/75a444ff5ef586238139ac2f091876b22ef2a671))

## [1.11.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.10.1...v1.11.0) (2022-02-28)


### Enhancements

* improve prefix handling in json ontos (DEV-572) ([#164](https://www.github.com/dasch-swiss/dsp-tools/issues/164)) ([8610885](https://www.github.com/dasch-swiss/dsp-tools/commit/86108851c74c1751a8604fb942b05e967f9075f7))

### [1.10.1](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.10.0...v1.10.1) (2022-02-23)


### Documentation

* add explanation how an Excel file for list creation must be structured (DEV-533) ([#159](https://www.github.com/dasch-swiss/dsp-tools/issues/159)) ([660d57b](https://www.github.com/dasch-swiss/dsp-tools/commit/660d57b52f8f2e1e570fe9b9e8d298f193748248))
* explain the interval-prop more precisely ([#162](https://www.github.com/dasch-swiss/dsp-tools/issues/162)) ([00c18dc](https://www.github.com/dasch-swiss/dsp-tools/commit/00c18dc01d0a8cb9987d8adb6f74694dbfde3211))

## [1.10.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.9.0...v1.10.0) (2022-02-21)


### Documentation

* add validate argparse info to xmlupload ([#156](https://www.github.com/dasch-swiss/dsp-tools/issues/156)) ([08ddebd](https://www.github.com/dasch-swiss/dsp-tools/commit/08ddebd0ba67b0211394d04a5ebf93c16da5ea20))
* improve docs (DEV-450) ([#152](https://www.github.com/dasch-swiss/dsp-tools/issues/152)) ([be5b69f](https://www.github.com/dasch-swiss/dsp-tools/commit/be5b69f41cea50a37c0ff840830232ebe65cf041))


### Maintenance

* excel to json list (DEV-431) ([#155](https://www.github.com/dasch-swiss/dsp-tools/issues/155)) ([8a8c9d0](https://www.github.com/dasch-swiss/dsp-tools/commit/8a8c9d02fe3a4c47523bb70bbaa754ece5c007cd))
* **xml-upload:** print XML validation errors when xmlupload fails due to validation (DEV-387) ([#149](https://www.github.com/dasch-swiss/dsp-tools/issues/149)) ([03554c2](https://www.github.com/dasch-swiss/dsp-tools/commit/03554c2d2ae666f2af694ba13a3b88c6be8e2409))


### Enhancements

* improve json schema validation error output (DEV-456) ([#153](https://www.github.com/dasch-swiss/dsp-tools/issues/153)) ([9f92b66](https://www.github.com/dasch-swiss/dsp-tools/commit/9f92b66f9ea9fb41450c0d177c2bfe31c6c79601))
* make comments optional for new properties and resources (DEV-502) ([#158](https://www.github.com/dasch-swiss/dsp-tools/issues/158)) ([9c30746](https://www.github.com/dasch-swiss/dsp-tools/commit/9c307464230d381c9e14ab9e587e7dff0508bd32))
* **ontology:** add Representation (DEV-551) ([#160](https://www.github.com/dasch-swiss/dsp-tools/issues/160)) ([cba7be0](https://www.github.com/dasch-swiss/dsp-tools/commit/cba7be072b4f96cc80f38f871e6253b3864e60d7))

## [1.9.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.8.1...v1.9.0) (2022-01-27)


### Documentation

* add isPartOf and seqnum properties to documentation (DEV-216) ([#145](https://www.github.com/dasch-swiss/dsp-tools/issues/145)) ([09d42a4](https://www.github.com/dasch-swiss/dsp-tools/commit/09d42a4525a91fb07a3437566c2b30ecef43de21))
* **dsp-tools-excel:** mention the GUI order and other small improvements (DEV-99) ([#148](https://www.github.com/dasch-swiss/dsp-tools/issues/148)) ([853068d](https://www.github.com/dasch-swiss/dsp-tools/commit/853068db3aee3012d6d009c87773a45cd69b6bde))


### Enhancements

* **xmlupload:** use custom IRIs created from salsah ARKs for XML upload (DEV-179) ([#147](https://www.github.com/dasch-swiss/dsp-tools/issues/147)) ([873324a](https://www.github.com/dasch-swiss/dsp-tools/commit/873324ad4cd4fefd48d8d2fc37f08774285849d5))

## [1.8.1](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.8.0...v1.8.1) (2022-01-11)


### Bug Fixes

* problem with reference to list values (DEV-356) ([#143](https://www.github.com/dasch-swiss/dsp-tools/issues/143)) ([3fce99a](https://www.github.com/dasch-swiss/dsp-tools/commit/3fce99a0d4236a8dcaa21785c3f3deba286725da))


### Maintenance

* **deps:** bump nltk from 3.6.5 to 3.6.6 ([#142](https://www.github.com/dasch-swiss/dsp-tools/issues/142)) ([4f91098](https://www.github.com/dasch-swiss/dsp-tools/commit/4f9109886a4a2ec828819f449249c6e56cf4adac))

## [1.8.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.7.1...v1.8.0) (2022-01-10)


### Bug Fixes

* **ontology:** add default values for missing comments (DEV-337) ([#141](https://www.github.com/dasch-swiss/dsp-tools/issues/141)) ([6f0094e](https://www.github.com/dasch-swiss/dsp-tools/commit/6f0094e9a91ba03ffd7bee84e50e4aa93820ab6f))
* print only unresolvable resptrs ([#139](https://www.github.com/dasch-swiss/dsp-tools/issues/139)) ([cbe1876](https://www.github.com/dasch-swiss/dsp-tools/commit/cbe1876f8c4ab1a8ac850a095560c34a380cfbc3))
* restrict the creation of classes without cardinalities (DEV-305) ([#136](https://www.github.com/dasch-swiss/dsp-tools/issues/136)) ([5604a5b](https://www.github.com/dasch-swiss/dsp-tools/commit/5604a5be2e4be6094d73c8d782699c4beab59a37))


### Enhancements

* **excel-to-json:** allow comments in class and property definitions ([#111](https://www.github.com/dasch-swiss/dsp-tools/issues/111)) ([807959f](https://www.github.com/dasch-swiss/dsp-tools/commit/807959fa3ec58ed5504f87c19905e5e666b2dc6e))
* **get:** extend get command to get more information (DEV-139) ([#137](https://www.github.com/dasch-swiss/dsp-tools/issues/137)) ([9ce6722](https://www.github.com/dasch-swiss/dsp-tools/commit/9ce6722a8df29bbbaaaa845d793d5306106aebc8))


### Maintenance

* improve ontology schema and extend tests (DEV-313) ([#140](https://www.github.com/dasch-swiss/dsp-tools/issues/140)) ([656ccff](https://www.github.com/dasch-swiss/dsp-tools/commit/656ccff0ff553b13b19242c9997220600e53a76f))

## [1.7.1](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.7.0...v1.7.1) (2021-12-14)


### Bug Fixes

* **groups:** make groups optional (DEV-138) ([#135](https://www.github.com/dasch-swiss/dsp-tools/issues/135)) ([6aa1aa7](https://www.github.com/dasch-swiss/dsp-tools/commit/6aa1aa78a81dc22d7c04ed17a705458f727dcc07))


### Maintenance

* **deps:** bump lxml from 4.6.4 to 4.6.5 ([#133](https://www.github.com/dasch-swiss/dsp-tools/issues/133)) ([605dc2f](https://www.github.com/dasch-swiss/dsp-tools/commit/605dc2fe7ddce5f18b5846a5fd12fdfe66fb9040))

## [1.7.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.6.1...v1.7.0) (2021-12-07)


### Bug Fixes

* **boolean-values:** allow 0 and 1 as boolean values (DEV-251) ([#131](https://www.github.com/dasch-swiss/dsp-tools/issues/131)) ([fd58ad4](https://www.github.com/dasch-swiss/dsp-tools/commit/fd58ad45b71163ecece1b86c5a1f88932196fc76))
* **create-ontology:** within an ontology, references to the ontology itself are not possible (DEV-135) ([#130](https://www.github.com/dasch-swiss/dsp-tools/issues/130)) ([6a40fc6](https://www.github.com/dasch-swiss/dsp-tools/commit/6a40fc6f291b3cf3fbb3a1c6af2c61cbef49d19c))
* **permissions:** use permissions in xml upload (DEV-178) ([#127](https://www.github.com/dasch-swiss/dsp-tools/issues/127)) ([4dad0ce](https://www.github.com/dasch-swiss/dsp-tools/commit/4dad0ced91f0db5ef80e9690d4ce1866475577fa))


### Documentation

* update out-of-date example in docs (DEV-265) ([#125](https://www.github.com/dasch-swiss/dsp-tools/issues/125)) ([0dc724c](https://www.github.com/dasch-swiss/dsp-tools/commit/0dc724c620d0d12cd792390dcc50289b7f6feb76))


### Enhancements

* update DSP-Tools to support ArchiveRepresentation (DEV-259) ([#128](https://www.github.com/dasch-swiss/dsp-tools/issues/128)) ([85a40c2](https://www.github.com/dasch-swiss/dsp-tools/commit/85a40c203d0fa7afc7f7bb122aac0860c304acf4))

## [1.6.1](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.6.0...v1.6.1) (2021-11-25)


### Bug Fixes

* inconsistencies in groups and projects (DEV-261) ([#121](https://www.github.com/dasch-swiss/dsp-tools/issues/121)) ([f9a95ed](https://www.github.com/dasch-swiss/dsp-tools/commit/f9a95edb25dd8d685233f2b51f52b1c770f44806))
* **schema:** list root node needs a comments object (DEV-61) ([#122](https://www.github.com/dasch-swiss/dsp-tools/issues/122)) ([7bdc589](https://www.github.com/dasch-swiss/dsp-tools/commit/7bdc58961a7ae4312c1444802a32fd0dbd0176dc))

## [1.6.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.5.2...v1.6.0) (2021-11-22)


### Bug Fixes

* **comments:** fix comments in ontology creation (DEV-250) ([#119](https://www.github.com/dasch-swiss/dsp-tools/issues/119)) ([08effdf](https://www.github.com/dasch-swiss/dsp-tools/commit/08effdfea27d65b1b9ab311b47ac02eb095bc09b))
* update dsp-tools to work with API version 16.0.0 ([#117](https://www.github.com/dasch-swiss/dsp-tools/issues/117)) ([af70e9b](https://www.github.com/dasch-swiss/dsp-tools/commit/af70e9b02b8be68f13a72bb1fd284c682642757b))


### Documentation

* add time value section ([#116](https://www.github.com/dasch-swiss/dsp-tools/issues/116)) ([8ef0329](https://www.github.com/dasch-swiss/dsp-tools/commit/8ef0329e138ab8fef8050e175b1bac6caffe7fb7))
* **typo:** correcting typos in documentation ([#112](https://www.github.com/dasch-swiss/dsp-tools/issues/112)) ([08c1059](https://www.github.com/dasch-swiss/dsp-tools/commit/08c10593f5eee511859ef3731e41da4cf2debbf2))


### Enhancements

* **id-to-iri:** extend xmlupload to allow references to existing resources (DEV-60) ([#108](https://www.github.com/dasch-swiss/dsp-tools/issues/108)) ([40b01db](https://www.github.com/dasch-swiss/dsp-tools/commit/40b01db9d32353dce048e60f48e1454ff7a9bbd5))

## [1.5.2](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.5.1...v1.5.2) (2021-11-16)


### Maintenance

* **documentation:** add missing documentation for excel2resources (DEV-144) ([cde0db5](https://www.github.com/dasch-swiss/dsp-tools/commit/cde0db5fc925055c0b7a5b3ff3706afd26497f8c))

## [1.5.1](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.5.0...v1.5.1) (2021-10-13)


### Bug Fixes

* **schema-documentation:** update schemas and documentation (DEV-61) ([#105](https://www.github.com/dasch-swiss/dsp-tools/issues/105)) ([4d9c1e4](https://www.github.com/dasch-swiss/dsp-tools/commit/4d9c1e40423384914503222063bebdc09370bb94))

## [1.5.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.4.2...v1.5.0) (2021-09-24)


### Enhancements

* **schema:** add error codes for validation (DSP-1902) ([#101](https://www.github.com/dasch-swiss/dsp-tools/issues/101)) ([0bc6149](https://www.github.com/dasch-swiss/dsp-tools/commit/0bc6149b7d0c92fcc0759f4b7161682896542c58))

### [1.4.2](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.4.1...v1.4.2) (2021-09-21)


### Bug Fixes

* **docs:** fix example in documentation (DSP-1740) ([#99](https://www.github.com/dasch-swiss/dsp-tools/issues/99)) ([11cdd72](https://www.github.com/dasch-swiss/dsp-tools/commit/11cdd72911e41d837a99579caf0d9d799b0360fc))

## [1.4.1](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.4.0...v1.4.1) (2021-09-20)


### Maintenance

* **schemas:** update schemas (DSP-1902) ([#92](https://www.github.com/dasch-swiss/dsp-tools/issues/92)) ([16ba335](https://www.github.com/dasch-swiss/dsp-tools/commit/16ba335c1e8bb687a53dd8e376d88a39f2f0aa44))

## [1.4.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.3.3...v1.4.0) (2021-09-16)


### Documentation

* **typo:** correct typo in documentation ([#85](https://www.github.com/dasch-swiss/dsp-tools/issues/85)) ([c689d7f](https://www.github.com/dasch-swiss/dsp-tools/commit/c689d7fb213b334fe53c4e9b02c935a5da333f6d))


### Enhancements

* **excel-to-properties:** create properties from Excel (DSP-1577) ([#89](https://www.github.com/dasch-swiss/dsp-tools/issues/89)) ([9f48e9a](https://www.github.com/dasch-swiss/dsp-tools/commit/9f48e9ae580121e01896fc4f2f8491da8150a180))
* **excel-to-resources:** create resources from excel (DSP-1576) ([#88](https://www.github.com/dasch-swiss/dsp-tools/issues/88)) ([7b0302f](https://www.github.com/dasch-swiss/dsp-tools/commit/7b0302f2feed3475f908c3915ce89d9b5d423d11))

## [1.3.3](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.3.2...v1.3.3) (2021-09-07)

### Bug Fixes

* wrong values &
  property ([#86](https://www.github.com/dasch-swiss/dsp-tools/issues/86)) ([7cf6405](https://www.github.com/dasch-swiss/dsp-tools/commit/7cf6405ad045bbd97d34bc2d0a2d4872e873a78e))

## [1.3.2](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.3.1...v1.3.2) (2021-08-17)

### Bug Fixes

* **import:** fix import error when starting script directly (
  DSP-1869) ([05b1eb1](https://www.github.com/dasch-swiss/dsp-tools/commit/05b1eb148b3dbb2c3c4c38f85cfaa7aa782c2641))

## [1.3.1](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.3.0...v1.3.1) (2021-08-11)

### Bug Fixes

* **manifest:** fix documentation and missing files (
  DSP-1580) ([#80](https://www.github.com/dasch-swiss/dsp-tools/issues/80)) ([3345f2a](https://www.github.com/dasch-swiss/dsp-tools/commit/3345f2a05456d501c9c6323c34b28d2cab87b4ea))

## [1.3.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.2.1...v1.3.0) (2021-08-10)

### Enhancements

* **excel-lists:** create multilanguage json lists from excel files (
  DSP-1580) ([#75](https://www.github.com/dasch-swiss/dsp-tools/issues/75)) ([06d071a](https://www.github.com/dasch-swiss/dsp-tools/commit/06d071a6d47cd1002610c70b076319236bdab0db))

## [1.2.1](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.2.0...v1.2.1) (2021-07-27)

### Bug Fixes

* **release:** fix skipped release after pull request [#74](https://www.github.com/dasch-swiss/dsp-tools/issues/74) (
  DSP-1797) ([#76](https://www.github.com/dasch-swiss/dsp-tools/issues/76)) ([c8e0a11](https://www.github.com/dasch-swiss/dsp-tools/commit/c8e0a11d299a302c8829bb9eec2cf8d338bf74cf))

## [1.2.0](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.1.6...v1.2.0) (2021-07-26)

### Enhancements

* **verbose xml upload:** use v option to print verbose output in XML upload (
  DSP-1797) ([#70](https://www.github.com/dasch-swiss/dsp-tools/issues/70)) ([b1f56a1](https://www.github.com/dasch-swiss/dsp-tools/commit/b1f56a1efe8ff32376c8e4f8bf8f292d6061e016))

## [1.1.6](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.1.5...v1.1.6) (2021-07-22)

### Documentation

* add
  changelog ([#71](https://www.github.com/dasch-swiss/dsp-tools/issues/71)) ([ce1feab](https://www.github.com/dasch-swiss/dsp-tools/commit/ce1feab45e15cb203447a906c93b7caaf951670e))

## [1.1.5](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.1.4...v1.1.5) (2021-07-14)

### Documentation

* **dsp-tools-xmlupload:** Add Warning
  section ([#69](https://www.github.com/dasch-swiss/dsp-tools/issues/69)) ([05baf3d](https://www.github.com/dasch-swiss/dsp-tools/commit/05baf3d685913f187ebcebd2bc740350a8d40d42))
* **dsp-tools-xmlupload:** addition to incomplete paragraph (
  DSP-1693) ([#67](https://www.github.com/dasch-swiss/dsp-tools/issues/67)) ([318547f](https://www.github.com/dasch-swiss/dsp-tools/commit/318547fd58fd015209b42a1279baef11056b585d))

## [1.1.4](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.1.3...v1.1.4) (2021-06-16)

### Documentation

* add copyright information to docs (
  DSP-1190) ([#65](https://www.github.com/dasch-swiss/dsp-tools/issues/65)) ([0174c4a](https://www.github.com/dasch-swiss/dsp-tools/commit/0174c4afda601047a92669a2f1f92a05d75999cb))

## [1.1.3](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.1.2...v1.1.3) (2021-06-08)

### Documentation

* update readme after documentation update (
  DSP-1693) ([#63](https://www.github.com/dasch-swiss/dsp-tools/issues/63)) ([7b7dcca](https://www.github.com/dasch-swiss/dsp-tools/commit/7b7dcca55c729aa6bf995c04ae37f50a630bf9a5))

## [1.1.2](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.1.1...v1.1.2) (2021-06-07)

### Maintenance

* bump Bazel to version with M1
  support ([#60](https://www.github.com/dasch-swiss/dsp-tools/issues/60)) ([69772f4](https://www.github.com/dasch-swiss/dsp-tools/commit/69772f47e9c0ad5c5f0be28d5e60dde30eb916b9))

### Documentation

* improve documentation (
  DSP-1693) ([#62](https://www.github.com/dasch-swiss/dsp-tools/issues/62)) ([591b5ad](https://www.github.com/dasch-swiss/dsp-tools/commit/591b5ad46f8c4b6aecd023ff1448953a7c6c7d45))

## [1.1.1](https://www.github.com/dasch-swiss/dsp-tools/compare/v1.1.0...v1.1.1) (2021-04-20)

### Bug Fixes

* fix import ontology from salsah-export (
  DSP-1532) ([#59](https://www.github.com/dasch-swiss/dsp-tools/issues/59)) ([6e3e7ca](https://www.github.com/dasch-swiss/dsp-tools/commit/6e3e7ca4f603be3f656e0caede7eefbea2790383))

### Maintenance

* fix doc deployment (
  DSP-1492) ([#57](https://www.github.com/dasch-swiss/dsp-tools/issues/57)) ([a55849e](https://www.github.com/dasch-swiss/dsp-tools/commit/a55849e719559b4d10f9dcdf947d43ab8891cae0))

## 1.1.0 (2021-04-09)

### Bug Fixes

* add create_ontology command line
  configuration ([3ab7e6b](https://www.github.com/dasch-swiss/dsp-tools/commit/3ab7e6b57fe1724f9f87a5cd8d6994dfd3b679d6))
* add folder
  independence ([2460937](https://www.github.com/dasch-swiss/dsp-tools/commit/24609374fa9881467a6fa9f7b6924daec9534ddf))
* add missing
  dependencies ([4d75128](https://www.github.com/dasch-swiss/dsp-tools/commit/4d75128fc866a1ccf6fcb6aca248c59daeed10ca))
* add user ([277121b](https://www.github.com/dasch-swiss/dsp-tools/commit/277121bea1a386e429cf6826dd25e58468258c8a))
* bulk-import of multiple resource link
  values ([6ef8908](https://www.github.com/dasch-swiss/dsp-tools/commit/6ef8908ca4fb260865a252546e60381352e1b6b8)),
  closes [#9](https://www.github.com/dasch-swiss/dsp-tools/issues/9)
* cleanup api logging (
  DSP-1076) ([#46](https://www.github.com/dasch-swiss/dsp-tools/issues/46)) ([d48e704](https://www.github.com/dasch-swiss/dsp-tools/commit/d48e704cbf8e665347f4c46e6893735c853f294f))
* command line
  scripts ([732a0fa](https://www.github.com/dasch-swiss/dsp-tools/commit/732a0fa56efd88d2f9712cc132181bf24c234f3b))
* Correctly set user
  password ([9db6445](https://www.github.com/dasch-swiss/dsp-tools/commit/9db64455454bdf5281ea1642eac6206aacaf092b))
* Correctly set user
  password ([3583ea2](https://www.github.com/dasch-swiss/dsp-tools/commit/3583ea2cafc45adecc1f422e21b3e4d145879e34))
* Do not send logout request if token is not
  set ([9cfd484](https://www.github.com/dasch-swiss/dsp-tools/commit/9cfd484fc3ffc8feb13ead3404738633cbdc6ebd))
* removed exception if keywords
  missing ([81f7d97](https://www.github.com/dasch-swiss/dsp-tools/commit/81f7d97e856fcd311c2a3236b33785ae1749ba1e))
* requirements ([b5941f1](https://www.github.com/dasch-swiss/dsp-tools/commit/b5941f12ee7b52c84950ea5a49679e3ab8d7bc7f))
* typo ([3def59d](https://www.github.com/dasch-swiss/dsp-tools/commit/3def59d33d72b9e91c52a07b1d922feb7be10b73))

### Documentation

* fix twine
  upload ([bcc87ca](https://www.github.com/dasch-swiss/dsp-tools/commit/bcc87ca416344642acad4e39ad8d09fc9d7d5b51))
* update publishing
  description ([6deb0da](https://www.github.com/dasch-swiss/dsp-tools/commit/6deb0da8b1805cc790f94cf1e0198a4192e97db4))

### Enhancements

* import lists from excel (
  DSP-1341) ([#48](https://www.github.com/dasch-swiss/dsp-tools/issues/48)) ([3628992](https://www.github.com/dasch-swiss/dsp-tools/commit/362899214c850e6c3f613a3cbff29ab2294dccfb))

### Maintenance

* add existing files into new
  structure ([84dc1d2](https://www.github.com/dasch-swiss/dsp-tools/commit/84dc1d221740b49b46978303ceb727925042aa9b))
* add publishing
  setup ([c18c6b9](https://www.github.com/dasch-swiss/dsp-tools/commit/c18c6b9be54b44f929f64231722adc3c834191b5))
* add pypi
  badge ([3fc148c](https://www.github.com/dasch-swiss/dsp-tools/commit/3fc148ce16fb428ddd2b6c97d125e2df96112ad4))
* add runing tests on
  travis ([2eeaeb8](https://www.github.com/dasch-swiss/dsp-tools/commit/2eeaeb879c27565880fa637b6f050ff33e6322f8))
* add runing tests on
  travis ([cf4f9e4](https://www.github.com/dasch-swiss/dsp-tools/commit/cf4f9e46e432a2dd1f1a5c7ba37a411c52b53680))
* add runing tests on
  travis ([b8f3bbc](https://www.github.com/dasch-swiss/dsp-tools/commit/b8f3bbc75c8f3bc03632300369dd41bf2418da2c))
* add runing tests on
  travis ([dc4fa02](https://www.github.com/dasch-swiss/dsp-tools/commit/dc4fa02c8d4167b2050972e750bc05ac35496b10))
* add runing tests on
  travis ([16844d8](https://www.github.com/dasch-swiss/dsp-tools/commit/16844d8d230cf64cbd54a7258fa9f1421128c81b))
* add runing tests on
  travis ([593ac85](https://www.github.com/dasch-swiss/dsp-tools/commit/593ac85be94c58e4b49e1a9e3b624f7561d48930))
* add testing (
  ongoing) ([c175a16](https://www.github.com/dasch-swiss/dsp-tools/commit/c175a167f6d04be2054a4ffbeb47030db70c6f8f))
* allow release PRs in PR title
  check ([#54](https://www.github.com/dasch-swiss/dsp-tools/issues/54)) ([0414948](https://www.github.com/dasch-swiss/dsp-tools/commit/04149483b4b5ed7f608e577d628841ec05eb2655))
* automate release process (
  DSP-1492) ([#52](https://www.github.com/dasch-swiss/dsp-tools/issues/52)) ([6a96eee](https://www.github.com/dasch-swiss/dsp-tools/commit/6a96eee5d2617642fe9ce81b1615388aa5b5beb2))
* bump version ([49bc9d8](https://www.github.com/dasch-swiss/dsp-tools/commit/49bc9d8a18a42c7e5a173eba8906aee0fc0a294c))
* bump version ([e7364c7](https://www.github.com/dasch-swiss/dsp-tools/commit/e7364c7029424841a3fd435ba08723a40705c071))
* bump version to 1.1.0 (
  DSP-1492) ([#55](https://www.github.com/dasch-swiss/dsp-tools/issues/55)) ([3814ed2](https://www.github.com/dasch-swiss/dsp-tools/commit/3814ed2afd121cd44e526ae95bde17fa06f031df))
* configure dependencies and command
  line ([7f79530](https://www.github.com/dasch-swiss/dsp-tools/commit/7f79530dc2dcb63d43396a313ef1e5e8c0f6bf0b))
