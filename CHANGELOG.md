# Changelog

## [4.0.0](https://github.com/dasch-swiss/dsp-tools/compare/v3.0.0...v4.0.0) (2023-08-22)


### ⚠ BREAKING CHANGES

* harmonize CLI flags, rename CLI entry point and add tests for the CLI (DEV-2525) ([#463](https://github.com/dasch-swiss/dsp-tools/issues/463))

### Bug Fixes

* fix bandit workflow configuration (DEV-2536) [#470](https://github.com/dasch-swiss/dsp-tools/issues/470) ([4fd6a10](https://github.com/dasch-swiss/dsp-tools/commit/4fd6a1046cc3200e65e4df528b4be5bb0a18dd1c))
* Make gui_attributes Mandatory for Spinbox in JSON Schema (DEV-2556) ([#478](https://github.com/dasch-swiss/dsp-tools/issues/478)) ([671d846](https://github.com/dasch-swiss/dsp-tools/commit/671d846247319753237eda0e6bf73a2e551d2ee6))
* **process-files:** in case of Docker API error, don't processes files a second time (DEV-2533) [#468](https://github.com/dasch-swiss/dsp-tools/issues/468) ([bace9aa](https://github.com/dasch-swiss/dsp-tools/commit/bace9aa9fbb1cd0c4a23d542c015645e84ae3c32))
* **upload-files:** handle server error, document how to circumvent resource leak (DEV-2528, DEV-2527) ([#464](https://github.com/dasch-swiss/dsp-tools/issues/464)) ([7aa7106](https://github.com/dasch-swiss/dsp-tools/commit/7aa7106774ac2305e2185e69e357d15a672d1a8b))


### Maintenance

* bump start-stack to 2023.08.02 (DEV-2561) [#482](https://github.com/dasch-swiss/dsp-tools/issues/482) ([84fb0a9](https://github.com/dasch-swiss/dsp-tools/commit/84fb0a9a3a39e2cd7e2454325eff1aa8dcdd2e4f))
* configure bandit security checks (DEV-2532) ([#466](https://github.com/dasch-swiss/dsp-tools/issues/466)) ([28a4907](https://github.com/dasch-swiss/dsp-tools/commit/28a490764c428f722ed63bebca394bfd561752bc))
* **deps:** bump dependencies [#467](https://github.com/dasch-swiss/dsp-tools/issues/467) ([a488161](https://github.com/dasch-swiss/dsp-tools/commit/a488161ae178ddb97eed63429a7fa6cdf45b6536))
* **deps:** bump dependencies [#473](https://github.com/dasch-swiss/dsp-tools/issues/473) ([57aa687](https://github.com/dasch-swiss/dsp-tools/commit/57aa68755287e304b3a2d671995d84a5c1991dad))
* diverse refactorings (DEV-2559) ([#480](https://github.com/dasch-swiss/dsp-tools/issues/480)) ([e29299b](https://github.com/dasch-swiss/dsp-tools/commit/e29299b7da262ef5f19037f06049c44f961a393b))
* explain in readme that imagemagick and ffmpeg must be installed for local testing (DEV-2558) [#479](https://github.com/dasch-swiss/dsp-tools/issues/479) ([a000ab3](https://github.com/dasch-swiss/dsp-tools/commit/a000ab3f4907efd1f0fb0d9185e5786e26ca6632))
* fix bandit: always exit with 0 (DEV-2536) [#476](https://github.com/dasch-swiss/dsp-tools/issues/476) ([c5351b4](https://github.com/dasch-swiss/dsp-tools/commit/c5351b439cfbbc81879d5eb17278138e7945ae51))
* harmonize CLI flags, rename CLI entry point and add tests for the CLI (DEV-2525) ([#463](https://github.com/dasch-swiss/dsp-tools/issues/463)) ([c1218d6](https://github.com/dasch-swiss/dsp-tools/commit/c1218d6b2ca3c48b7aee18524775e6d2ed8e04a9))
* lint XML models (DEV-2560) ([#481](https://github.com/dasch-swiss/dsp-tools/issues/481)) ([f2e4c88](https://github.com/dasch-swiss/dsp-tools/commit/f2e4c888630dce9d4632dfde94a5636d46d28082))
* move to Python 3.11 (DEV-2524) [#461](https://github.com/dasch-swiss/dsp-tools/issues/461) ([74a93e5](https://github.com/dasch-swiss/dsp-tools/commit/74a93e522699d0987149aa3e31aa5a96b46e0658))
* refactor models.bitstream (DEV-2538) [#472](https://github.com/dasch-swiss/dsp-tools/issues/472) ([6e2deff](https://github.com/dasch-swiss/dsp-tools/commit/6e2deff7837b17793404b553089f9893498251db))
* replace re by regex (DEV-2531) ([#465](https://github.com/dasch-swiss/dsp-tools/issues/465)) ([8ac8c99](https://github.com/dasch-swiss/dsp-tools/commit/8ac8c9957215ad77176fdcc1fc815a19e9d0bbab))
* use darglint to check if the docstrings match the actual implementation (DEV-2530) ([#453](https://github.com/dasch-swiss/dsp-tools/issues/453)) ([8183235](https://github.com/dasch-swiss/dsp-tools/commit/81832352485a5558267170fd9907319e55973b6c))


### Documentation

* update outdated link (DEV-2537) [#471](https://github.com/dasch-swiss/dsp-tools/issues/471) ([9f5c468](https://github.com/dasch-swiss/dsp-tools/commit/9f5c468b22e09adeb4501c4776ab91317cbb69d2))

## [3.0.0](https://github.com/dasch-swiss/dsp-tools/compare/v2.5.0...v3.0.0) (2023-08-08)


### Enhancements

* **create:** in property definitions of JSON files, accept references to list labels (DEV-2247) ([#460](https://github.com/dasch-swiss/dsp-tools/issues/460)) ([1529330](https://github.com/dasch-swiss/dsp-tools/commit/1529330629fe74d40b7721a36bafdb54f2a99a94))


### Bug Fixes

* **upload-files, fast-xmlupload:** handle multiple pickle files (DEV-2500) ([#451](https://github.com/dasch-swiss/dsp-tools/issues/451)) ([98f0b97](https://github.com/dasch-swiss/dsp-tools/commit/98f0b976068321dce24b3104744ff7ce5a7c97f1))


### ⚠ BREAKING CHANGES

* replace gui_element Slider by Spinbox, remove gui_element SimpleText for intervals, et al. (DEV-2501) ([#452](https://github.com/dasch-swiss/dsp-tools/issues/452)) ([5e668f0](https://github.com/dasch-swiss/dsp-tools/commit/5e668f00af2ae4666480490efe76a19a50a8512e))


### Maintenance

* bump start-stack to 2023.08.01 (DEV-2514) [#458](https://github.com/dasch-swiss/dsp-tools/issues/458) ([65f2719](https://github.com/dasch-swiss/dsp-tools/commit/65f2719a11ef23a9b5d42369d427cdb3e49471b4))
* **create:** apply law of Demeter (DEV-2515) ([#459](https://github.com/dasch-swiss/dsp-tools/issues/459)) ([46cdf19](https://github.com/dasch-swiss/dsp-tools/commit/46cdf1950c197f0ef5fea4ef98fa603f77a0da72))
* **deps-dev:** bump the all-dependencies group with 2 updates ([#454](https://github.com/dasch-swiss/dsp-tools/issues/454)) ([57527cd](https://github.com/dasch-swiss/dsp-tools/commit/57527cd388c4bfeacbb2d4dafea73c8b0e89905c))
* **deps:** bump dependencies [#456](https://github.com/dasch-swiss/dsp-tools/issues/456) ([15096e7](https://github.com/dasch-swiss/dsp-tools/commit/15096e7e8286962a5180a5c2a6fd88b416210426))
* handle timeout errors in API requests (DEV-2513) ([#457](https://github.com/dasch-swiss/dsp-tools/issues/457)) ([4cdaf2a](https://github.com/dasch-swiss/dsp-tools/commit/4cdaf2abd540da79812d38b70b10845e28590e82))


## [2.5.0](https://github.com/dasch-swiss/dsp-tools/compare/v2.4.0...v2.5.0) (2023-07-28)


### Enhancements

* guess subdomains based on conventions (DEV-1979) ([#445](https://github.com/dasch-swiss/dsp-tools/issues/445)) ([d6c4ff4](https://github.com/dasch-swiss/dsp-tools/commit/d6c4ff429c9d99bd722affccaa411b4c45dad528))


### Bug Fixes

* **process-files:** quit Python interpreter after every batch to prevent "too many open files" error (DEV-2268) ([#402](https://github.com/dasch-swiss/dsp-tools/issues/402)) ([1cbf927](https://github.com/dasch-swiss/dsp-tools/commit/1cbf927ecccbff8bfa8a9c7d3043343af868bb82))
* **start-stack:** fix outdated TTL paths, open config file correctly (DEV-2497) ([#447](https://github.com/dasch-swiss/dsp-tools/issues/447)) ([98e0579](https://github.com/dasch-swiss/dsp-tools/commit/98e05791aebde482073ba0ea74f4ef5da9f04328))


### Maintenance

* bump start-stack to 2023.07.02 (DEV-2499) [#450](https://github.com/dasch-swiss/dsp-tools/issues/450) ([61af5da](https://github.com/dasch-swiss/dsp-tools/commit/61af5da1e27474287f962e0816ffb200e8546acc))
* **deps:** bump dependencies ([#449](https://github.com/dasch-swiss/dsp-tools/issues/449)) ([8fd23d4](https://github.com/dasch-swiss/dsp-tools/commit/8fd23d4b4d0bbf850b9decaa6aa805402b8fbf8c))
* increase timeout from 5 to 10 seconds (DEV-2450) [#438](https://github.com/dasch-swiss/dsp-tools/issues/438) ([4f82d2e](https://github.com/dasch-swiss/dsp-tools/commit/4f82d2e196f118586f10cee0029e75855b893341))
* run dependabot monthly, and group updates into 1 single PR (DEV-2498) [#448](https://github.com/dasch-swiss/dsp-tools/issues/448) ([e03d633](https://github.com/dasch-swiss/dsp-tools/commit/e03d6333d4ab57d3eb325c96663c2cd9de56a88e))
* **xmlupload:** forbid empty strings in some tags of the XML, et al. (DEV-2439) ([#433](https://github.com/dasch-swiss/dsp-tools/issues/433)) ([679654d](https://github.com/dasch-swiss/dsp-tools/commit/679654d0d8abba3fa3e1a040badb1869eacf8de4))

## [2.4.0](https://github.com/dasch-swiss/dsp-tools/compare/v2.3.4...v2.4.0) (2023-07-11)


### Bug Fixes

* **create:** if the name of the ontology is used in a propertyname, it gets removed (DEV-2406) [#429](https://github.com/dasch-swiss/dsp-tools/issues/429) ([e6292f0](https://github.com/dasch-swiss/dsp-tools/commit/e6292f01c661461f2913458fbd4140b309c8376c))
* **xmlupload:** make sure resources aren't created multiple times after timeout error (DEV-2412) [#432](https://github.com/dasch-swiss/dsp-tools/issues/432)  ([b109e3c](https://github.com/dasch-swiss/dsp-tools/commit/b109e3ce204f83a2336b075df4d23d3684870f7a))


### Enhancements

* **start-stack:** add flag to start stack from main branch of DSP-API repository (DEV-2396) ([#424](https://github.com/dasch-swiss/dsp-tools/issues/424)) ([6ff2c48](https://github.com/dasch-swiss/dsp-tools/commit/6ff2c487348afbc1fc09f7e71fa4d591b15e9a54))


### Maintenance

* bump start-stack to 2023.07.01 (DEV-2428) ([#430](https://github.com/dasch-swiss/dsp-tools/issues/430)) ([8e11b95](https://github.com/dasch-swiss/dsp-tools/commit/8e11b95999bb238b85c1d4d92f49b268f781aab8))
* **deps-dev:** bump black from 23.3.0 to 23.7.0 ([#431](https://github.com/dasch-swiss/dsp-tools/issues/431)) ([1aeb778](https://github.com/dasch-swiss/dsp-tools/commit/1aeb778b744c5cd78a7bc28003d759263470c87e))
* **deps-dev:** bump mkdocs-material from 9.1.17 to 9.1.18 ([#426](https://github.com/dasch-swiss/dsp-tools/issues/426)) ([7a54181](https://github.com/dasch-swiss/dsp-tools/commit/7a5418121801ffc99b24c68a485ed4b54289e880))
* **deps:** bump jsonschema from 4.17.3 to 4.18.0 ([#428](https://github.com/dasch-swiss/dsp-tools/issues/428)) ([4b1a9ff](https://github.com/dasch-swiss/dsp-tools/commit/4b1a9ff6afc6e973da42996ae9cd649a252ccc91))
* **deps:** bump lxml from 4.9.2 to 4.9.3 ([#427](https://github.com/dasch-swiss/dsp-tools/issues/427)) ([1e933b3](https://github.com/dasch-swiss/dsp-tools/commit/1e933b3fa45c20adda2a8dc65bb6990a24c83add))
* **deps:** bump pandas from 2.0.2 to 2.0.3 ([#422](https://github.com/dasch-swiss/dsp-tools/issues/422)) ([70b38b0](https://github.com/dasch-swiss/dsp-tools/commit/70b38b00f1969277670012701623249d339c17cf))
* refactor start-stack (DEV-2397) ([#423](https://github.com/dasch-swiss/dsp-tools/issues/423)) ([679a267](https://github.com/dasch-swiss/dsp-tools/commit/679a26704498e6a644cf16d26d75f83988f3adc1))
* refine/resolve ignore comments, resolve pylint issues (DEV-2398) ([#425](https://github.com/dasch-swiss/dsp-tools/issues/425)) ([906c8a3](https://github.com/dasch-swiss/dsp-tools/commit/906c8a341053b129772ffee9785f27693177f0b4))
* set up pre-commit hooks (DEV-2393) ([#420](https://github.com/dasch-swiss/dsp-tools/issues/420)) ([9578181](https://github.com/dasch-swiss/dsp-tools/commit/95781811b40d5e22e584307ce4ff0c056d16913a))

## [2.3.4](https://github.com/dasch-swiss/dsp-tools/compare/v2.3.3...v2.3.4) (2023-06-27)


### Bug Fixes

* **xmlupload:** allow colon in URL (DEV-2318) ([#419](https://github.com/dasch-swiss/dsp-tools/issues/419)) ([b79ab23](https://github.com/dasch-swiss/dsp-tools/commit/b79ab23e0db4548aff88e2ab36a7aa5161e15422))


### Maintenance

* bump start-stack to 2023.06.02 (DEV-2312) [#418](https://github.com/dasch-swiss/dsp-tools/issues/418) ([88a4bf3](https://github.com/dasch-swiss/dsp-tools/commit/88a4bf306f9b9b1dd9bbab173c8880a58c4abf15))
* **deps-dev:** bump mkdocs-material from 9.1.16 to 9.1.17 ([#414](https://github.com/dasch-swiss/dsp-tools/issues/414)) ([313b923](https://github.com/dasch-swiss/dsp-tools/commit/313b9237016393c6dac4e704d64adbb9ec186100))
* **deps-dev:** bump mypy from 1.3.0 to 1.4.0 ([#413](https://github.com/dasch-swiss/dsp-tools/issues/413)) ([919fd8e](https://github.com/dasch-swiss/dsp-tools/commit/919fd8ef642824323450efbadde31f24126bd3f7))
* **deps-dev:** bump mypy from 1.4.0 to 1.4.1 ([#415](https://github.com/dasch-swiss/dsp-tools/issues/415)) ([2867a00](https://github.com/dasch-swiss/dsp-tools/commit/2867a007598a2666646c345932ebb030eefa3318))
* **deps-dev:** bump pytest from 7.3.2 to 7.4.0 ([#416](https://github.com/dasch-swiss/dsp-tools/issues/416)) ([8d6b587](https://github.com/dasch-swiss/dsp-tools/commit/8d6b587497013f827e0bb7dd0602317f5e290f90))
* **deps-dev:** bump types-openpyxl from 3.1.0.12 to 3.1.0.13 ([#417](https://github.com/dasch-swiss/dsp-tools/issues/417)) ([7b53622](https://github.com/dasch-swiss/dsp-tools/commit/7b536222d5383bcec64953535ebb01995ee5bd2e))
* lint "models", part two (DEV-2287) ([#406](https://github.com/dasch-swiss/dsp-tools/issues/406)) ([466597c](https://github.com/dasch-swiss/dsp-tools/commit/466597c9ea23cc5de97a1e0585f0634c5a104426))
* onto create (DEV-2298) [#412](https://github.com/dasch-swiss/dsp-tools/issues/412) ([d8abe48](https://github.com/dasch-swiss/dsp-tools/commit/d8abe484f2a186dfc3d9bf564f80d8dba83946ab))
* remove dependency inconsistency in pyproject.toml (DEV-2290) [#410](https://github.com/dasch-swiss/dsp-tools/issues/410) ([9da9ccf](https://github.com/dasch-swiss/dsp-tools/commit/9da9ccf1dbbd5edb5a424e86d0df43caa082a6a1))
* remove unused code (DEV-2289) ([#409](https://github.com/dasch-swiss/dsp-tools/issues/409)) ([809f4fe](https://github.com/dasch-swiss/dsp-tools/commit/809f4febefb107d78986951f7ea2f84b75823fc2))
* **xmlupload:** improve error handling of Timeout Error (DEV-2299) ([#411](https://github.com/dasch-swiss/dsp-tools/issues/411)) ([b9cf8eb](https://github.com/dasch-swiss/dsp-tools/commit/b9cf8eb419e73a4f2c1621dedd4c3ab08ac9fd4d))

## [2.3.3](https://github.com/dasch-swiss/dsp-tools/compare/v2.3.2...v2.3.3) (2023-06-13)


### Bug Fixes

* **fast xmlupload:** make process-files more robust (DEV-2235) ([#395](https://github.com/dasch-swiss/dsp-tools/issues/395)) ([12d527b](https://github.com/dasch-swiss/dsp-tools/commit/12d527bfa98496e8839e31d2b996af3c84b8db33))


### Maintenance

* add overview of code quality tools; format code with black (DEV-2224) ([#391](https://github.com/dasch-swiss/dsp-tools/issues/391)) ([d7fb690](https://github.com/dasch-swiss/dsp-tools/commit/d7fb69053ddd4171fe8a8f1b0d44ddadc13e1602))
* allow latest version of poetry again (DEV-2245) [#398](https://github.com/dasch-swiss/dsp-tools/issues/398) ([3d646ad](https://github.com/dasch-swiss/dsp-tools/commit/3d646ad3d7bc9c0202eb27978d0360c0eb071034))
* bump start-stack to 2023.06.01 (DEV-2272) [#401](https://github.com/dasch-swiss/dsp-tools/issues/401) ([d684c18](https://github.com/dasch-swiss/dsp-tools/commit/d684c18e050737965d4334ff3a8b686043be5d89))
* **deps-dev:** bump pytest from 7.3.1 to 7.3.2 ([#403](https://github.com/dasch-swiss/dsp-tools/issues/403)) ([6dbcf6c](https://github.com/dasch-swiss/dsp-tools/commit/6dbcf6c91b37a4b96cf6b7a30a406f7008066e53))
* **deps-dev:** bump types-openpyxl from 3.1.0.8 to 3.1.0.9 ([#405](https://github.com/dasch-swiss/dsp-tools/issues/405)) ([12a97d6](https://github.com/dasch-swiss/dsp-tools/commit/12a97d6d47c352c1ca5d84b27aea8401de7f2e99))
* **deps-dev:** bump types-regex from 2023.5.5.0 to 2023.6.3.0 ([#397](https://github.com/dasch-swiss/dsp-tools/issues/397)) ([067e265](https://github.com/dasch-swiss/dsp-tools/commit/067e26506ca36d08d0cbaf9846498dace3886e50))
* **deps:** bump docker from 6.1.2 to 6.1.3 ([#393](https://github.com/dasch-swiss/dsp-tools/issues/393)) ([2a79fe6](https://github.com/dasch-swiss/dsp-tools/commit/2a79fe68f1aada10a35522884b527225a703a3f7))
* **deps:** bump regex from 2023.5.5 to 2023.6.3 ([#396](https://github.com/dasch-swiss/dsp-tools/issues/396)) ([6ee38c9](https://github.com/dasch-swiss/dsp-tools/commit/6ee38c96b5de5e66d1e818d4cf01740b9ea8c0dc))
* lint "models", part one (DEV-2265) ([#400](https://github.com/dasch-swiss/dsp-tools/issues/400)) ([27a32b1](https://github.com/dasch-swiss/dsp-tools/commit/27a32b1e0487d76dcb7b89b02948be82e97aed4d))
* loosen python requirement, add py.typed marker (DEV-2278) ([#404](https://github.com/dasch-swiss/dsp-tools/issues/404)) ([17b22b3](https://github.com/dasch-swiss/dsp-tools/commit/17b22b3d124e6ef88b0fb282f9de6e9a6144fac1))
* reformat code (DEV-2263) ([#399](https://github.com/dasch-swiss/dsp-tools/issues/399)) ([35af8c4](https://github.com/dasch-swiss/dsp-tools/commit/35af8c41517ff61e239d96d4a426b13c9ebac0fb))

## [2.3.2](https://github.com/dasch-swiss/dsp-tools/compare/v2.3.1...v2.3.2) (2023-05-31)


### Maintenance

* bump start-stack to 2023.05.03 (DEV-2222) [#392](https://github.com/dasch-swiss/dsp-tools/issues/392) ([80bdecb](https://github.com/dasch-swiss/dsp-tools/commit/80bdecb721183679dbfe09c2be2291720ee29ac2))
* **deps-dev:** bump mkdocs-material from 9.1.14 to 9.1.15 ([#390](https://github.com/dasch-swiss/dsp-tools/issues/390)) ([18287c3](https://github.com/dasch-swiss/dsp-tools/commit/18287c3d1e8a8de5fb2c3759e3bbd957dc7713a6))
* **deps-dev:** bump types-requests from 2.30.0.0 to 2.31.0.0 ([#382](https://github.com/dasch-swiss/dsp-tools/issues/382)) ([74738fa](https://github.com/dasch-swiss/dsp-tools/commit/74738fa3d371495ea7a073ac34d13ad0b032f541))
* **deps-dev:** bump types-requests from 2.31.0.0 to 2.31.0.1 ([#389](https://github.com/dasch-swiss/dsp-tools/issues/389)) ([1829fd5](https://github.com/dasch-swiss/dsp-tools/commit/1829fd50488bd43d029b48764b6757a429b599fe))
* **deps:** bump pandas from 2.0.1 to 2.0.2 ([#388](https://github.com/dasch-swiss/dsp-tools/issues/388)) ([e23bb10](https://github.com/dasch-swiss/dsp-tools/commit/e23bb1073289243b46b4d7b7b1499aabf6e0af27))
* don't configure logging statically (DEV-2183) ([#385](https://github.com/dasch-swiss/dsp-tools/issues/385)) ([7c82a59](https://github.com/dasch-swiss/dsp-tools/commit/7c82a594ea6619e807aa95883b792f4fba2d82fd))
* move _derandomize_xsd_id (DEV-2186) [#381](https://github.com/dasch-swiss/dsp-tools/issues/381) ([e909384](https://github.com/dasch-swiss/dsp-tools/commit/e90938422f657321aeab619555648b0cff399bfb))
* refactor CLI part of excel2xml (DEV-2190) ([#384](https://github.com/dasch-swiss/dsp-tools/issues/384)) ([cd9cbb7](https://github.com/dasch-swiss/dsp-tools/commit/cd9cbb75f1e05acfee2c0b828d84454888594f72))
* remove autopep8 from dependencies (DEV-2213) [#387](https://github.com/dasch-swiss/dsp-tools/issues/387) ([993854b](https://github.com/dasch-swiss/dsp-tools/commit/993854ba37ebb7c6ac4361197b9d20a2c63e3bad))
* speed up CI tests with caching (DEV-2165) ([#369](https://github.com/dasch-swiss/dsp-tools/issues/369)) ([9283aa1](https://github.com/dasch-swiss/dsp-tools/commit/9283aa1d498c319a391856dd547e5681ec3de9f6))

## [2.3.1](https://github.com/dasch-swiss/dsp-tools/compare/v2.3.0...v2.3.1) (2023-05-23)


### Bug Fixes

* **process-files:** allow files with whitespaces in filename, allow files with uppercase extension (DEV-2182) ([#379](https://github.com/dasch-swiss/dsp-tools/issues/379)) ([7f63743](https://github.com/dasch-swiss/dsp-tools/commit/7f637432817b31a70222b16ba70a664fa0e03474))


### Maintenance

* code formatting (DEV-2171) ([#376](https://github.com/dasch-swiss/dsp-tools/issues/376)) ([96a4056](https://github.com/dasch-swiss/dsp-tools/commit/96a4056b0c7280ac16907b17e4a419c1b8d886a9))
* **deps-dev:** bump mkdocs-material from 9.1.11 to 9.1.14 ([#377](https://github.com/dasch-swiss/dsp-tools/issues/377)) ([8095f6f](https://github.com/dasch-swiss/dsp-tools/commit/8095f6f9b311d013d1bde857fbed1203af268db6))
* **deps-dev:** bump types-openpyxl from 3.1.0.7 to 3.1.0.8 ([#374](https://github.com/dasch-swiss/dsp-tools/issues/374)) ([c536ebc](https://github.com/dasch-swiss/dsp-tools/commit/c536ebca7f4a41ae144af294bfd72c9975758b82))
* **deps:** bump requests from 2.30.0 to 2.31.0 ([#378](https://github.com/dasch-swiss/dsp-tools/issues/378)) ([b932e03](https://github.com/dasch-swiss/dsp-tools/commit/b932e03a4742da4da044c3dae13f25188f3a7ff6))
* enable automatic version updating by Dependabot (DEV-2170) [#373](https://github.com/dasch-swiss/dsp-tools/issues/373) ([bd1cfd2](https://github.com/dasch-swiss/dsp-tools/commit/bd1cfd21c16aed84fa1c664091789af2760382e2))
* lint e2e tests (DEV-2160) ([#366](https://github.com/dasch-swiss/dsp-tools/issues/366)) ([e75eb27](https://github.com/dasch-swiss/dsp-tools/commit/e75eb2749b8223a6b2617c2655288f06e7755e98))

## [2.3.0](https://github.com/dasch-swiss/dsp-tools/compare/v2.2.2...v2.3.0) (2023-05-17)


### Bug Fixes

* **get:** write proper tests for get command, fix multiple bugs (DEV-2123) ([#356](https://github.com/dasch-swiss/dsp-tools/issues/356)) ([edd671d](https://github.com/dasch-swiss/dsp-tools/commit/edd671da0a1af4265da09c2e490f2df6b69e0a3c))


### Documentation

* render nested lists correctly, adapt markdownlint rules, apply new rules everywhere (DEV-2134) ([#358](https://github.com/dasch-swiss/dsp-tools/issues/358)) ([e899d5c](https://github.com/dasch-swiss/dsp-tools/commit/e899d5c78d2281dc4efe7e54d8c4d8541196bf3e))


### Enhancements

* fast XML upload (DEV-1626) ([#352](https://github.com/dasch-swiss/dsp-tools/issues/352)) ([c2f46ea](https://github.com/dasch-swiss/dsp-tools/commit/c2f46ea432bc5aa37557c034e22f2fbc855198ba))


### Maintenance

* bump dependencies, add docker, update readme, remove unused poetry exec script (DEV-2159) ([#365](https://github.com/dasch-swiss/dsp-tools/issues/365)) ([69d65e7](https://github.com/dasch-swiss/dsp-tools/commit/69d65e7bf51a4fc98f6287e10d224d6b0a30f62e))
* bump start-stack to 2023.05.01 (DEV-2164) [#368](https://github.com/dasch-swiss/dsp-tools/issues/368) ([646586b](https://github.com/dasch-swiss/dsp-tools/commit/646586b20d7fb4331dbfdff6c6d8b87396f37f75))
* **deps:** bump pymdown-extensions from 9.11 to 10.0 ([#370](https://github.com/dasch-swiss/dsp-tools/issues/370)) ([1764e81](https://github.com/dasch-swiss/dsp-tools/commit/1764e81a78e10eaea42fa842b776c041a449f7bf))
* **excel2xml:** minor improvements (DEV-2152) [#360](https://github.com/dasch-swiss/dsp-tools/issues/360) ([1d24848](https://github.com/dasch-swiss/dsp-tools/commit/1d2484808f230964cad6ea06be6201bfdf067efe))
* log every CLI call to dsp-tools (DEV-2156) [#362](https://github.com/dasch-swiss/dsp-tools/issues/362)  ([a93cb86](https://github.com/dasch-swiss/dsp-tools/commit/a93cb8637796d52581d05348015b4143429fbca0))
* make all test files executable with pytest (DEV-2157) ([1e4d427](https://github.com/dasch-swiss/dsp-tools/commit/1e4d42720222bf7eab36380b5cd835c1c23471fa))
* prevent access to unset attribute of BaseError (DEV-2158) [#364](https://github.com/dasch-swiss/dsp-tools/issues/364) ([b0e089d](https://github.com/dasch-swiss/dsp-tools/commit/b0e089d357587813a7d77a2198038af22be4f631))
* resolve CodeQL issues (DEV-2169) [#371](https://github.com/dasch-swiss/dsp-tools/issues/371) ([6822344](https://github.com/dasch-swiss/dsp-tools/commit/6822344060c56460ad202bb4081feea9a1cac72a))
* update mypy, resolve all mypy+pylint issues in "unittests", unignore "unittests" in CI pipline (DEV-2131) ([#357](https://github.com/dasch-swiss/dsp-tools/issues/357)) ([b75e2c7](https://github.com/dasch-swiss/dsp-tools/commit/b75e2c734c4937c535561e3309c49d6660c68d7a))
* XML validation: resource's iri and ark must be unique, resource's label must not be empty (DEV-2154) ([#361](https://github.com/dasch-swiss/dsp-tools/issues/361)) ([62ec04b](https://github.com/dasch-swiss/dsp-tools/commit/62ec04b7dc31330536337b21b03b015f5795c7bf))

## [2.2.2](https://github.com/dasch-swiss/dsp-tools/compare/v2.2.1...v2.2.2) (2023-05-03)


### Bug Fixes

* **xmlupload:** print reason of error if a resource cannot be created, remodel BaseError (DEV-1977) ([#349](https://github.com/dasch-swiss/dsp-tools/issues/349)) ([7f60b1a](https://github.com/dasch-swiss/dsp-tools/commit/7f60b1a39365a534451045975835373952b2d953))


### Maintenance

* bump start-stack to 2023.04.03 (DEV-2117) ([#355](https://github.com/dasch-swiss/dsp-tools/issues/355)) ([1abb081](https://github.com/dasch-swiss/dsp-tools/commit/1abb081e2e367d5f7c46190168c6fb2f4440b1aa))
* resolve linting errors, make linting checks in CI more strict (DEV-2080) ([#354](https://github.com/dasch-swiss/dsp-tools/issues/354)) ([e3daff3](https://github.com/dasch-swiss/dsp-tools/commit/e3daff37c2b9f699db91d0c1f71667c809b5f87b))

## [2.2.1](https://github.com/dasch-swiss/dsp-tools/compare/v2.2.0...v2.2.1) (2023-04-18)


### Maintenance

* bump dependencies (DEV-1960) [#350](https://github.com/dasch-swiss/dsp-tools/issues/350) ([5b999f5](https://github.com/dasch-swiss/dsp-tools/commit/5b999f5f534da38e62433adeb9725426c91195cb))
* bump start-stack to 2023.04.02 (DEV-1933) ([#351](https://github.com/dasch-swiss/dsp-tools/issues/351)) ([163ac19](https://github.com/dasch-swiss/dsp-tools/commit/163ac1953da303cbb67fe23badb5d13cefebf9e6))
* **get:** allow shortname to be uppercase (DEV-1972) [#346](https://github.com/dasch-swiss/dsp-tools/issues/346) ([e0ce7d4](https://github.com/dasch-swiss/dsp-tools/commit/e0ce7d42a613dc8b3d2d962a5c388891a2d37bac))
* inside a JSON or Excel file, resource & property names must be unique (DEV-1971) ([#345](https://github.com/dasch-swiss/dsp-tools/issues/345)) ([c6df889](https://github.com/dasch-swiss/dsp-tools/commit/c6df8892bdc07309aa60fdedd743db3576ca52fd))
* refactor try_network_action() (DEV-1844) ([#325](https://github.com/dasch-swiss/dsp-tools/issues/325)) ([896586f](https://github.com/dasch-swiss/dsp-tools/commit/896586f4eaab4f397e50f0dfb68a2a2eb9fae0dc))

## [2.2.0](https://github.com/dasch-swiss/dsp-tools/compare/v2.1.1...v2.2.0) (2023-03-21)


### Bug Fixes

* allow Pulldown, Radio, and List as gui_elements for lists (DEV-1810) ([#330](https://github.com/dasch-swiss/dsp-tools/issues/330)) ([5ff1aac](https://github.com/dasch-swiss/dsp-tools/commit/5ff1aac9df3f875c754ba76c876e8fceeb29180a))
* correct broken schema references in test data files (DEV-1832) [#323](https://github.com/dasch-swiss/dsp-tools/issues/323) ([512de36](https://github.com/dasch-swiss/dsp-tools/commit/512de3641726dc08f4d83a27e35fee1391cdad86))
* **create, get:** handle comment to ontology (DEV-1852) [#326](https://github.com/dasch-swiss/dsp-tools/issues/326) ([5af3f19](https://github.com/dasch-swiss/dsp-tools/commit/5af3f19e214774ddfa9fa7ad8e7337d07893ed52))
* **create:** allow identical onto names if they belong to different projects (DEV-1777) ([#314](https://github.com/dasch-swiss/dsp-tools/issues/314)) ([7139f67](https://github.com/dasch-swiss/dsp-tools/commit/7139f67d9fa010e1e2c4335bc77e8752ee6ed0b7))
* **create:** prevent infinite loop when super-resource is not existing (DEV-1886) ([#338](https://github.com/dasch-swiss/dsp-tools/issues/338)) ([b176b7c](https://github.com/dasch-swiss/dsp-tools/commit/b176b7ce09e52fe21223160a37c1f04aff1ee047))
* **xmlupload:** legitimate html-escapes in utf8-texts don't raise a validation error any more (DEV-1936) ([#341](https://github.com/dasch-swiss/dsp-tools/issues/341)) ([cf90269](https://github.com/dasch-swiss/dsp-tools/commit/cf902690e59edc492a742e3d1f252486cec0b01a))
* **xmlupload:** write metrics only when requested to do so (DEV-1883) [#334](https://github.com/dasch-swiss/dsp-tools/issues/334) ([5c1196f](https://github.com/dasch-swiss/dsp-tools/commit/5c1196fd1749498e6df8f5c3c3f886dd18642ed1))


### Enhancements

* check out rosetta and upload it on local stack (DEV-1842) ([#332](https://github.com/dasch-swiss/dsp-tools/issues/332)) ([d067cc1](https://github.com/dasch-swiss/dsp-tools/commit/d067cc14f028fd0d1dbf2becb279f7588310fa71))
* **create:** create a resource class without cardinalities (DEV-1853) [#327](https://github.com/dasch-swiss/dsp-tools/issues/327) ([2d1cee0](https://github.com/dasch-swiss/dsp-tools/commit/2d1cee011b980ba0c6dacd7661467f52d72e5835))
* new command to generate template repo, move schema files (DEV-1839) ([#333](https://github.com/dasch-swiss/dsp-tools/issues/333)) ([9ea3a4f](https://github.com/dasch-swiss/dsp-tools/commit/9ea3a4f9b882ac9c931ed6e58df9801fd47e3e38))


### Documentation

* replace outdated screenshot, use local copy of CSS of dsp-docs (DEV-1896) ([#337](https://github.com/dasch-swiss/dsp-tools/issues/337)) ([c22c5e4](https://github.com/dasch-swiss/dsp-tools/commit/c22c5e47c250f6d3c8789b1d5dee752fe08646df))
* use single quotes around passwords to prevent problems with special characters (DEV-1825) [#320](https://github.com/dasch-swiss/dsp-tools/issues/320) ([ca2bf1a](https://github.com/dasch-swiss/dsp-tools/commit/ca2bf1a6c4fef12d709aed29181590dbde2b0005))


### Maintenance

* adapt shortcode of import scripts (DEV-1925) ([#340](https://github.com/dasch-swiss/dsp-tools/issues/340)) ([f440bda](https://github.com/dasch-swiss/dsp-tools/commit/f440bda058e9ae54d545a1848c71333b8eb68948))
* bump start-stack to 2023.03.02 (DEV-1819) ([#317](https://github.com/dasch-swiss/dsp-tools/issues/317)) ([54a4514](https://github.com/dasch-swiss/dsp-tools/commit/54a4514af12182bd6d2645d0cff1a389b278a5f9))
* **excel2json:** improve error messages of excel2json (DEV-1789) ([#315](https://github.com/dasch-swiss/dsp-tools/issues/315)) ([36a1209](https://github.com/dasch-swiss/dsp-tools/commit/36a120990a0ea2f4456ca63ed8c42a6b453f1c3d))
* implement logging system (DEV-132) ([#335](https://github.com/dasch-swiss/dsp-tools/issues/335)) ([c92e943](https://github.com/dasch-swiss/dsp-tools/commit/c92e9438e20b9af704f9d145a4a50039c47d4cb3))
* merge dublette class into one class (DEV-1831) [#322](https://github.com/dasch-swiss/dsp-tools/issues/322) ([e5cddf5](https://github.com/dasch-swiss/dsp-tools/commit/e5cddf5ef73425ebf1f408d58930f76d759c1c7b))
* minor improvements (DEV-1912) [#336](https://github.com/dasch-swiss/dsp-tools/issues/336) ([91664a9](https://github.com/dasch-swiss/dsp-tools/commit/91664a99a8d4a46e72659284036b0de833976d52))
* new error handling strategy (DEV-1770) ([#324](https://github.com/dasch-swiss/dsp-tools/issues/324)) ([f2aa4b0](https://github.com/dasch-swiss/dsp-tools/commit/f2aa4b077cd071edf9623f956c1f3385e110decf))
* remove pystrict dependency (DEV-1843) [#329](https://github.com/dasch-swiss/dsp-tools/issues/329) ([2111d21](https://github.com/dasch-swiss/dsp-tools/commit/2111d217764fbde8c763d6cce47fba172ddf9f8a))
* save location for log files (DEV-1856) ([#328](https://github.com/dasch-swiss/dsp-tools/issues/328)) ([30f914d](https://github.com/dasch-swiss/dsp-tools/commit/30f914df808c2b78b31eef5fab9d546436f01a5c))
* tidy up testdata folder (DEV-1822) ([#319](https://github.com/dasch-swiss/dsp-tools/issues/319)) ([b5fe9fd](https://github.com/dasch-swiss/dsp-tools/commit/b5fe9fd8f1cdc9ee536230303dfa3369512df022))
* **xmlupload:** improve user feedback when shortcode or onto are inexistent (DEV-1827) ([#321](https://github.com/dasch-swiss/dsp-tools/issues/321)) ([f21a64e](https://github.com/dasch-swiss/dsp-tools/commit/f21a64e6198cca805db3281a1f3fefe5b7363e0f))

## [2.1.1](https://github.com/dasch-swiss/dsp-tools/compare/v2.1.0...v2.1.1) (2023-03-08)


### Bug Fixes

* **excel2json:** add missing comments in the resources template (DEV-1765) [#303](https://github.com/dasch-swiss/dsp-tools/issues/303) ([b2532e4](https://github.com/dasch-swiss/dsp-tools/commit/b2532e47e6020db39fde74db62cd8b74e55f02de))
* **excel2xml:** make_xsd_id_compatible() does now replace all special characters (DEV-1792) ([#313](https://github.com/dasch-swiss/dsp-tools/issues/313)) ([b87f903](https://github.com/dasch-swiss/dsp-tools/commit/b87f903080ffd053c858b3b63e493e7911b7f7f7))
* **excel2xml:** proper handling of special characters in text properties, depending on the encoding (DEV-1719) ([#296](https://github.com/dasch-swiss/dsp-tools/issues/296)) ([c8f1e7a](https://github.com/dasch-swiss/dsp-tools/commit/c8f1e7ac01319460eb008fb3205fc62fb59344e2))
* **get:** prevent invalid gui_element "Pulldown" (DEV-1781) [#312](https://github.com/dasch-swiss/dsp-tools/issues/312) ([c5d355e](https://github.com/dasch-swiss/dsp-tools/commit/c5d355e362cb99537557702630fd46d8d39bf49d))
* invalid argument names in CLI entrypoint (DEV-1776) [#310](https://github.com/dasch-swiss/dsp-tools/issues/310) ([6e1a6fb](https://github.com/dasch-swiss/dsp-tools/commit/6e1a6fb921ee2214c450e629e04f715638980b76))


### Maintenance

* allow input of xmlupload to be parsed (DEV-1780) ([#311](https://github.com/dasch-swiss/dsp-tools/issues/311)) ([abc167f](https://github.com/dasch-swiss/dsp-tools/commit/abc167f0881878800dfd7253b06de6e5f4aa53c5))
* beautify stack traces (DEV-1766) [#305](https://github.com/dasch-swiss/dsp-tools/issues/305) ([17b6f2f](https://github.com/dasch-swiss/dsp-tools/commit/17b6f2f1b75e7e0e5a156d12f367c3f6a7cd1579))
* bump start-stack to 2023.03.01 (DEV-1802) ([#316](https://github.com/dasch-swiss/dsp-tools/issues/316)) ([3d3f476](https://github.com/dasch-swiss/dsp-tools/commit/3d3f476410bc75719fe2bb9c9e9aa373766d9da4))
* harmonize CLI help texts with the CLI commands documentation (DEV-1767) ([#306](https://github.com/dasch-swiss/dsp-tools/issues/306)) ([f9e4dca](https://github.com/dasch-swiss/dsp-tools/commit/f9e4dca1fce76f1f411ac46632fc4905b42a98d3))
* new error handling strategy (DEV-1773) ([#307](https://github.com/dasch-swiss/dsp-tools/issues/307)) ([4c02e18](https://github.com/dasch-swiss/dsp-tools/commit/4c02e180db7bec024c843bccbfde1a1357eeb228))
* refactor list creation (DEV-1775) ([#309](https://github.com/dasch-swiss/dsp-tools/issues/309)) ([78a8488](https://github.com/dasch-swiss/dsp-tools/commit/78a848812d48f2a49e568350471ff023b1a724e9))
* refactor onto creation (DEV-1774) ([#308](https://github.com/dasch-swiss/dsp-tools/issues/308)) ([f5a16e4](https://github.com/dasch-swiss/dsp-tools/commit/f5a16e4f938c2607d092e15d7bfc7bf3a5a41554))

## [2.1.0](https://github.com/dasch-swiss/dsp-tools/compare/v2.0.3...v2.1.0) (2023-02-21)


### Bug Fixes

* **create:** improve validation to prevent endless loop if properties are undefined (DEV-1720) ([#297](https://github.com/dasch-swiss/dsp-tools/issues/297)) ([ee3e446](https://github.com/dasch-swiss/dsp-tools/commit/ee3e4469dde19790841617f4aab76e673e0ef3f2))
* **create:** property from other ontology not found (DEV-1381) [#299](https://github.com/dasch-swiss/dsp-tools/issues/299) ([d1345ec](https://github.com/dasch-swiss/dsp-tools/commit/d1345ecce816b220a142e570fa2d824325b089ea))


### Documentation

* fix identical heading problem, assimilate mkdocs config to dsp-docs (DEV-1713) ([#294](https://github.com/dasch-swiss/dsp-tools/issues/294)) ([c235ff3](https://github.com/dasch-swiss/dsp-tools/commit/c235ff341a54a44b38e8f579a3791245f749517f))


### Enhancements

* **excel2json:** add support for gui_order, make templates better understandable (DEV-1711) ([#293](https://github.com/dasch-swiss/dsp-tools/issues/293)) ([3b5304f](https://github.com/dasch-swiss/dsp-tools/commit/3b5304fb0dd52515ae7d9595a969e2364358a4ec))


### Maintenance

* bump start-stack to 2023.02.02 (DEV-1732) [#302](https://github.com/dasch-swiss/dsp-tools/issues/302) ([b97a696](https://github.com/dasch-swiss/dsp-tools/commit/b97a6964ae86756642dfb657d6bebd2b6b61f6e5))
* enhanced xmlupload: add test onto (DEV-1760) [#300](https://github.com/dasch-swiss/dsp-tools/issues/300) ([ca32842](https://github.com/dasch-swiss/dsp-tools/commit/ca32842f07d1b72cb9960d979de0906d14d24516))
* **excel2xml:** allow PathLike for bitstream-prop (DEV-1729) [#298](https://github.com/dasch-swiss/dsp-tools/issues/298) ([ab9386f](https://github.com/dasch-swiss/dsp-tools/commit/ab9386fae84d9b91f627a474c072c9413ca19009))
* remove temporary workaround in GET groups (DEV-1733) [#301](https://github.com/dasch-swiss/dsp-tools/issues/301) ([7ead9de](https://github.com/dasch-swiss/dsp-tools/commit/7ead9dea33eb75711693f4b31a4ebafbe5eef874))

## [2.0.3](https://github.com/dasch-swiss/dsp-tools/compare/v2.0.2...v2.0.3) (2023-02-07)


### Documentation

* restructure docs, add link-checking (DEV-1623) ([#286](https://github.com/dasch-swiss/dsp-tools/issues/286)) ([d65ff53](https://github.com/dasch-swiss/dsp-tools/commit/d65ff53ec2f4b368326234f5cb8516b209834341))


### Maintenance

* access data files correctly (DEV-1618) ([#288](https://github.com/dasch-swiss/dsp-tools/issues/288)) ([7a64a27](https://github.com/dasch-swiss/dsp-tools/commit/7a64a27a2af2a41a4b98bd545bbe36b046b5d27b))
* bump start-stack to 2023.02.01 (DEV-1709) ([#292](https://github.com/dasch-swiss/dsp-tools/issues/292)) ([5fd58d2](https://github.com/dasch-swiss/dsp-tools/commit/5fd58d266d407c134f91ed527be4965c5336435c))
* bump versions of start-stack to 2023.01.02 (DEV-1652) ([#290](https://github.com/dasch-swiss/dsp-tools/issues/290)) ([2889a20](https://github.com/dasch-swiss/dsp-tools/commit/2889a20d494c311205cdf425a12d3bc12a398579))
* update links according to new structure of docs (DEV-1648) ([#289](https://github.com/dasch-swiss/dsp-tools/issues/289)) ([16d9c12](https://github.com/dasch-swiss/dsp-tools/commit/16d9c1234c404badc62f1882ab74001bee22b977))

## [2.0.2](https://github.com/dasch-swiss/dsp-tools/compare/v2.0.1...v2.0.2) (2023-01-17)


### Bug Fixes

* get command fails if no groups are on the server (DEV-1622) ([#283](https://github.com/dasch-swiss/dsp-tools/issues/283)) ([d6bf458](https://github.com/dasch-swiss/dsp-tools/commit/d6bf4588484ed40618e67c152c88ebee55b5f690))


### Documentation

* fix broken links, make dsp-tools uppercase (DEV-1550) ([#284](https://github.com/dasch-swiss/dsp-tools/issues/284)) ([aa66109](https://github.com/dasch-swiss/dsp-tools/commit/aa66109bd55eb370138a7a6672cc647ae55e425e))

## [2.0.1](https://github.com/dasch-swiss/dsp-tools/compare/v2.0.0...v2.0.1) (2023-01-17)


### Maintenance

* bump versions of start-stack, use dynamic project IRI in get command (DEV-1613) ([#282](https://github.com/dasch-swiss/dsp-tools/issues/282)) ([2ecf4f5](https://github.com/dasch-swiss/dsp-tools/commit/2ecf4f5c7ae7269f36bace5b6786975bb7088681))
* refactor project creation (DEV-1165) ([#280](https://github.com/dasch-swiss/dsp-tools/issues/280)) ([5e662a6](https://github.com/dasch-swiss/dsp-tools/commit/5e662a6f59aeb6b6e84e4f56fd5f700eb12e93cb))
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
* **testdata:** remove salsah-links from id2iri/test-id2iri-data.xml (DEV-975) ([#199](https://www.github.com/dasch-swiss/dsp-tools/issues/199)) ([7548501](https://www.github.com/dasch-swiss/dsp-tools/commit/7548501426edb3845e513e9916533bb21f74ea17))
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
