# Changelog

## [16.12.1](https://github.com/dasch-swiss/dsp-tools/compare/v16.12.0...v16.12.1) (2025-09-26)


### Bug Fixes

* **excel2json:** make list sorting consistent across OS ([#1963](https://github.com/dasch-swiss/dsp-tools/issues/1963)) ([a02d434](https://github.com/dasch-swiss/dsp-tools/commit/a02d4344bdbc76fe10594ff7ea2aa9da34fbd75c))
* **validate:** handle absent key gracefully (DEV-5428) ([#1960](https://github.com/dasch-swiss/dsp-tools/issues/1960)) ([8e0c563](https://github.com/dasch-swiss/dsp-tools/commit/8e0c563670445965e813efaaed4418549cead2c1))


### Maintenance

* **start-stack:** bump versions to 2025.09.04 ([#1962](https://github.com/dasch-swiss/dsp-tools/issues/1962)) ([c11177c](https://github.com/dasch-swiss/dsp-tools/commit/c11177c792c956d1a44d89b8e3a996b151876c20))

## [16.12.0](https://github.com/dasch-swiss/dsp-tools/compare/v16.11.0...v16.12.0) (2025-09-17)


### Enhancements

* **create:** allow reusing props from another onto (DEV-5418) ([#1956](https://github.com/dasch-swiss/dsp-tools/issues/1956)) ([66aa897](https://github.com/dasch-swiss/dsp-tools/commit/66aa89768ce036391f321ec5e6f46d27b2bdbb2a))
* remove `template` CLI command (DEV-5385) ([#1958](https://github.com/dasch-swiss/dsp-tools/issues/1958)) ([e31d07e](https://github.com/dasch-swiss/dsp-tools/commit/e31d07ecacc52b526524f922669a45b49370c3a0))
* **xmlupload:** implement warning for large fuseki bloating on localhost (DEV-5402) ([#1952](https://github.com/dasch-swiss/dsp-tools/issues/1952)) ([00da0ef](https://github.com/dasch-swiss/dsp-tools/commit/00da0ef6da12cb0c635f0cf852e88068cf8f67be))


### Bug Fixes

* **excel2json:** enable references to other ontologies in resource cardinalities (DEV-5416) ([#1954](https://github.com/dasch-swiss/dsp-tools/issues/1954)) ([0d6de05](https://github.com/dasch-swiss/dsp-tools/commit/0d6de05924c13d4a6061156e4723c79db59cfd75))
* **xmllib:** add missing Umlaute to `xsd:ID` regex (DEV-5382) ([#1957](https://github.com/dasch-swiss/dsp-tools/issues/1957)) ([f21ddb3](https://github.com/dasch-swiss/dsp-tools/commit/f21ddb37ce3da88193deda0cdbba868ef65ed02e))


### Maintenance

* **start-stack:** bump versions to 2025.09.03 ([#1959](https://github.com/dasch-swiss/dsp-tools/issues/1959)) ([ae2aa31](https://github.com/dasch-swiss/dsp-tools/commit/ae2aa316b76ed533cf2ac66c12a553909c3f5130))

## [16.11.0](https://github.com/dasch-swiss/dsp-tools/compare/v16.10.0...v16.11.0) (2025-09-10)


### Enhancements

* **get:** support legacy permissions (DOAPs) (DEV-5346) ([#1945](https://github.com/dasch-swiss/dsp-tools/issues/1945)) ([7c2804d](https://github.com/dasch-swiss/dsp-tools/commit/7c2804d1f965b5772d819d1cdf7257a694536271))
* **validate-data:** ensure that integers are within the range specified for `xsd:int` (DEV-5391) ([#1951](https://github.com/dasch-swiss/dsp-tools/issues/1951)) ([0512a01](https://github.com/dasch-swiss/dsp-tools/commit/0512a01d42d12d7e085af58b1099374e42b51d47))


### Bug Fixes

* **validate-data:** implement `sh:DatatypeConstraintComponent` in validation (DEV-5387) ([#1950](https://github.com/dasch-swiss/dsp-tools/issues/1950)) ([e7d9e6c](https://github.com/dasch-swiss/dsp-tools/commit/e7d9e6c093eada592a0396e848cba58d54000381))
* **xmllib:** replace usage of the deprecated `create_list_from_string` with `create_list_from_input` (DEV-5397) ([#1949](https://github.com/dasch-swiss/dsp-tools/issues/1949)) ([de0dc8c](https://github.com/dasch-swiss/dsp-tools/commit/de0dc8c48a5e6a23ff75027f92e1a1024a56815f))


### Maintenance

* **start-stack:** bump versions to 2025.09.02 ([#1953](https://github.com/dasch-swiss/dsp-tools/issues/1953)) ([a0790b8](https://github.com/dasch-swiss/dsp-tools/commit/a0790b86509aca62e255279a1b6e58278119cdb1))

## [16.10.0](https://github.com/dasch-swiss/dsp-tools/compare/v16.9.0...v16.10.0) (2025-09-03)


### Enhancements

* **excel2json:** guarantee sorting of labels/comments in output (DEV-5369) ([#1942](https://github.com/dasch-swiss/dsp-tools/issues/1942)) ([cda7db7](https://github.com/dasch-swiss/dsp-tools/commit/cda7db7e6659c5dcced079ae45c48ffb0fcfa62d))


### Bug Fixes

* **get:** don't crash when no credentials are given (DEV-5347) ([#1940](https://github.com/dasch-swiss/dsp-tools/issues/1940)) ([272dc59](https://github.com/dasch-swiss/dsp-tools/commit/272dc598a15f7554920aec22b16b8edd413e85ae))
* **start-stack:** asset download on localhost broken (DEV-5362) ([#1939](https://github.com/dasch-swiss/dsp-tools/issues/1939)) ([263de95](https://github.com/dasch-swiss/dsp-tools/commit/263de959444db72a8230d8a4cd3a16a9d254c4f3))


### Maintenance

* **start-stack:** remove fuseki initialization and bump versions to 2025.09.01 (DEV-5297) ([#1937](https://github.com/dasch-swiss/dsp-tools/issues/1937)) ([6a06645](https://github.com/dasch-swiss/dsp-tools/commit/6a0664582d5200cae69d0478af87b5ddfa71700f))


### Documentation

* reorganisation documentation structure (DEV-5371) ([#1946](https://github.com/dasch-swiss/dsp-tools/issues/1946)) ([abb5407](https://github.com/dasch-swiss/dsp-tools/commit/abb5407a2b36c8e9be6f476147679c85f45e21a5))
* **xmllib:** create overview of xmllib (DEV-5291) ([#1930](https://github.com/dasch-swiss/dsp-tools/issues/1930)) ([5a4391a](https://github.com/dasch-swiss/dsp-tools/commit/5a4391a820deb127779a6f8f63c47c61d90f6bd6))
* **xmllib:** fix links after renaming files and update CLAUDE.md (DEV-5370) ([#1943](https://github.com/dasch-swiss/dsp-tools/issues/1943)) ([309c418](https://github.com/dasch-swiss/dsp-tools/commit/309c418bbc3388d6c6ec8bed77f56ad15fad1a1a))

## [16.9.0](https://github.com/dasch-swiss/dsp-tools/compare/v16.8.0...v16.9.0) (2025-08-27)


### Enhancements

* **get:** retrieve class-wise and property-wise DOAPs (DEV-5120) ([#1919](https://github.com/dasch-swiss/dsp-tools/issues/1919)) ([30d0a67](https://github.com/dasch-swiss/dsp-tools/commit/30d0a67c2277152d6ad207e631b6129d4a3f0aff))
* **xmllib:** create functions to explicitly add textareas to a resource (DEV-5305) ([#1936](https://github.com/dasch-swiss/dsp-tools/issues/1936)) ([6daf503](https://github.com/dasch-swiss/dsp-tools/commit/6daf503b97c03c41e3dd98d715fe04d1d2f3cf79))
* **xmllib:** improve message of deprecation warning (DEV-5300) ([#1932](https://github.com/dasch-swiss/dsp-tools/issues/1932)) ([81d76da](https://github.com/dasch-swiss/dsp-tools/commit/81d76da09d8148b57e5a28d828b1e6aae7c73d46))


### Bug Fixes

* empty log files written during long-lived debugging sessions (DEV-5281) ([#1931](https://github.com/dasch-swiss/dsp-tools/issues/1931)) ([3b19134](https://github.com/dasch-swiss/dsp-tools/commit/3b19134f81f4527347ce390d14a4f0dc0ca17a34))
* **excel2json:** put "default_permissions_overrule" at correct position (DEV-5345) ([#1935](https://github.com/dasch-swiss/dsp-tools/issues/1935)) ([7a94bbc](https://github.com/dasch-swiss/dsp-tools/commit/7a94bbcb51b3c26baeeeba608c3dff048375ab3a))
* **xmllib:** consider permissions of values and files when evaluating which are referenced (DEV-5290) ([#1927](https://github.com/dasch-swiss/dsp-tools/issues/1927)) ([46942aa](https://github.com/dasch-swiss/dsp-tools/commit/46942aa11f73fdc8a47a67b5788b0061b5600c48))


### Maintenance

* **start-stack:** bump versions to 2025.08.04 ([#1938](https://github.com/dasch-swiss/dsp-tools/issues/1938)) ([4e89926](https://github.com/dasch-swiss/dsp-tools/commit/4e89926776b2bf72268ae19faa39cfb53f4766c7))
* waypaver for DOAP-PR ([#1928](https://github.com/dasch-swiss/dsp-tools/issues/1928)) ([6ff1012](https://github.com/dasch-swiss/dsp-tools/commit/6ff10127d08678700c06783111788e32af90367d))


### Documentation

* **excel2json:** better explanation of default_permissions_overrule ([#1934](https://github.com/dasch-swiss/dsp-tools/issues/1934)) ([6506fc5](https://github.com/dasch-swiss/dsp-tools/commit/6506fc5f4e6931fc1ec0065e67bc3794aa506085))
* **xmllib:** split up configuration options and improve grouping of sections (DEV-5302) ([#1933](https://github.com/dasch-swiss/dsp-tools/issues/1933)) ([8d51d6f](https://github.com/dasch-swiss/dsp-tools/commit/8d51d6fa12674a493fca381b9b92bb44767dcb45))

## [16.8.0](https://github.com/dasch-swiss/dsp-tools/compare/v16.7.0...v16.8.0) (2025-08-20)


### Enhancements

* add docker health check to all CLI-commands if they are on localhost and require a stack (DEV-5227) ([#1924](https://github.com/dasch-swiss/dsp-tools/issues/1924)) ([c66a19a](https://github.com/dasch-swiss/dsp-tools/commit/c66a19a153f5c11380d658eee0f9c3b63463c6da))
* **excel2json:** add support for overruling default permissions for classes/properties (DEV-5032) ([#1915](https://github.com/dasch-swiss/dsp-tools/issues/1915)) ([69a20ee](https://github.com/dasch-swiss/dsp-tools/commit/69a20ee6ba80e36846f965f6affb1b1db3b54841))


### Maintenance

* **start-stack:** bump versions to 2025.08.03 ([#1926](https://github.com/dasch-swiss/dsp-tools/issues/1926)) ([05c927b](https://github.com/dasch-swiss/dsp-tools/commit/05c927b14e2f37acbc008dbc4941fac524dde8e6))


### Documentation

* improve the wording for the text value in the ontology (DEV-5279) ([#1920](https://github.com/dasch-swiss/dsp-tools/issues/1920)) ([bd503c4](https://github.com/dasch-swiss/dsp-tools/commit/bd503c41fb34f27c275fa1e9db5322a9a2c27ee5))
* **xmllib:** add tips and links to helper functions ([#1922](https://github.com/dasch-swiss/dsp-tools/issues/1922)) ([16e4352](https://github.com/dasch-swiss/dsp-tools/commit/16e4352126d76693e007bc3b130e9f88abe58b61))

## [16.7.0](https://github.com/dasch-swiss/dsp-tools/compare/v16.6.1...v16.7.0) (2025-08-13)


### Enhancements

* change organisation of log files (DEV-5228) ([#1895](https://github.com/dasch-swiss/dsp-tools/issues/1895)) ([830836c](https://github.com/dasch-swiss/dsp-tools/commit/830836c8d0d7d9d5988d4907630fe2fbd88e87b8))
* **create:** add support for classes/property specific default permissions (DOAPs) (DEV-5038) ([#1900](https://github.com/dasch-swiss/dsp-tools/issues/1900)) ([653498e](https://github.com/dasch-swiss/dsp-tools/commit/653498e1092d847c0fa7bfdd05c5790bedb55faa))
* **xmllib:** add deprecation warning to `create_list_from_string` (DEV-5252) ([#1909](https://github.com/dasch-swiss/dsp-tools/issues/1909)) ([9df7b9d](https://github.com/dasch-swiss/dsp-tools/commit/9df7b9d39dfd164139b9075b72dabd4769aec544))
* **xmllib:** helper function create list if the input is non-empty (DEV-5249) ([#1906](https://github.com/dasch-swiss/dsp-tools/issues/1906)) ([6bc7aa4](https://github.com/dasch-swiss/dsp-tools/commit/6bc7aa4c0c47d8ad7877428d3f39c0df63c5ef85))
* **xmllib:** level of user info that is printed configurable in the `.env` (DEV-5254) ([#1910](https://github.com/dasch-swiss/dsp-tools/issues/1910)) ([b261276](https://github.com/dasch-swiss/dsp-tools/commit/b2612766837c8bd603430f6a188078927a5d4e8a))


### Bug Fixes

* **upload-files:** enable extension ".json" (was forgotten) ([#1899](https://github.com/dasch-swiss/dsp-tools/issues/1899)) ([86017ee](https://github.com/dasch-swiss/dsp-tools/commit/86017ee0047e240bf33e54de95671a69c959f3a8))
* **xmllib:** don't crash if the listnode lookup does not find a label with the specified language (DEV-5247) ([#1902](https://github.com/dasch-swiss/dsp-tools/issues/1902)) ([583d273](https://github.com/dasch-swiss/dsp-tools/commit/583d2738151306dcc58809db1b90eeee20620ef8))
* **xmllib:** make the function `create_list_from_input` importable (DEV-5250) ([#1908](https://github.com/dasch-swiss/dsp-tools/issues/1908)) ([53ba941](https://github.com/dasch-swiss/dsp-tools/commit/53ba9419270ab06cd79a6ca92d5d98a13bd52438))


### Maintenance

* bump dependencies ([#1912](https://github.com/dasch-swiss/dsp-tools/issues/1912)) ([377555f](https://github.com/dasch-swiss/dsp-tools/commit/377555fd47bd947d2d3092762f93fd51fa4ecaa2))
* **excel2json:** add CLAUDE.md ([#1914](https://github.com/dasch-swiss/dsp-tools/issues/1914)) ([8fe0e85](https://github.com/dasch-swiss/dsp-tools/commit/8fe0e857a437266f51ab6c12e3eeed7f13f98802))
* **start-stack:** bump versions to 2025.08.02 ([#1916](https://github.com/dasch-swiss/dsp-tools/issues/1916)) ([2957bd1](https://github.com/dasch-swiss/dsp-tools/commit/2957bd1b3f838047d9710591a7646def59b734b2))
* **xmlupload:** generate CLAUDE.md file (DEV-5204) ([#1893](https://github.com/dasch-swiss/dsp-tools/issues/1893)) ([1b089b5](https://github.com/dasch-swiss/dsp-tools/commit/1b089b553108e5238de9770b42f15d4e8bd25499))

## [16.6.1](https://github.com/dasch-swiss/dsp-tools/compare/v16.6.0...v16.6.1) (2025-08-06)


### Maintenance

* bump start-stack to 2025.08.01 ([#1897](https://github.com/dasch-swiss/dsp-tools/issues/1897)) ([24ab2d9](https://github.com/dasch-swiss/dsp-tools/commit/24ab2d9348f436b1a89088440cdfc33f97cbc578))

## [16.6.0](https://github.com/dasch-swiss/dsp-tools/compare/v16.5.0...v16.6.0) (2025-07-30)


### Enhancements

* **create:** allow only subclasses of StillImageRepresentation in default_permissions_overrule.limited_view (DEV-5179) ([#1881](https://github.com/dasch-swiss/dsp-tools/issues/1881)) ([67d1b46](https://github.com/dasch-swiss/dsp-tools/commit/67d1b46eb93ad0c895b3fbd336881c2ddce1ef3f))
* **validate-data:** add flag to ignore ontology validation (DEV-5200) ([#1892](https://github.com/dasch-swiss/dsp-tools/issues/1892)) ([1ee25c4](https://github.com/dasch-swiss/dsp-tools/commit/1ee25c4dc069f5972faaf187da30e205035a8974))
* **validate-data:** include standoff links to IRIs in validation (DEV-4944) ([#1888](https://github.com/dasch-swiss/dsp-tools/issues/1888)) ([f6aba7c](https://github.com/dasch-swiss/dsp-tools/commit/f6aba7c00423d3e650e1e74e9cb20ed848eb2412))


### Maintenance

* bump start-stack to 2025.07.05 ([#1896](https://github.com/dasch-swiss/dsp-tools/issues/1896)) ([fcd7a6b](https://github.com/dasch-swiss/dsp-tools/commit/fcd7a6b8e7471228591d120d08629a94f155ebe6))
* **validate-data:** separate queries and reformatting of validation results ([#1894](https://github.com/dasch-swiss/dsp-tools/issues/1894)) ([1feaf55](https://github.com/dasch-swiss/dsp-tools/commit/1feaf555427bc19f96fa86d19d3f5b06914d3766))


### Documentation

* **bulk ingest:** remove "experimental" warning, add "SystemAdmin" warning ([#1889](https://github.com/dasch-swiss/dsp-tools/issues/1889)) ([323a27e](https://github.com/dasch-swiss/dsp-tools/commit/323a27e804a2ee567a111a21aa7eaeb509efe1eb))

## [16.5.0](https://github.com/dasch-swiss/dsp-tools/compare/v16.4.0...v16.5.0) (2025-07-23)


### Enhancements

* improve message if file path from user is not found (DEV-5171) ([#1874](https://github.com/dasch-swiss/dsp-tools/issues/1874)) ([3c6cfe5](https://github.com/dasch-swiss/dsp-tools/commit/3c6cfe5821540b27853548c257e128d2e7d2a39b))
* **validate-data:** Create CLAUDE.md (DEV-5107) ([#1829](https://github.com/dasch-swiss/dsp-tools/issues/1829)) ([405c8ae](https://github.com/dasch-swiss/dsp-tools/commit/405c8ae47e670454c3bee1ffa8553ae4dd03c807))
* **validate-data:** ensure that the end date is equal or after the start date (DEV-5173) ([#1879](https://github.com/dasch-swiss/dsp-tools/issues/1879)) ([db32e38](https://github.com/dasch-swiss/dsp-tools/commit/db32e382ac62c28b2737c08ddbd72b29f06aa263))
* **validate-data:** ensure that the end date is not `BCE` when the start date is `CE` (DEV-5176) ([#1878](https://github.com/dasch-swiss/dsp-tools/issues/1878)) ([6f9b136](https://github.com/dasch-swiss/dsp-tools/commit/6f9b1363e49a69d20839f3ef95439c3f482b4e51))
* **validate-data:** find dates that have an invalid month or year number (DEV-5175) ([#1876](https://github.com/dasch-swiss/dsp-tools/issues/1876)) ([66ec5ce](https://github.com/dasch-swiss/dsp-tools/commit/66ec5ce4b08610466ac277789d24d4a5d8f2d881))
* **validate-data:** improve user message if the file value is wrong (DEV-5122) ([#1873](https://github.com/dasch-swiss/dsp-tools/issues/1873)) ([758d323](https://github.com/dasch-swiss/dsp-tools/commit/758d323735d78db588ea7db0aa75bd623f7a3bda))
* **validate-data:** parse DateValue into xsd compatible date datatypes (DEV-5172) ([#1875](https://github.com/dasch-swiss/dsp-tools/issues/1875)) ([7f7f42e](https://github.com/dasch-swiss/dsp-tools/commit/7f7f42e4177c461a977831b3842f52d4d5f96308))
* **validate-data:** raise validation severity of duplicate files from `INFO` to `WARNING` (DEV-5167) ([#1868](https://github.com/dasch-swiss/dsp-tools/issues/1868)) ([e36893d](https://github.com/dasch-swiss/dsp-tools/commit/e36893d648f7a3fb233ed17d3d8b4bb2491d4885))


### Bug Fixes

* **ingest-files:** save latest mapping without timestamp (DEV-5163) ([#1866](https://github.com/dasch-swiss/dsp-tools/issues/1866)) ([66a78ba](https://github.com/dasch-swiss/dsp-tools/commit/66a78babe387138c77966b2bab6a5955020e7adf))
* **start-stack:** don't crash if `stop-stack` is called multiple times ([#1884](https://github.com/dasch-swiss/dsp-tools/issues/1884)) ([e638620](https://github.com/dasch-swiss/dsp-tools/commit/e638620750384aca0966107cb417de0afeec995c))
* **validate-data:** turn all dates into full dates for validation to allow for comparison (DEV-5180) ([#1880](https://github.com/dasch-swiss/dsp-tools/issues/1880)) ([7c64869](https://github.com/dasch-swiss/dsp-tools/commit/7c6486924b7d7e76d82276a0ede470a6ebf36d03))
* **xmlupload:** use slightly shorter timeout than traefik's 10 min ([#1883](https://github.com/dasch-swiss/dsp-tools/issues/1883)) ([f78cc2f](https://github.com/dasch-swiss/dsp-tools/commit/f78cc2fe768304b4f02bfe80c80da3ccb1dea34a))


### Maintenance

* bump start-stack to 2025.07.04 ([#1887](https://github.com/dasch-swiss/dsp-tools/issues/1887)) ([e0815a8](https://github.com/dasch-swiss/dsp-tools/commit/e0815a81c05ab58fa7e196c4bd95ce31f501b2da))
* make dependabot functional again ([#1855](https://github.com/dasch-swiss/dsp-tools/issues/1855)) ([9dec12a](https://github.com/dasch-swiss/dsp-tools/commit/9dec12a71980148d309cbc52dedef310ca7f9b6e))
* run e2e tests in parallel ([#1882](https://github.com/dasch-swiss/dsp-tools/issues/1882)) ([e81520c](https://github.com/dasch-swiss/dsp-tools/commit/e81520cab0d0a5517af664fa2dd7bd521920e2df))
* **validate-data:** always check for duplicates with python logic (DEV-5158) ([#1856](https://github.com/dasch-swiss/dsp-tools/issues/1856)) ([3d33663](https://github.com/dasch-swiss/dsp-tools/commit/3d336632ee5cda4e8440c15f0a85b185e227bf31))
* **validate-data:** delete unnecessary code to filter out multiple duplicate file warnings (DEV-5168) ([#1872](https://github.com/dasch-swiss/dsp-tools/issues/1872)) ([1abd25b](https://github.com/dasch-swiss/dsp-tools/commit/1abd25b894e3233b646af850c5fe4bd06fff1b28))
* **validate-data:** remove unnecessary file duplicate reformatting (DEV-5159) ([#1869](https://github.com/dasch-swiss/dsp-tools/issues/1869)) ([72d8734](https://github.com/dasch-swiss/dsp-tools/commit/72d8734cd6a3d346a0494817aaa86e9fdb16adb3))
* **validate-data:** remove unused turtle files for duplicate check (DEV-5164) ([#1870](https://github.com/dasch-swiss/dsp-tools/issues/1870)) ([5b26b7e](https://github.com/dasch-swiss/dsp-tools/commit/5b26b7e4a266f0fc9e8dd4ab6282a5223ddb5120))
* **xmllib:** create designated `xmllib` error classes (DEV-5098) ([#1865](https://github.com/dasch-swiss/dsp-tools/issues/1865)) ([5620780](https://github.com/dasch-swiss/dsp-tools/commit/562078078dd7a9c8bcf7c63c7677363e38921d41))

## [16.4.0](https://github.com/dasch-swiss/dsp-tools/compare/v16.3.0...v16.4.0) (2025-07-16)


### Enhancements

* **validate-data:** consistently save or print validation results based on total number found (DEV-5135) ([#1848](https://github.com/dasch-swiss/dsp-tools/issues/1848)) ([ef37b87](https://github.com/dasch-swiss/dsp-tools/commit/ef37b874d28004c77ac2d0161fd275653213f480))
* **validate-data:** eable multiple parallel calls at the same time without conflicts (DEV-5137) ([#1836](https://github.com/dasch-swiss/dsp-tools/issues/1836)) ([26a4599](https://github.com/dasch-swiss/dsp-tools/commit/26a45999d769ff5c16c009381a9c206603a0c58a))
* **validate-data:** prevent crash if too many duplicate files are in the data (DEV-5140) ([#1841](https://github.com/dasch-swiss/dsp-tools/issues/1841)) ([4bf4fa0](https://github.com/dasch-swiss/dsp-tools/commit/4bf4fa06d3612750f5dba913adde61d4c800fa45))
* **validate-data:** use the SHACL CLI for all validation calls (DEV-5127) ([#1831](https://github.com/dasch-swiss/dsp-tools/issues/1831)) ([687adfe](https://github.com/dasch-swiss/dsp-tools/commit/687adfec6693dc43e1ae02ccc91032977f1da268))
* **xmlupload:** always write id2iri to ".dsp-tools" folder (DEV-5162) ([#1862](https://github.com/dasch-swiss/dsp-tools/issues/1862)) ([08b050b](https://github.com/dasch-swiss/dsp-tools/commit/08b050ba021f69668ce1be96e1a7cc55f51f60d3))


### Maintenance

* align folder naming of ingest docker folders with naming on servers ([#1849](https://github.com/dasch-swiss/dsp-tools/issues/1849)) ([1f0cdd4](https://github.com/dasch-swiss/dsp-tools/commit/1f0cdd4420e812a5e0b143c35aa85f051ddc2553))
* bump start-stack to 2025.07.03 ([#1864](https://github.com/dasch-swiss/dsp-tools/issues/1864)) ([71f1f28](https://github.com/dasch-swiss/dsp-tools/commit/71f1f2873f16e6161713933b32876e3599a26bd8))
* reorganise GitHub workflow files (DEV-5154) ([#1851](https://github.com/dasch-swiss/dsp-tools/issues/1851)) ([8a3fa56](https://github.com/dasch-swiss/dsp-tools/commit/8a3fa56fa1ba1dddfe0231d0fc2d286aa8af7367))
* **validate-data:** allow `InputProblems` without resource ID and type ([#1857](https://github.com/dasch-swiss/dsp-tools/issues/1857)) ([10a462c](https://github.com/dasch-swiss/dsp-tools/commit/10a462cb4d7fafddc5a39d8b152d1f45cef1ba30))
* **validate-data:** create `validation` folder ([#1843](https://github.com/dasch-swiss/dsp-tools/issues/1843)) ([ae24254](https://github.com/dasch-swiss/dsp-tools/commit/ae2425409cb89a42a46c8e078d425189703953d8))
* **validate-data:** group files into categories ([#1837](https://github.com/dasch-swiss/dsp-tools/issues/1837)) ([00f6ade](https://github.com/dasch-swiss/dsp-tools/commit/00f6adef00218f80ab1d1218dd8b3386708e4a5b))
* **validate-data:** improve edge cases e2e tests ([#1859](https://github.com/dasch-swiss/dsp-tools/issues/1859)) ([d23e389](https://github.com/dasch-swiss/dsp-tools/commit/d23e389394cd3e11266fda075421d292b2b643d2))
* **validate-data:** improve generic violations e2e tests ([#1860](https://github.com/dasch-swiss/dsp-tools/issues/1860)) ([df78c39](https://github.com/dasch-swiss/dsp-tools/commit/df78c391c6ef0f329545dfcdc183bed5a1a1a7f5))
* **validate-data:** improve warnings and info e2e tests ([#1861](https://github.com/dasch-swiss/dsp-tools/issues/1861)) ([d8e80f1](https://github.com/dasch-swiss/dsp-tools/commit/d8e80f1520821ff2cb1260bf9cc68b05186d13d3))
* **validate-data:** move check for unknown resources classes to own file ([#1844](https://github.com/dasch-swiss/dsp-tools/issues/1844)) ([1b15119](https://github.com/dasch-swiss/dsp-tools/commit/1b151199454786c29899b3bccb7fb025cce5a454))
* **validate-data:** move get ontology validation message to correct file ([#1845](https://github.com/dasch-swiss/dsp-tools/issues/1845)) ([bd1eb96](https://github.com/dasch-swiss/dsp-tools/commit/bd1eb96ed538a42742fc9ef032fd39db3c2282be))
* **validate-data:** move get validation report to own file ([#1846](https://github.com/dasch-swiss/dsp-tools/issues/1846)) ([7669828](https://github.com/dasch-swiss/dsp-tools/commit/766982849b0bfd247974f2f1d3831bb2c06ec929))
* **validate-data:** only use `pytest.fixtures` in e2e tests when needed ([#1863](https://github.com/dasch-swiss/dsp-tools/issues/1863)) ([77f924f](https://github.com/dasch-swiss/dsp-tools/commit/77f924fe66796ea2fcd97ca7f90ce92e74ca6017))
* **validate-data:** read shacl-cli docker image from file ([#1850](https://github.com/dasch-swiss/dsp-tools/issues/1850)) ([4c4daf2](https://github.com/dasch-swiss/dsp-tools/commit/4c4daf29a959aaaa7417b9a864f15d2eccab24a3))
* **validate-data:** remove unused parameter `asset_value` from `RdfLikeResource` ([#1839](https://github.com/dasch-swiss/dsp-tools/issues/1839)) ([a2dc2d4](https://github.com/dasch-swiss/dsp-tools/commit/a2dc2d40486f814d45c71a0521b786d57966c968))
* **validate-data:** restructure function calls internally ([#1840](https://github.com/dasch-swiss/dsp-tools/issues/1840)) ([8a9847c](https://github.com/dasch-swiss/dsp-tools/commit/8a9847caaa219fb18ea6e47f987cb913170e5f5f))
* **validate-data:** separate printing of messages and creating the validation result ([#1858](https://github.com/dasch-swiss/dsp-tools/issues/1858)) ([a80596f](https://github.com/dasch-swiss/dsp-tools/commit/a80596f4017ced5a42ae89dcdeb01f5f4b342f13))


### Documentation

* **validate-data:** add validation logic diagram to developers' docs ([#1847](https://github.com/dasch-swiss/dsp-tools/issues/1847)) ([6cd508a](https://github.com/dasch-swiss/dsp-tools/commit/6cd508a00c90ecd49e83683feea58c00ff3267ad))

## [16.3.0](https://github.com/dasch-swiss/dsp-tools/compare/v16.2.0...v16.3.0) (2025-07-09)


### Enhancements

* **get:** retrieve default permissions (DEV-5076) ([#1825](https://github.com/dasch-swiss/dsp-tools/issues/1825)) ([4414149](https://github.com/dasch-swiss/dsp-tools/commit/4414149357270c73ba5129e17ccd7cf9e2b7d084))
* **validate-data:** run validation locally with a docker container (DEV-5062) ([#1827](https://github.com/dasch-swiss/dsp-tools/issues/1827)) ([343bfda](https://github.com/dasch-swiss/dsp-tools/commit/343bfda799a33633fb7894d82a6db6d9c62152b5))
* **xmllib:** prevent conversion of null values into strings (DEV-5117) ([#1822](https://github.com/dasch-swiss/dsp-tools/issues/1822)) ([877af93](https://github.com/dasch-swiss/dsp-tools/commit/877af93879e38b316aa53d97af3b09b03062c06d))
* **xmllib:** remove functionality to set default permissions on `write_file` (DEV-5105) ([#1823](https://github.com/dasch-swiss/dsp-tools/issues/1823)) ([c44fb5c](https://github.com/dasch-swiss/dsp-tools/commit/c44fb5ccdb96a62e598407789c5be05da86cbe8d))
* **xmllib:** rename permissions open/restricted/restricted view to public/private/limited_view (DEV-5079) ([#1820](https://github.com/dasch-swiss/dsp-tools/issues/1820)) ([569e2bf](https://github.com/dasch-swiss/dsp-tools/commit/569e2bff84eb89728df0558ce3150ba7688b3ac2))


### Bug Fixes

* allow hexadecimal letters in resource iri check (DEV-5118) ([#1824](https://github.com/dasch-swiss/dsp-tools/issues/1824)) ([2f90826](https://github.com/dasch-swiss/dsp-tools/commit/2f9082673e2351f3a0fd7a5d5c63c919bedbe956))
* **xmllib:** remove duplicate warning if an empty value is added in Simpletext (DEV-5121) ([#1826](https://github.com/dasch-swiss/dsp-tools/issues/1826)) ([78c2618](https://github.com/dasch-swiss/dsp-tools/commit/78c2618aa966e7d1a198056570d26f6cac420258))


### Maintenance

* bump start-stack to 2025.07.02 ([#1833](https://github.com/dasch-swiss/dsp-tools/issues/1833)) ([b86ad3a](https://github.com/dasch-swiss/dsp-tools/commit/b86ad3a046ee0d9a914f45416030af6c7a886807))
* update CLAUDE.md ([#1819](https://github.com/dasch-swiss/dsp-tools/issues/1819)) ([23b1cf8](https://github.com/dasch-swiss/dsp-tools/commit/23b1cf8161678d15f3926aa9ce696cebc7283297))
* **xmllib:** add CLAUDE.md file for xmllib (DEV-5097) ([#1815](https://github.com/dasch-swiss/dsp-tools/issues/1815)) ([58eadeb](https://github.com/dasch-swiss/dsp-tools/commit/58eadebbc05e740d9513b28f1d7a7f4cd2ab456c))


### Documentation

* **create:** add `default_permissions_overrule` to test data, docs, and JSON schema (DEV-5031) ([#1828](https://github.com/dasch-swiss/dsp-tools/issues/1828)) ([ebfaf60](https://github.com/dasch-swiss/dsp-tools/commit/ebfaf609bd3313ea051846ea8c49f7cb5a9e2350))

## [16.2.0](https://github.com/dasch-swiss/dsp-tools/compare/v16.1.0...v16.2.0) (2025-07-02)


### Enhancements

* **create:** rename "project_default_permissions" to "default_permissions" (DEV-5091) ([#1811](https://github.com/dasch-swiss/dsp-tools/issues/1811)) ([32e4b2d](https://github.com/dasch-swiss/dsp-tools/commit/32e4b2d54dd2cd68dae53b853df9063aaef8d85d))
* **excel2json:** set project default permissions in Excel (DEV-5036) ([#1808](https://github.com/dasch-swiss/dsp-tools/issues/1808)) ([ffcdf8e](https://github.com/dasch-swiss/dsp-tools/commit/ffcdf8e1847d5d2be087aa58b50e2df7d9f1b14f))
* remove default for project_default_permissions (DEV-5087) ([#1806](https://github.com/dasch-swiss/dsp-tools/issues/1806)) ([576b147](https://github.com/dasch-swiss/dsp-tools/commit/576b1472c39e35cdbf4c088692ad6fe9f9213e16))


### Bug Fixes

* remove dataclass decorator from enum class (DEV-5073) ([#1818](https://github.com/dasch-swiss/dsp-tools/issues/1818)) ([1768840](https://github.com/dasch-swiss/dsp-tools/commit/176884037a7300972bad443bcf184e47a2a202ad))
* **start-stack:** prevent sipi data from filling up storage (DEV-5065) ([#1810](https://github.com/dasch-swiss/dsp-tools/issues/1810)) ([5bc0e80](https://github.com/dasch-swiss/dsp-tools/commit/5bc0e80dfa76c6315f22b33f272c9a08924e4896))
* **validate-data:** allow stand-off links for resources (DEV-5101) ([#1816](https://github.com/dasch-swiss/dsp-tools/issues/1816)) ([6ad6f0e](https://github.com/dasch-swiss/dsp-tools/commit/6ad6f0ecef7f003bdf11c3a51e229307f7395a1e))
* **xmlupload:** add more retries to account for 45 min and more fuseki compaction (DEV-5094) ([#1812](https://github.com/dasch-swiss/dsp-tools/issues/1812)) ([d716e08](https://github.com/dasch-swiss/dsp-tools/commit/d716e085fb44a87918eb095c59ae29cfef84f351))
* **xmlupload:** retry during ca. 15min (DEV-5089) ([#1809](https://github.com/dasch-swiss/dsp-tools/issues/1809)) ([0dd91a2](https://github.com/dasch-swiss/dsp-tools/commit/0dd91a23edc42580fc5fd8acc20911e38acd0f19))


### Maintenance

* bump start-stack to 2025.07.01 and remove api-config workaround (DEV-5106) ([#1817](https://github.com/dasch-swiss/dsp-tools/issues/1817)) ([a508526](https://github.com/dasch-swiss/dsp-tools/commit/a50852688098dc43d7e98d59798cdf7cf8c532fe))
* **start-stack:** subpar bind mount in docker-compose.yml (DEV-5096) ([#1813](https://github.com/dasch-swiss/dsp-tools/issues/1813)) ([bb030ac](https://github.com/dasch-swiss/dsp-tools/commit/bb030acf9bb69b6de064f83fb72a5b83c433b30c))


### Documentation

* **xmllib:** fix some mistakes in documentation of helpers and converters ([#1814](https://github.com/dasch-swiss/dsp-tools/issues/1814)) ([8093557](https://github.com/dasch-swiss/dsp-tools/commit/8093557cf189abe0e2bdfc802aa32cd0345fe807))

## [16.1.0](https://github.com/dasch-swiss/dsp-tools/compare/v16.0.0...v16.1.0) (2025-06-24)


### Enhancements

* **create:** set project default permissions in JSON (DEV-5035, DEV-5037) ([#1801](https://github.com/dasch-swiss/dsp-tools/issues/1801)) ([16fc473](https://github.com/dasch-swiss/dsp-tools/commit/16fc4738a5d97415fe7d8ca26397266b1dd80e0d))
* **xmlupload:** add support for HTML and EPUB files (DEV-5084) ([#1805](https://github.com/dasch-swiss/dsp-tools/issues/1805)) ([007f641](https://github.com/dasch-swiss/dsp-tools/commit/007f64148b839f8113b00fdab3c28c56cfcdd29e))


### Maintenance

* apply new permissions terminology - everywhere except xmllib (DEV-5077) ([#1804](https://github.com/dasch-swiss/dsp-tools/issues/1804)) ([ff0e1fa](https://github.com/dasch-swiss/dsp-tools/commit/ff0e1fa2cbe7e04f9cb50744b439837b8b9e60ef))
* bump dependencies ([#1799](https://github.com/dasch-swiss/dsp-tools/issues/1799)) ([bb99e6d](https://github.com/dasch-swiss/dsp-tools/commit/bb99e6d785d7596540a72b722db639fa515d8a93))


### Documentation

* **xmlupload:** reflect the new project default permissions (DEV-5078) ([#1803](https://github.com/dasch-swiss/dsp-tools/issues/1803)) ([0bb0037](https://github.com/dasch-swiss/dsp-tools/commit/0bb00373fd09b0e6d7195ddea415c30792a797fc))

## [16.0.0](https://github.com/dasch-swiss/dsp-tools/compare/v15.1.0...v16.0.0) (2025-06-18)


### ⚠ BREAKING CHANGES

* **create:** disallow creation of SystemAdmin (DEV-5009) ([#1787](https://github.com/dasch-swiss/dsp-tools/issues/1787))

### Enhancements

* allow that images are part of multiple compound objects (DEV-5070) ([#1796](https://github.com/dasch-swiss/dsp-tools/issues/1796)) ([70e6371](https://github.com/dasch-swiss/dsp-tools/commit/70e6371c04f3f1f08df228cd5fcbaec838e43dec))
* **create:** disallow creation of SystemAdmin (DEV-5009) ([#1787](https://github.com/dasch-swiss/dsp-tools/issues/1787)) ([08dac08](https://github.com/dasch-swiss/dsp-tools/commit/08dac08703b983d86d6f446fe07352842d4958b5))
* **create:** link existing users to project (DEV-5052) ([#1793](https://github.com/dasch-swiss/dsp-tools/issues/1793)) ([4ff19ae](https://github.com/dasch-swiss/dsp-tools/commit/4ff19ae06c05a0c584d450900f7ff6e7bc43f272))
* reformat and write large xsd schema validation results into a file (DEV-4998) ([#1775](https://github.com/dasch-swiss/dsp-tools/issues/1775)) ([b3ada62](https://github.com/dasch-swiss/dsp-tools/commit/b3ada62bf7cad7af0c9fe718f9cbb3fd951915e3))
* **validate-data:** add flag to ignore duplicate image warnings (DEV-5060) ([#1791](https://github.com/dasch-swiss/dsp-tools/issues/1791)) ([2d8a701](https://github.com/dasch-swiss/dsp-tools/commit/2d8a7013e3010e054a7a25bf2bdc6247c2f3e7ad))
* **validate-data:** don't shorten user input if it is a ListValue (DEV-5048) ([#1782](https://github.com/dasch-swiss/dsp-tools/issues/1782)) ([2bcd9d5](https://github.com/dasch-swiss/dsp-tools/commit/2bcd9d575848241c1231d69c9c9b1cf474b2180a))
* **validate-data:** print out longer user input in validation message and don't shorten if info if it is a link (DEV-5047) ([#1781](https://github.com/dasch-swiss/dsp-tools/issues/1781)) ([a4c94ef](https://github.com/dasch-swiss/dsp-tools/commit/a4c94efbdbdfd7319c6acb3ab36fb4c3e577106f))
* **xmllib:** add function to reformat dates from a known format (DEV-5054) ([#1786](https://github.com/dasch-swiss/dsp-tools/issues/1786)) ([3e6e596](https://github.com/dasch-swiss/dsp-tools/commit/3e6e5960664f22cab0bebf323e02eb79c3534dbb))
* **xmllib:** check if the Resource ID is already used when adding a new one to the `XmlRoot` (DEV-4997) ([#1785](https://github.com/dasch-swiss/dsp-tools/issues/1785)) ([748cc18](https://github.com/dasch-swiss/dsp-tools/commit/748cc183e4c43db1c792c81ed3046bef71050d74))
* **xmllib:** validate that the resource ids are correct (DEV-4996) ([#1780](https://github.com/dasch-swiss/dsp-tools/issues/1780)) ([c0e938e](https://github.com/dasch-swiss/dsp-tools/commit/c0e938eda55c3f22399ada149684515c2563c062))
* **xmlupload:** add flag to skip SHACL validation (DEV-5058) ([#1790](https://github.com/dasch-swiss/dsp-tools/issues/1790)) ([a24cb0e](https://github.com/dasch-swiss/dsp-tools/commit/a24cb0e2901cfc9c756164050dcab55220465183))


### Bug Fixes

* **validate-data:** prevent the same prefix to be used for different IRIs in the serialisation (DEV-5053) ([#1784](https://github.com/dasch-swiss/dsp-tools/issues/1784)) ([f21688a](https://github.com/dasch-swiss/dsp-tools/commit/f21688a6bcd7f386da409ee933ac399be8f9cec8))
* **validate-data:** set higher timeouts for operations that could last long - 360s (DEV-5049) ([#1788](https://github.com/dasch-swiss/dsp-tools/issues/1788)) ([65edb79](https://github.com/dasch-swiss/dsp-tools/commit/65edb79a2d6c2801be8b030543cb12c2409572f6))
* **validate-data:** set higher timeouts for operations that could last long (DEV-5049) ([#1783](https://github.com/dasch-swiss/dsp-tools/issues/1783)) ([03a24cd](https://github.com/dasch-swiss/dsp-tools/commit/03a24cdc56ec07ccc7455d49a74c580f1937523f))
* **xmllib:** don't warn if the list name is empty if the node is an absolute iri (DEV-5019) ([#1774](https://github.com/dasch-swiss/dsp-tools/issues/1774)) ([b5fb167](https://github.com/dasch-swiss/dsp-tools/commit/b5fb1672ce3cd949286324b15fdb19b4a76b1d5a))
* **xmllib:** remove duplicate warnings for empty input when creating a new `Resource` (DEV-5057) ([#1789](https://github.com/dasch-swiss/dsp-tools/issues/1789)) ([57e0431](https://github.com/dasch-swiss/dsp-tools/commit/57e0431a460152700534508dceff62b7dae2dd65))
* **xmlupload:** allow more special characters ([#1794](https://github.com/dasch-swiss/dsp-tools/issues/1794)) ([f245f80](https://github.com/dasch-swiss/dsp-tools/commit/f245f8029fe19a925572e2067c2616df31271772))


### Maintenance

* add CLAUDE.md to fine-tune Claude Code instances ([#1792](https://github.com/dasch-swiss/dsp-tools/issues/1792)) ([cc4f9c7](https://github.com/dasch-swiss/dsp-tools/commit/cc4f9c72a13c8de404e407759a580c5a1b70f61d))
* bump start-stack to 2025.06.02 ([#1795](https://github.com/dasch-swiss/dsp-tools/issues/1795)) ([41b21d9](https://github.com/dasch-swiss/dsp-tools/commit/41b21d994cffacd94a5e7988ec83bc646ad4ecfe))
* **start-stack:** add more logging ([#1777](https://github.com/dasch-swiss/dsp-tools/issues/1777)) ([4eacc50](https://github.com/dasch-swiss/dsp-tools/commit/4eacc503a5c34c9fc3e2fe8c27741f2baf57a6f9))
* **start-stack:** add more logging (DEV-5071) ([#1797](https://github.com/dasch-swiss/dsp-tools/issues/1797)) ([19c2092](https://github.com/dasch-swiss/dsp-tools/commit/19c20926a60b0b013993c3f51e6f73b78fee9614))
* **start-stack:** capture and log API logs in case of failure (DEV-5071) ([#1798](https://github.com/dasch-swiss/dsp-tools/issues/1798)) ([36dff9f](https://github.com/dasch-swiss/dsp-tools/commit/36dff9f902c3a54d5d56d035c69e3a0124e89b29))
* **validate-data:** remove erroneous logging statement ([#1778](https://github.com/dasch-swiss/dsp-tools/issues/1778)) ([dcc312c](https://github.com/dasch-swiss/dsp-tools/commit/dcc312c8fd0678118a2214c2385bfde0270e7d7d))

## [15.1.0](https://github.com/dasch-swiss/dsp-tools/compare/v15.0.0...v15.1.0) (2025-06-04)


### Enhancements

* **create:** enable licenses on a per-project base (DEV-4864) ([#1744](https://github.com/dasch-swiss/dsp-tools/issues/1744)) ([27004a6](https://github.com/dasch-swiss/dsp-tools/commit/27004a6a4054e964e4fe5f663a1f7fb3c1bb1ed9))
* migrate warning about angular brackets in simpletext from `xmplupload` to `xmllib` (DEV-4943) ([#1750](https://github.com/dasch-swiss/dsp-tools/issues/1750)) ([c48d041](https://github.com/dasch-swiss/dsp-tools/commit/c48d041d3882977d4fa56cefe85cdaa3dac5f03f))
* **validate-data:** add more logging statements to find out slow process (DEV-4977) ([#1763](https://github.com/dasch-swiss/dsp-tools/issues/1763)) ([cad440c](https://github.com/dasch-swiss/dsp-tools/commit/cad440cdc58cae9993cfc5c3a515687dd65ae60e))
* **validate-data:** check that only enabled licenses are referenced in the xml (DEV-4951) ([#1755](https://github.com/dasch-swiss/dsp-tools/issues/1755)) ([dd42602](https://github.com/dasch-swiss/dsp-tools/commit/dd426026c97e8c86d5d9f1ef629708808c212215))
* **validate-data:** don't shorten user input in print out if it is a file paht (DEV-5008) ([#1769](https://github.com/dasch-swiss/dsp-tools/issues/1769)) ([208b049](https://github.com/dasch-swiss/dsp-tools/commit/208b04903d3cf1918cdf0d4ee52abca19d5a9d7a))
* **validate-data:** ensure that only defined permissions are used (DEV-4939) ([#1748](https://github.com/dasch-swiss/dsp-tools/issues/1748)) ([8009778](https://github.com/dasch-swiss/dsp-tools/commit/8009778ad508bdd7f36a340aa654feb23b94f642))
* **validate-data:** serialise the `rdflib` graphs into strings before concatenation with other graphs (DEV-5001) ([#1768](https://github.com/dasch-swiss/dsp-tools/issues/1768)) ([ea8ead7](https://github.com/dasch-swiss/dsp-tools/commit/ea8ead7b7018ddbc3d9276b2b7fd46fe25164a7f))
* **validate-data:** warn if bitstreams/iiif-uri are duplicated (DEV-4665) ([#1752](https://github.com/dasch-swiss/dsp-tools/issues/1752)) ([741223c](https://github.com/dasch-swiss/dsp-tools/commit/741223c7157f72d36d01ce240e59f3dd7c3e4280))
* **validate-data:** warnings give a validation failure if it is on a prod server (DEV-4948) ([#1754](https://github.com/dasch-swiss/dsp-tools/issues/1754)) ([a8006fb](https://github.com/dasch-swiss/dsp-tools/commit/a8006fbadcb4093a8bf5570f03efc850fdeaaf15))
* **xmllib:** accept Italian "sì" as boolean (RDU-94) ([#1746](https://github.com/dasch-swiss/dsp-tools/issues/1746)) ([322fa00](https://github.com/dasch-swiss/dsp-tools/commit/322fa002783635dc09d06046a07c6131078c0e11))
* **xmllib:** don't print out warnings if they are saved into a csv (DEV-5011) ([#1772](https://github.com/dasch-swiss/dsp-tools/issues/1772)) ([bec6807](https://github.com/dasch-swiss/dsp-tools/commit/bec68077cad08ebdc954968b3288e947dc177264))
* **xmlupload:** add dummy legal info when none provided and not on prod server (DEV-4926) ([#1757](https://github.com/dasch-swiss/dsp-tools/issues/1757)) ([17a7fd0](https://github.com/dasch-swiss/dsp-tools/commit/17a7fd01b29226b1036caae47f508bf501c672cc))
* **xmlupload:** show progress bar on CLI when uploading stash (DEV-4935) ([#1747](https://github.com/dasch-swiss/dsp-tools/issues/1747)) ([7fd490c](https://github.com/dasch-swiss/dsp-tools/commit/7fd490c0709d972c5eb75e5c5785da5d5b1db440))
* xsd file should validate that a `<resptr>` only contains valid characters (DEV-4999) ([#1771](https://github.com/dasch-swiss/dsp-tools/issues/1771)) ([452c4bc](https://github.com/dasch-swiss/dsp-tools/commit/452c4bc47ee075d8e22d34b6b4ab48e04e66909b))


### Bug Fixes

* remove erroneous mandatory gui attribute of `Spinbox` (DEV-4679) ([#1764](https://github.com/dasch-swiss/dsp-tools/issues/1764)) ([fecfabf](https://github.com/dasch-swiss/dsp-tools/commit/fecfabff5adb06bdd4c91573eb7f024186193e6f))
* **validate-data:** add missing API URLs to the list of production servers (DEV-4995) ([#1767](https://github.com/dasch-swiss/dsp-tools/issues/1767)) ([b3ebb95](https://github.com/dasch-swiss/dsp-tools/commit/b3ebb953bca3a2d3342ac906ed1d7abce50b2dfb))
* **validate-data:** validate with list IRIs instead of names (DEV-4470) ([#1741](https://github.com/dasch-swiss/dsp-tools/issues/1741)) ([678164f](https://github.com/dasch-swiss/dsp-tools/commit/678164f1c68320bf51e2e42353d2b57a3c681827))


### Maintenance

* describe yamlfmt installation in readme and bump markdownlint version ([#1753](https://github.com/dasch-swiss/dsp-tools/issues/1753)) ([b3a712f](https://github.com/dasch-swiss/dsp-tools/commit/b3a712f6eda78f96b7d0b9b6ead21027db34fef0))
* improve boolean arguments ([#1765](https://github.com/dasch-swiss/dsp-tools/issues/1765)) ([e97c0aa](https://github.com/dasch-swiss/dsp-tools/commit/e97c0aac67818660fd9ad6976b9533c9a6889692))
* **start-stack:** bump versions to 2025.06.01 ([#1773](https://github.com/dasch-swiss/dsp-tools/issues/1773)) ([6f1f38a](https://github.com/dasch-swiss/dsp-tools/commit/6f1f38a8e9cde4e657f5eebfa46a4e519961d9cf))
* **validate-data:** change list node extraction ([#1742](https://github.com/dasch-swiss/dsp-tools/issues/1742)) ([83fdd6d](https://github.com/dasch-swiss/dsp-tools/commit/83fdd6d79ad590f8e1690023182e96685ed5fb6f))
* **xmlupload:** change processing of `ParsedFileValue` ([#1758](https://github.com/dasch-swiss/dsp-tools/issues/1758)) ([92c8abd](https://github.com/dasch-swiss/dsp-tools/commit/92c8abdc7a04f2cd0bbd4cac7851addf079f54b5))
* **xmlupload:** clean up RDF creation of legal info (DEV-4959) ([#1766](https://github.com/dasch-swiss/dsp-tools/issues/1766)) ([9d4fcb4](https://github.com/dasch-swiss/dsp-tools/commit/9d4fcb4f7ce3c05bcfc748a1668493e873ff3a2b))
* **xmlupload:** remove redundant check if link targets exist (DEV-4942) ([#1751](https://github.com/dasch-swiss/dsp-tools/issues/1751)) ([e7cee5b](https://github.com/dasch-swiss/dsp-tools/commit/e7cee5b3ac071c5bb1cae361a8b46ed3d5388f66))
* **xmlupload:** remove unnecessary conversion checks (DEV-4934) ([#1745](https://github.com/dasch-swiss/dsp-tools/issues/1745)) ([cea1509](https://github.com/dasch-swiss/dsp-tools/commit/cea1509f620032e19b3188a013024ec2dba15812))
* **xmlupload:** remove unnecessary permissions error handling (DEV-4940) ([#1749](https://github.com/dasch-swiss/dsp-tools/issues/1749)) ([0fabaf2](https://github.com/dasch-swiss/dsp-tools/commit/0fabaf2e425ce71a19428810bc36af70d484a1b0))


### Documentation

* add explanation of `TextValue` types (DEV-5013) ([#1770](https://github.com/dasch-swiss/dsp-tools/issues/1770)) ([1f830fa](https://github.com/dasch-swiss/dsp-tools/commit/1f830fa4c1a9ecaddacc963fb280f8c648dc623c))

## [15.0.0](https://github.com/dasch-swiss/dsp-tools/compare/v14.0.0...v15.0.0) (2025-05-21)


### ⚠ BREAKING CHANGES

* rename find_date_in_string() to find_dates_in_string() (RDU-93) ([#1738](https://github.com/dasch-swiss/dsp-tools/issues/1738))
* find_date_in_string() returns list[str] instead of Optional[str] (DEV-4900) ([#1733](https://github.com/dasch-swiss/dsp-tools/issues/1733))

### Enhancements

* find_date_in_string() returns list[str] instead of Optional[str] (DEV-4900) ([#1733](https://github.com/dasch-swiss/dsp-tools/issues/1733)) ([53c7d75](https://github.com/dasch-swiss/dsp-tools/commit/53c7d7531b6f08d5b409ba10c078182c1ab32bb2))
* rename find_date_in_string() to find_dates_in_string() (RDU-93) ([#1738](https://github.com/dasch-swiss/dsp-tools/issues/1738)) ([05c99b1](https://github.com/dasch-swiss/dsp-tools/commit/05c99b11d2d38125971d69dee77fd7a9950675f0))
* retrieve licenses of project and add authentication to validate-data (DEV-4906) ([#1725](https://github.com/dasch-swiss/dsp-tools/issues/1725)) ([fc17405](https://github.com/dasch-swiss/dsp-tools/commit/fc174055a9fa19dd1c15bdd31c7602895e08cca2))
* **start-stack:** add parameter for a custom host (DEV-4907) ([#1675](https://github.com/dasch-swiss/dsp-tools/issues/1675)) ([ea3a89e](https://github.com/dasch-swiss/dsp-tools/commit/ea3a89e235b8207874a315a748928216ca713a9c))
* **validate-data:** validate that only existing licenses are used (DEV-4862) ([#1729](https://github.com/dasch-swiss/dsp-tools/issues/1729)) ([930a92d](https://github.com/dasch-swiss/dsp-tools/commit/930a92d28505e5b3cbb8ed7bb5840cf7e6c63fa3))
* **xmllib:** add `None` as a default for legal info (DEV-4927) ([#1737](https://github.com/dasch-swiss/dsp-tools/issues/1737)) ([57e9de5](https://github.com/dasch-swiss/dsp-tools/commit/57e9de5a212bcf52506af249dccb106ab2ccb08e))
* **xmllib:** add new LicenseOther licenses to find_license_in_string() (DEV-4876) ([#1716](https://github.com/dasch-swiss/dsp-tools/issues/1716)) ([e7db46f](https://github.com/dasch-swiss/dsp-tools/commit/e7db46f9efc0ca31224ad1316c66344b4816302a))
* **xmllib:** change .env variable name to save warnings file (RDU-91) ([#1723](https://github.com/dasch-swiss/dsp-tools/issues/1723)) ([4eb75e5](https://github.com/dasch-swiss/dsp-tools/commit/4eb75e52a03b1a9a1ec20e114a8c5b71f248610b))
* **xmllib:** enable sorting of resources and values during serialisation (RDU-89) ([#1730](https://github.com/dasch-swiss/dsp-tools/issues/1730)) ([fb386b3](https://github.com/dasch-swiss/dsp-tools/commit/fb386b336db14bb31336fbfe61d1f0d7ddc90211))
* **xmlupload:** add CLI args to configure which validation severity level should be printed out (DEV-4901) ([#1732](https://github.com/dasch-swiss/dsp-tools/issues/1732)) ([0282cdc](https://github.com/dasch-swiss/dsp-tools/commit/0282cdc95ceba7866d2c2cf53c287f45a509c105))
* **xmlupload:** validate XML input with `validate-data` (DEV-4461) ([#1722](https://github.com/dasch-swiss/dsp-tools/issues/1722)) ([93c2345](https://github.com/dasch-swiss/dsp-tools/commit/93c2345d8be0b507d1a38e25f0e71e2ba0eb5576))


### Bug Fixes

* allow all licenses, not only the recommended ones (DEV-4903) ([#1724](https://github.com/dasch-swiss/dsp-tools/issues/1724)) ([82a3214](https://github.com/dasch-swiss/dsp-tools/commit/82a32145be65b388f72058db0dbdc52359343859))
* **validate-data:** allow values of the same property to have identical comments (DEV-4905) ([#1727](https://github.com/dasch-swiss/dsp-tools/issues/1727)) ([f35bd93](https://github.com/dasch-swiss/dsp-tools/commit/f35bd933ad634cf6c39ac51375b6d6e6100b6ecf))
* **validate-data:** reorganise user print messages and fix validation bool (DEV-4898) ([#1718](https://github.com/dasch-swiss/dsp-tools/issues/1718)) ([899f74b](https://github.com/dasch-swiss/dsp-tools/commit/899f74b3cd2a2c2876b146e4ef76f6300b78ec4b))


### Maintenance

* **start-stack:** bump versions to 2025.05.02 ([#1739](https://github.com/dasch-swiss/dsp-tools/issues/1739)) ([5787d3a](https://github.com/dasch-swiss/dsp-tools/commit/5787d3a72998c62b2e0f5dd92b190760c3c334eb))
* **valiate-data:** extract get project info from api ([#1740](https://github.com/dasch-swiss/dsp-tools/issues/1740)) ([b88e59e](https://github.com/dasch-swiss/dsp-tools/commit/b88e59ef636d56854775714028bfb0c5b97b2515))
* **validate-data:** add validate config ([#1726](https://github.com/dasch-swiss/dsp-tools/issues/1726)) ([98ac8d6](https://github.com/dasch-swiss/dsp-tools/commit/98ac8d6f91f1110c641bb00452e167a2f4289e51))
* **validate-data:** extract parsing of resources from validation command ([#1720](https://github.com/dasch-swiss/dsp-tools/issues/1720)) ([b591d1e](https://github.com/dasch-swiss/dsp-tools/commit/b591d1e5a5d05f87e8bb1f5c10fd432f4bdf6c5f))
* **validate-data:** rename `AllProjectLists` to more generic name ([#1728](https://github.com/dasch-swiss/dsp-tools/issues/1728)) ([f338b26](https://github.com/dasch-swiss/dsp-tools/commit/f338b26f3fc59b41abe88be1ee5e6ad0f43fe8b9))
* waypaver for next PR ([#1735](https://github.com/dasch-swiss/dsp-tools/issues/1735)) ([b62b1fd](https://github.com/dasch-swiss/dsp-tools/commit/b62b1fd9018038758ea057902cfb9c6dc8894246))
* **xmlupload:** separate parsing of processing of resources ([#1721](https://github.com/dasch-swiss/dsp-tools/issues/1721)) ([54c9b08](https://github.com/dasch-swiss/dsp-tools/commit/54c9b086ccdb82eea08bc94f85fcd5297b7e1151))


### Documentation

* **validate-data:** add all the flags and add explanation (DEV-4915) ([#1731](https://github.com/dasch-swiss/dsp-tools/issues/1731)) ([ab40324](https://github.com/dasch-swiss/dsp-tools/commit/ab4032465a2f47249cb08a1f262fc4634196ad1a))

## [14.0.0](https://github.com/dasch-swiss/dsp-tools/compare/v13.1.0...v14.0.0) (2025-05-15)


### ⚠ BREAKING CHANGES

* remove old create label to list node name mapper function (DEV-4850) ([#1690](https://github.com/dasch-swiss/dsp-tools/issues/1690))

### Enhancements

* **excel2json:** create enabled license array in json with excel (DEV-4865) ([#1697](https://github.com/dasch-swiss/dsp-tools/issues/1697)) ([9e93009](https://github.com/dasch-swiss/dsp-tools/commit/9e9300959b20eba5c639b8ac87bb663d117e7275))
* include enabled licenses in json (DEV-4805) ([#1696](https://github.com/dasch-swiss/dsp-tools/issues/1696)) ([2fb7739](https://github.com/dasch-swiss/dsp-tools/commit/2fb7739f86dcc0268193c65357fd669c253998bb))
* remove old create label to list node name mapper function (DEV-4850) ([#1690](https://github.com/dasch-swiss/dsp-tools/issues/1690)) ([c572e3c](https://github.com/dasch-swiss/dsp-tools/commit/c572e3c7e39799799af9e5a3d2f321960e967f48))
* **validate-data:** check that SimpleText gui elements do not contain linebreaks (DEV-4840) ([#1681](https://github.com/dasch-swiss/dsp-tools/issues/1681)) ([1eafc90](https://github.com/dasch-swiss/dsp-tools/commit/1eafc90a6a18868419a8774d8db2a3fb47fb5736))
* **validate-data:** downgrade the severity of missing legal information to warning (DEV-4897) ([#1714](https://github.com/dasch-swiss/dsp-tools/issues/1714)) ([2412948](https://github.com/dasch-swiss/dsp-tools/commit/241294877bc82572414c1e9d08cce61479c524cc))
* **validate-data:** filter out violations when Links reference resources in DB (DEV-4819) ([#1689](https://github.com/dasch-swiss/dsp-tools/issues/1689)) ([6932358](https://github.com/dasch-swiss/dsp-tools/commit/6932358ff7ba944b61ca5aaf37333ca98353ca39))
* **validate-data:** validate authorship string (DEV-4896) ([#1713](https://github.com/dasch-swiss/dsp-tools/issues/1713)) ([222f4f7](https://github.com/dasch-swiss/dsp-tools/commit/222f4f7eef02bb354b0c6c9155c67a576c511460))
* **xmllib:** add new license IRIs (DEV-4873) ([#1707](https://github.com/dasch-swiss/dsp-tools/issues/1707)) ([17b4672](https://github.com/dasch-swiss/dsp-tools/commit/17b4672207882f9a3a4f66a7fe79c617231fdd33))
* **xmllib:** add the option to overwrite the `Permissions.PROJECT_SPECIFIC_PERMISSIONS` with a custom default permissions (DEV-4877) ([#1710](https://github.com/dasch-swiss/dsp-tools/issues/1710)) ([56e3e55](https://github.com/dasch-swiss/dsp-tools/commit/56e3e550696f1b16161784a139813e4df39f72ba))
* **xmllib:** enable to save warning messages in csv through an .env configuration (DEV-4853) ([#1692](https://github.com/dasch-swiss/dsp-tools/issues/1692)) ([99c65ba](https://github.com/dasch-swiss/dsp-tools/commit/99c65ba97a02c0d829f22f1e2216319a724ae650))
* **xmllib:** helper function to parse licenses (DEV-4800) ([#1640](https://github.com/dasch-swiss/dsp-tools/issues/1640)) ([35c4f3a](https://github.com/dasch-swiss/dsp-tools/commit/35c4f3a41455ff3ba6570202165e588a4bed83fb))
* **xmllib:** support polars null values in is null checks (DEV-4841) ([#1673](https://github.com/dasch-swiss/dsp-tools/issues/1673)) ([8f0d416](https://github.com/dasch-swiss/dsp-tools/commit/8f0d416bce11b4ff1c9b1cd2ebc4e58bfeff19a0))


### Bug Fixes

* **xmllib:** prevent data loss in find_date_in_string() (DEV-4839) ([#1684](https://github.com/dasch-swiss/dsp-tools/issues/1684)) ([edd5740](https://github.com/dasch-swiss/dsp-tools/commit/edd57401f9930ce871f3bf2cc7e190bfe83f915c))
* **xmllib:** values of dsp in built resources should inherit permissions of the resource if it is not possible to specify them individually (DEV-4888) ([#1711](https://github.com/dasch-swiss/dsp-tools/issues/1711)) ([648879e](https://github.com/dasch-swiss/dsp-tools/commit/648879edaab0506a5e9417b5a7e0f50bc895d95d))
* **xmlupload:** characters that are escaped in the XML should not be escaped in the string after parsing (DEV-4835) ([#1671](https://github.com/dasch-swiss/dsp-tools/issues/1671)) ([f1e1552](https://github.com/dasch-swiss/dsp-tools/commit/f1e15523fcbf0aa41abff4127c534ba130c5b5fb))


### Maintenance

* autofix pyupgrade linting rules ([#1679](https://github.com/dasch-swiss/dsp-tools/issues/1679)) ([e236a73](https://github.com/dasch-swiss/dsp-tools/commit/e236a730c215bb88d30c502ffe97cb90b7e61af0))
* deduplicate helpers from excel2xml and xmllib ([#1683](https://github.com/dasch-swiss/dsp-tools/issues/1683)) ([e464967](https://github.com/dasch-swiss/dsp-tools/commit/e464967829c00718cfd50fd103f010ab3d3aa33d))
* explain dmypy restart in readme (DEV-4833) ([#1688](https://github.com/dasch-swiss/dsp-tools/issues/1688)) ([e2f5618](https://github.com/dasch-swiss/dsp-tools/commit/e2f56184f3ea0d03119f767c723379471c1d0cb1))
* resolve warnings in tests ([#1709](https://github.com/dasch-swiss/dsp-tools/issues/1709)) ([e693b77](https://github.com/dasch-swiss/dsp-tools/commit/e693b77693413ed55baffd3b496d2e5018adaffe))
* some small fixes ([#1685](https://github.com/dasch-swiss/dsp-tools/issues/1685)) ([54bea5e](https://github.com/dasch-swiss/dsp-tools/commit/54bea5ee80d3581073f1a170f42a7790fe6e0cfc))
* **start-stack:** bump versions to 2025.05.01 ([#1715](https://github.com/dasch-swiss/dsp-tools/issues/1715)) ([edc0fa0](https://github.com/dasch-swiss/dsp-tools/commit/edc0fa099165aa390670206f0092c7c6f8bf17bc))
* **validate-data:** improve code structure of user message communication ([#1695](https://github.com/dasch-swiss/dsp-tools/issues/1695)) ([75b1907](https://github.com/dasch-swiss/dsp-tools/commit/75b19077ed0f5178a897aeefa7493e24251c9895))
* **validate-data:** re-organise validation message for user ([#1693](https://github.com/dasch-swiss/dsp-tools/issues/1693)) ([dd314dd](https://github.com/dasch-swiss/dsp-tools/commit/dd314dd26914c2f1430961b7d8acd27a285d53ff))
* **xmllib:** change order of warnings util functions ([#1691](https://github.com/dasch-swiss/dsp-tools/issues/1691)) ([05c5a9e](https://github.com/dasch-swiss/dsp-tools/commit/05c5a9ee278b89dc3849a622b2b8f1d3593e281f))
* **xmllib:** create factory methods for `FileValues` ([#1668](https://github.com/dasch-swiss/dsp-tools/issues/1668)) ([4b8b347](https://github.com/dasch-swiss/dsp-tools/commit/4b8b347f45fbb7363ad541bfda0fc07245286e34))
* **xmllib:** integrate warning utils ([#1677](https://github.com/dasch-swiss/dsp-tools/issues/1677)) ([919669e](https://github.com/dasch-swiss/dsp-tools/commit/919669ede88f8dd1ca1631ddfd19fe2288f50a3c))
* **xmllib:** move internal code into separate folder ([#1676](https://github.com/dasch-swiss/dsp-tools/issues/1676)) ([b0b3dbc](https://github.com/dasch-swiss/dsp-tools/commit/b0b3dbc7026c85ff432bced57d7cbc5a85ba3978))
* **xmllib:** move raising of errors out of richtext serialisation (DEV-4832) ([#1686](https://github.com/dasch-swiss/dsp-tools/issues/1686)) ([7ee2605](https://github.com/dasch-swiss/dsp-tools/commit/7ee2605020536bf046cf92166603f70786a9d1d1))
* **xmllib:** remove resource id from `Value` ([#1672](https://github.com/dasch-swiss/dsp-tools/issues/1672)) ([5b28a47](https://github.com/dasch-swiss/dsp-tools/commit/5b28a4762d97ff3836d3b0c81779afe0b85088c9))
* **xmllib:** reorganise and streamline internal util functions ([#1678](https://github.com/dasch-swiss/dsp-tools/issues/1678)) ([792880d](https://github.com/dasch-swiss/dsp-tools/commit/792880d2ad7fb35be8b3a1d11abe653f92443de2))
* **xmlupload:** remove duplicate file type identification (DEV-4455) ([#1717](https://github.com/dasch-swiss/dsp-tools/issues/1717)) ([41a71ef](https://github.com/dasch-swiss/dsp-tools/commit/41a71efa8b567472cf7a7512ee796a4c6bc07e9f))


### Documentation

* fix typo in documentation ([#1694](https://github.com/dasch-swiss/dsp-tools/issues/1694)) ([70c25cb](https://github.com/dasch-swiss/dsp-tools/commit/70c25cb1657d33ec2889c735a0fca7aa5beb8525))
* move incremental-xmlupload into folder special-workflows ([#1687](https://github.com/dasch-swiss/dsp-tools/issues/1687)) ([4359bea](https://github.com/dasch-swiss/dsp-tools/commit/4359bea3fd987f170f0be6aee2142c1cc804babc))

## [13.1.0](https://github.com/dasch-swiss/dsp-tools/compare/v13.0.0...v13.1.0) (2025-04-30)


### Enhancements

* **validate-data:** ensure that properties that should only be single line do not contain line breaks (DEV-4808) ([#1635](https://github.com/dasch-swiss/dsp-tools/issues/1635)) ([21efebb](https://github.com/dasch-swiss/dsp-tools/commit/21efebbbdc0516b7b8ea2334e80a9790718e73de))
* **validate-data:** remove whitespaces from `TextValues` to better detect duplicates (RDU-78) ([#1651](https://github.com/dasch-swiss/dsp-tools/issues/1651)) ([c099421](https://github.com/dasch-swiss/dsp-tools/commit/c099421d13dc40e93870c5604963226c94853495))
* **xmllib:** create function to remove redundant whitespaces and newlines from string (DEV-4801) ([#1633](https://github.com/dasch-swiss/dsp-tools/issues/1633)) ([7167890](https://github.com/dasch-swiss/dsp-tools/commit/716789080fac2a043ef3f705a659fe1f3b7a3df1))
* **xmllib:** search and warn potentially empty input string (DEV-4827) ([#1662](https://github.com/dasch-swiss/dsp-tools/issues/1662)) ([ed348bd](https://github.com/dasch-swiss/dsp-tools/commit/ed348bd2c206d88b649d82ab0ab352eaa7ce0f7a))
* **xmlupload:** allow list IRIs to be referenced in the XML (DEV-4831) ([#1664](https://github.com/dasch-swiss/dsp-tools/issues/1664)) ([3497f9d](https://github.com/dasch-swiss/dsp-tools/commit/3497f9d5dbbf3c3a019e568b94dbf10c82ae97b7))


### Bug Fixes

* distinguish between strings/regexes in KNOWN_XML_TAGS (DEV-4781) ([#1619](https://github.com/dasch-swiss/dsp-tools/issues/1619)) ([0c7c5d7](https://github.com/dasch-swiss/dsp-tools/commit/0c7c5d7e66d501c43fb97d1cfcf1cc8244e22b3c))
* **id2iri:** include segment resources for id replacement (DEV-4797) ([#1630](https://github.com/dasch-swiss/dsp-tools/issues/1630)) ([c6ba599](https://github.com/dasch-swiss/dsp-tools/commit/c6ba59918c084490b3f14194164bbd7e620ca5ee))
* SyntaxWarning: invalid escape sequence '\p' ([#1618](https://github.com/dasch-swiss/dsp-tools/issues/1618)) ([d279c92](https://github.com/dasch-swiss/dsp-tools/commit/d279c92d9f1603c0ccd9bc28204f5ebddf804377))
* **xmllib:** do not warn if comment on values are left empty (DEV-4834) ([#1669](https://github.com/dasch-swiss/dsp-tools/issues/1669)) ([f848d73](https://github.com/dasch-swiss/dsp-tools/commit/f848d736eaa9fed39c1e104d6921a8513b8e6732))
* **xmllib:** new warnings: pair programming results ([#1661](https://github.com/dasch-swiss/dsp-tools/issues/1661)) ([ae70ba8](https://github.com/dasch-swiss/dsp-tools/commit/ae70ba8a9b53317847fa45a8a3f7569222a2b922))
* **xmllib:** replace namedentities package (DEV-4755) ([#1611](https://github.com/dasch-swiss/dsp-tools/issues/1611)) ([fbd8b44](https://github.com/dasch-swiss/dsp-tools/commit/fbd8b449a290f706b0263a0f38648698ccb9d4f1))
* **xmlupload:** convert HTTPS api url to HTTP url for ontology IRI construction (DEV-4803) ([#1634](https://github.com/dasch-swiss/dsp-tools/issues/1634)) ([a81888c](https://github.com/dasch-swiss/dsp-tools/commit/a81888c8fdb042f429a7cc0f60468cca4e69396f))
* **xmlupload:** correctly communicate if text val contains invalid chars ([#1650](https://github.com/dasch-swiss/dsp-tools/issues/1650)) ([d5950e5](https://github.com/dasch-swiss/dsp-tools/commit/d5950e5ff0271bc6d9e4a76fcd66eebc37cbcb82))
* **xmlupload:** user friendly message for duplicate res IDs (DEV-4747) ([#1643](https://github.com/dasch-swiss/dsp-tools/issues/1643)) ([46d8015](https://github.com/dasch-swiss/dsp-tools/commit/46d801555e7f883f35502a4a058b8ef138dfcb77))
* **xmlupload:** validate link target IDs of Segment resources (DEV-4794) ([#1625](https://github.com/dasch-swiss/dsp-tools/issues/1625)) ([6cd2a27](https://github.com/dasch-swiss/dsp-tools/commit/6cd2a2743c99df75861b638444e8a25db7658fd1))


### Maintenance

* add deprecation warning to excel2xml.write_xml() (DEV-4783) ([#1641](https://github.com/dasch-swiss/dsp-tools/issues/1641)) ([3b4353b](https://github.com/dasch-swiss/dsp-tools/commit/3b4353b53b298f8b311f58c2b0adb1a241e8d633))
* bump dependencies ([#1652](https://github.com/dasch-swiss/dsp-tools/issues/1652)) ([51903a5](https://github.com/dasch-swiss/dsp-tools/commit/51903a5e18fe2856919e03fc0b8342f8cf843e82))
* consolidate duplications of is_nonempty_value() and is_string_like() (DEV-4788) ([#1621](https://github.com/dasch-swiss/dsp-tools/issues/1621)) ([b501cd9](https://github.com/dasch-swiss/dsp-tools/commit/b501cd982869f6a212ae9414a6261aec3d8f7be9))
* consolidate xml parsing and cleaning functions ([#1632](https://github.com/dasch-swiss/dsp-tools/issues/1632)) ([1b309c3](https://github.com/dasch-swiss/dsp-tools/commit/1b309c333970c93d3bec1b44de9b0b8eb6920b2b))
* copy tests from excel2xml to xmllib ([#1629](https://github.com/dasch-swiss/dsp-tools/issues/1629)) ([8846c5b](https://github.com/dasch-swiss/dsp-tools/commit/8846c5b5cfb85e182746f6720ec421fdbce89ec5))
* implement vulture to find dead code ([#1626](https://github.com/dasch-swiss/dsp-tools/issues/1626)) ([bf53313](https://github.com/dasch-swiss/dsp-tools/commit/bf53313c681f1f13ccd30eff23878391db34a78b))
* **ingest-xmlupload:** use `ParsedResource` instead of `XMLResource` ([#1622](https://github.com/dasch-swiss/dsp-tools/issues/1622)) ([4ab3fd8](https://github.com/dasch-swiss/dsp-tools/commit/4ab3fd853a49de193e2c43a5c86e135eb6dc6387))
* refactor _handle_non_ok_responses() ([#1646](https://github.com/dasch-swiss/dsp-tools/issues/1646)) ([206a7f8](https://github.com/dasch-swiss/dsp-tools/commit/206a7f8d86f563b0a262d7360679aeaff3ddce46))
* remove `XMLResource` ([#1624](https://github.com/dasch-swiss/dsp-tools/issues/1624)) ([1a7289d](https://github.com/dasch-swiss/dsp-tools/commit/1a7289d0ac1f775ddf8696ae81d2e6a86a8ab2da))
* remove get used IRIs from `get_parsed_resources` ([#1645](https://github.com/dasch-swiss/dsp-tools/issues/1645)) ([932d756](https://github.com/dasch-swiss/dsp-tools/commit/932d756d993e59336c0aed6ad8be47e858ec9d5e))
* remove whitespaces when creating `ParsedResource` ([#1623](https://github.com/dasch-swiss/dsp-tools/issues/1623)) ([1d86782](https://github.com/dasch-swiss/dsp-tools/commit/1d86782553ca3f5e655e1f4b962620af4c0c6d93))
* rename get_data_deserialised file ([#1627](https://github.com/dasch-swiss/dsp-tools/issues/1627)) ([9d445d7](https://github.com/dasch-swiss/dsp-tools/commit/9d445d7c4dc1e21597684b42f8f32fb60d4aa679))
* resolve warnings and bump dependencies ([#1636](https://github.com/dasch-swiss/dsp-tools/issues/1636)) ([f00aa31](https://github.com/dasch-swiss/dsp-tools/commit/f00aa3154a65557b3c54cb5dc935919b8145730e))
* resolve warnings in tests ([#1647](https://github.com/dasch-swiss/dsp-tools/issues/1647)) ([713a2b3](https://github.com/dasch-swiss/dsp-tools/commit/713a2b3b08a6fe71dd68c4424f801e810ec412c3))
* **start-stack:** bump versions to 2025.04.03 ([#1670](https://github.com/dasch-swiss/dsp-tools/issues/1670)) ([4c8c51e](https://github.com/dasch-swiss/dsp-tools/commit/4c8c51e06ef4919482d7dddbed9bfa746d0cad8a))
* **validate-data:** clean up and add logging statements ([#1660](https://github.com/dasch-swiss/dsp-tools/issues/1660)) ([e0cb871](https://github.com/dasch-swiss/dsp-tools/commit/e0cb87105e11a4085c30466cb6b92ec6b9851217))
* **validate-data:** create `DataDeserialised` from `ParsedResource` ([#1628](https://github.com/dasch-swiss/dsp-tools/issues/1628)) ([ffc6192](https://github.com/dasch-swiss/dsp-tools/commit/ffc6192a30221f041b56e2bc7f8e31478a60c1ac))
* **validate-data:** integrate get data deserialised from `ParsedResource` into code ([#1631](https://github.com/dasch-swiss/dsp-tools/issues/1631)) ([748bf92](https://github.com/dasch-swiss/dsp-tools/commit/748bf92ddef79178fde1f903a869172d41595700))
* **validate-data:** optimise check if only known resource classes are used in file ([#1644](https://github.com/dasch-swiss/dsp-tools/issues/1644)) ([ce01b6f](https://github.com/dasch-swiss/dsp-tools/commit/ce01b6ff9e7e2aded1e3a420e74d9246f3668885))
* **validate-data:** rename `ResourceDeserialised` into `RdfLikeResource` (DEV-4817) ([#1654](https://github.com/dasch-swiss/dsp-tools/issues/1654)) ([a08b472](https://github.com/dasch-swiss/dsp-tools/commit/a08b4728a7407a08bcb1f805e2b30133c9fc789b))
* **validate-data:** reorganise parsing of XML file and data construction ([#1642](https://github.com/dasch-swiss/dsp-tools/issues/1642)) ([58d0f86](https://github.com/dasch-swiss/dsp-tools/commit/58d0f86b1857fb6aa84e6ab36bcc498a55e9eed2))
* **xmllib:** change construction of warnings messages (DEV-4793) ([#1656](https://github.com/dasch-swiss/dsp-tools/issues/1656)) ([d70346b](https://github.com/dasch-swiss/dsp-tools/commit/d70346b95697507718ae3bd0198c2f9b168efdb8))
* **xmllib:** change find function trace ([#1658](https://github.com/dasch-swiss/dsp-tools/issues/1658)) ([01b0cd3](https://github.com/dasch-swiss/dsp-tools/commit/01b0cd343cbf8d8f024190f5eabb66bf71375cd9))
* **xmllib:** change input type mismatch warning ([#1659](https://github.com/dasch-swiss/dsp-tools/issues/1659)) ([cadcb56](https://github.com/dasch-swiss/dsp-tools/commit/cadcb564255bd40755d0a067ac8d38ac71c75029))
* **xmllib:** change warning and error messages in helper functions ([#1667](https://github.com/dasch-swiss/dsp-tools/issues/1667)) ([f5d1e01](https://github.com/dasch-swiss/dsp-tools/commit/f5d1e011a025005992e3540020e0ee0a1263d82d))
* **xmllib:** create all values with factory method ([#1666](https://github.com/dasch-swiss/dsp-tools/issues/1666)) ([a9b45ce](https://github.com/dasch-swiss/dsp-tools/commit/a9b45cef1796e6dd3350ce85d240c5c55c4a11cf))
* **xmllib:** create factory method for `BooleanValue` ([#1663](https://github.com/dasch-swiss/dsp-tools/issues/1663)) ([f243e60](https://github.com/dasch-swiss/dsp-tools/commit/f243e6015d6ca42c2594a8e7f9246fcf6410fc67))
* **xmllib:** create factory method for `Richtext` ([#1665](https://github.com/dasch-swiss/dsp-tools/issues/1665)) ([44d1278](https://github.com/dasch-swiss/dsp-tools/commit/44d12787c5f4e18345486a282ad15403f86af74d))
* **xmllib:** create separate warning classes (DEV-4819) ([#1655](https://github.com/dasch-swiss/dsp-tools/issues/1655)) ([ed40e78](https://github.com/dasch-swiss/dsp-tools/commit/ed40e7891671adda0c976be481f6c90c483516be))
* **xmllib:** integrate warning utils into dsp base resources (DEV-4823) ([#1657](https://github.com/dasch-swiss/dsp-tools/issues/1657)) ([af6fb77](https://github.com/dasch-swiss/dsp-tools/commit/af6fb77e034a43958587a099acba5eab52f7310e))
* **xmlupload:** move create lookup functions into utils ([#1638](https://github.com/dasch-swiss/dsp-tools/issues/1638)) ([8f642f2](https://github.com/dasch-swiss/dsp-tools/commit/8f642f2522d5daf41fd6782fe6f7dec64a3e1765))
* **xmlupload:** rename `IntermediaryResource` into `ProcessedResource` (DEV-4816) ([#1653](https://github.com/dasch-swiss/dsp-tools/issues/1653)) ([0f65f38](https://github.com/dasch-swiss/dsp-tools/commit/0f65f386ec2fd152f36af7301b9dccf01c7e81e3))
* **xmlupload:** use `ParsedResource` instead of `XMLResource` ([#1617](https://github.com/dasch-swiss/dsp-tools/issues/1617)) ([f5f293a](https://github.com/dasch-swiss/dsp-tools/commit/f5f293a53043bf0c4dc91c98d3e2eea7f20de85d))

## [13.0.0](https://github.com/dasch-swiss/dsp-tools/compare/v12.1.0...v13.0.0) (2025-04-09)


### ⚠ BREAKING CHANGES

* change structure of `PreDefinedLicenses` config in xmllib (DEV-4762) ([#1605](https://github.com/dasch-swiss/dsp-tools/issues/1605))

### Enhancements

* change structure of `PreDefinedLicenses` config in xmllib (DEV-4762) ([#1605](https://github.com/dasch-swiss/dsp-tools/issues/1605)) ([7319985](https://github.com/dasch-swiss/dsp-tools/commit/7319985ec95b26a1b2ce5265cb5760015c56e8a3))
* downgrade warning level if angular brackets were found in Simpletext (DEV-4746) ([#1593](https://github.com/dasch-swiss/dsp-tools/issues/1593)) ([16d875a](https://github.com/dasch-swiss/dsp-tools/commit/16d875a3a82ae87946903a321d8997d54b1b183b))
* **xmllib:** create additional label to list name helper functions and lookups (DEV-4753) ([#1598](https://github.com/dasch-swiss/dsp-tools/issues/1598)) ([da67e9a](https://github.com/dasch-swiss/dsp-tools/commit/da67e9a72f6f989f4122e2da9b341a4063631e40))
* **xmllib:** support BCE dates in `find_date_in_string()` (RDU-83) ([#1596](https://github.com/dasch-swiss/dsp-tools/issues/1596)) ([5361bc6](https://github.com/dasch-swiss/dsp-tools/commit/5361bc603a8f1b7db4865590c2449217618d875d))


### Bug Fixes

* correct rdflib import (DEV-4765) ([#1612](https://github.com/dasch-swiss/dsp-tools/issues/1612)) ([67d6770](https://github.com/dasch-swiss/dsp-tools/commit/67d67708cfe89bf4730279a4483ab6ca1a3cd8de))
* **xmllib:** allow additional header tags that can be displayed in the app (DEV-4756) ([#1599](https://github.com/dasch-swiss/dsp-tools/issues/1599)) ([700ccbb](https://github.com/dasch-swiss/dsp-tools/commit/700ccbb806554c7bb9e1fe0268c10b8e78a7f8a9))


### Maintenance

* bump start-stack to 2025.04.02 ([#1616](https://github.com/dasch-swiss/dsp-tools/issues/1616)) ([486855f](https://github.com/dasch-swiss/dsp-tools/commit/486855f42f61aa432681813728bc78d682ab7009))
* consolidate code duplications (DEV-4780) ([#1613](https://github.com/dasch-swiss/dsp-tools/issues/1613)) ([432364d](https://github.com/dasch-swiss/dsp-tools/commit/432364d4d5fa3d8d2dcf5d5ccab5a4928504bc63))
* create new classes to parse XML ([#1591](https://github.com/dasch-swiss/dsp-tools/issues/1591)) ([6b8fce1](https://github.com/dasch-swiss/dsp-tools/commit/6b8fce1a03415c914ff525d561548e46072cd1a4))
* parse XML into `ParsedResource` ([#1594](https://github.com/dasch-swiss/dsp-tools/issues/1594)) ([dfb4ff3](https://github.com/dasch-swiss/dsp-tools/commit/dfb4ff332da4ea82c7d23e63ca2157fa55ffbe35))
* PR checks should be triggered on PRs from forks ([#1608](https://github.com/dasch-swiss/dsp-tools/issues/1608)) ([164b2f9](https://github.com/dasch-swiss/dsp-tools/commit/164b2f926de7522ed9f0ec5e57f332af041310bd))
* **start-stack:** switch `docker` command parts to match documentation ([#1606](https://github.com/dasch-swiss/dsp-tools/issues/1606)) ([bdb93c2](https://github.com/dasch-swiss/dsp-tools/commit/bdb93c2ba38229b8cbfe3013632d68d68f5eb208))
* **xmlupload:** create functionality to transform resources from `ParsedResource` into `ResourceIntermediary` ([#1601](https://github.com/dasch-swiss/dsp-tools/issues/1601)) ([1cfdc8d](https://github.com/dasch-swiss/dsp-tools/commit/1cfdc8d623fbc7b65919d743801cd7c8621c6c7b))
* **xmlupload:** deserialise list-prop as tuple and not string ([#1597](https://github.com/dasch-swiss/dsp-tools/issues/1597)) ([22d7fcf](https://github.com/dasch-swiss/dsp-tools/commit/22d7fcf2fea52957b24114559c9fb645a7e05321))
* **xmlupload:** extract validation functions that use the root ([#1614](https://github.com/dasch-swiss/dsp-tools/issues/1614)) ([2df357f](https://github.com/dasch-swiss/dsp-tools/commit/2df357f49f045ba8ae948942da9d72375f4a7273))
* **xmlupload:** move creation of intermediary lookup ([#1610](https://github.com/dasch-swiss/dsp-tools/issues/1610)) ([4b6d708](https://github.com/dasch-swiss/dsp-tools/commit/4b6d708e68bd7a759ed2f832471f9d46cd9501f4))
* **xmlupload:** move transform rich- and simpletext values ([#1603](https://github.com/dasch-swiss/dsp-tools/issues/1603)) ([cb98c3c](https://github.com/dasch-swiss/dsp-tools/commit/cb98c3c5c252bc0023c4652a540b565c01bd8570))
* **xmlupload:** rename transform into intermediary resources files ([#1602](https://github.com/dasch-swiss/dsp-tools/issues/1602)) ([f3394f7](https://github.com/dasch-swiss/dsp-tools/commit/f3394f725c584e4f9d3e22a5e2c8fbbe8adc26a5))


### Documentation

* fix typo and display in architecture.md ([#1600](https://github.com/dasch-swiss/dsp-tools/issues/1600)) ([9ef3743](https://github.com/dasch-swiss/dsp-tools/commit/9ef3743ad64c58d1bad95eb90c58e4fbe2798163))
* **xmlupload:** fix attribute of hasSegmentBounds (`<video-segment>` / `<audio-segment>`) ([#1595](https://github.com/dasch-swiss/dsp-tools/issues/1595)) ([472a0b9](https://github.com/dasch-swiss/dsp-tools/commit/472a0b9f66ed75c4e4da834817ae3497b9f2d6e9))

## [12.1.0](https://github.com/dasch-swiss/dsp-tools/compare/v12.0.0...v12.1.0) (2025-04-02)


### Enhancements

* **xmllib:** use UUID for authorship ID instead of number (DEV-4739) ([#1584](https://github.com/dasch-swiss/dsp-tools/issues/1584)) ([7b8fa4a](https://github.com/dasch-swiss/dsp-tools/commit/7b8fa4a985a2734d50fb81b21d8a8d3eec83f9bd))


### Bug Fixes

* **xmlupload:** add comment on value to shashed links and texts (DEV-4730) ([#1573](https://github.com/dasch-swiss/dsp-tools/issues/1573)) ([3670754](https://github.com/dasch-swiss/dsp-tools/commit/36707542761cf7f9d1a7683f73512315ae869b39))


### Maintenance

* bump start-stack to 2025.04.01 ([#1583](https://github.com/dasch-swiss/dsp-tools/issues/1583)) ([794b842](https://github.com/dasch-swiss/dsp-tools/commit/794b842fcf26e2546fd64394bf8e2e06c16a65bd))
* delete dead code ([#1577](https://github.com/dasch-swiss/dsp-tools/issues/1577)) ([0205c59](https://github.com/dasch-swiss/dsp-tools/commit/0205c5958f6117929c7c4ec16da403c01f5ce352))
* move rdflib constants to one file ([#1589](https://github.com/dasch-swiss/dsp-tools/issues/1589)) ([78070eb](https://github.com/dasch-swiss/dsp-tools/commit/78070eb56263392124fcbaefb5ba82a2422c8b25))
* optimise `just clean` ([#1570](https://github.com/dasch-swiss/dsp-tools/issues/1570)) ([8347fe3](https://github.com/dasch-swiss/dsp-tools/commit/8347fe30dcbb76f986c0041671a518846ac5ac0c))
* **test:** Use real iris in xmlupload integration tests ([#1582](https://github.com/dasch-swiss/dsp-tools/issues/1582)) ([634a8b4](https://github.com/dasch-swiss/dsp-tools/commit/634a8b49c8df5881e2c02eb4da2cd37784882987))
* **xmlupload:** add option to use own value IRI in graph ([#1575](https://github.com/dasch-swiss/dsp-tools/issues/1575)) ([cf1927b](https://github.com/dasch-swiss/dsp-tools/commit/cf1927b1a57a667e76b079d882eb6f8294abe635))
* **xmlupload:** change order of code ([#1574](https://github.com/dasch-swiss/dsp-tools/issues/1574)) ([5b7d657](https://github.com/dasch-swiss/dsp-tools/commit/5b7d6577a67cbb96cbfabb4d7edac6923a6f53eb))
* **xmlupload:** create minimal XML parsing and validation function ([#1590](https://github.com/dasch-swiss/dsp-tools/issues/1590)) ([b0f51d6](https://github.com/dasch-swiss/dsp-tools/commit/b0f51d6db62dd57a7bb78436712510b4bc61f29d))
* **xmlupload:** extract json-ld serialisation ([#1580](https://github.com/dasch-swiss/dsp-tools/issues/1580)) ([b961d9c](https://github.com/dasch-swiss/dsp-tools/commit/b961d9c6cd1f1ade6c576805b5270d534a817387))
* **xmlupload:** integrate create upload order from `ResourceIntermediary` ([#1550](https://github.com/dasch-swiss/dsp-tools/issues/1550)) ([b279e68](https://github.com/dasch-swiss/dsp-tools/commit/b279e689b9ec0903daa34ff153f260cc5b7c1364))
* **xmlupload:** move resolve ID to IRI outside of function when creating a `LinkValue` ([#1581](https://github.com/dasch-swiss/dsp-tools/issues/1581)) ([aed3ff2](https://github.com/dasch-swiss/dsp-tools/commit/aed3ff2c5a4cbc00e3e415d731f82df6c53568e4))
* **xmlupload:** remove old code and rename files ([#1572](https://github.com/dasch-swiss/dsp-tools/issues/1572)) ([cbd14de](https://github.com/dasch-swiss/dsp-tools/commit/cbd14de69c85c24f1cad522f69a28811a6c45f6c))
* **xmlupload:** remove redundant `JsonldContext` ([#1586](https://github.com/dasch-swiss/dsp-tools/issues/1586)) ([2827881](https://github.com/dasch-swiss/dsp-tools/commit/2827881211018a627caf5f38e2c2fc98c4480e88))
* **xmlupload:** serialise `LinkValueStashItem` with rdflib ([#1579](https://github.com/dasch-swiss/dsp-tools/issues/1579)) ([041c6c3](https://github.com/dasch-swiss/dsp-tools/commit/041c6c3e7db6d8e4ed456b67e06791ba5dc4842e))
* **xmlupload:** serialise `StandoffStashItem` with rdflib ([#1576](https://github.com/dasch-swiss/dsp-tools/issues/1576)) ([53de9d4](https://github.com/dasch-swiss/dsp-tools/commit/53de9d4a8c12b59443387fcc0a366b20d28dce1b))


### Documentation

* create architectural design record ([#1587](https://github.com/dasch-swiss/dsp-tools/issues/1587)) ([5546dcf](https://github.com/dasch-swiss/dsp-tools/commit/5546dcfd92e7c73246472ac455755bab156d25b5))

## [12.0.0](https://github.com/dasch-swiss/dsp-tools/compare/v11.0.0...v12.0.0) (2025-03-26)


### ⚠ BREAKING CHANGES

* rename old and new excel2json/excel2lists commands (RDU-80) ([#1558](https://github.com/dasch-swiss/dsp-tools/issues/1558))

### Enhancements

* rename old and new excel2json/excel2lists commands (RDU-80) ([#1558](https://github.com/dasch-swiss/dsp-tools/issues/1558)) ([5788aba](https://github.com/dasch-swiss/dsp-tools/commit/5788abaa22aec64d7ff9a978d9a05863bb9968b9))


### Bug Fixes

* delete warning.log if empty (DEV-3438) ([#1559](https://github.com/dasch-swiss/dsp-tools/issues/1559)) ([41ff3ed](https://github.com/dasch-swiss/dsp-tools/commit/41ff3ed290691eef5e8def5474aa14797226607c))
* **xmlupload:** disallow the combination of eras and Islamic calendar dates (RDU-77) ([#1557](https://github.com/dasch-swiss/dsp-tools/issues/1557)) ([36206ea](https://github.com/dasch-swiss/dsp-tools/commit/36206eae9e04042fac6570563bcb393540864830))


### Maintenance

* add option to exclude request response text in logging ([#1569](https://github.com/dasch-swiss/dsp-tools/issues/1569)) ([624d1a2](https://github.com/dasch-swiss/dsp-tools/commit/624d1a28248ec49cc3e49780365f5b765c8993de))
* bump dependencies ([#1566](https://github.com/dasch-swiss/dsp-tools/issues/1566)) ([34e7051](https://github.com/dasch-swiss/dsp-tools/commit/34e7051b7c3c66a44d4813567062329f146ddc66))
* merge UserError and InputError classes (DEV-4698) ([#1555](https://github.com/dasch-swiss/dsp-tools/issues/1555)) ([52ba834](https://github.com/dasch-swiss/dsp-tools/commit/52ba8342a46ec79b878289254e73a7c77ac9a7f4))
* remove version restriction on "testcontainers" ([#1567](https://github.com/dasch-swiss/dsp-tools/issues/1567)) ([f2fb985](https://github.com/dasch-swiss/dsp-tools/commit/f2fb985c129966455e4d14dd6323cc68f024e6be))
* reorganise package structure (DEV-4721) ([#1564](https://github.com/dasch-swiss/dsp-tools/issues/1564)) ([e483b3b](https://github.com/dasch-swiss/dsp-tools/commit/e483b3b1a20af89e169c73b60a47229e7c1af354))
* reorganise utils ([#1565](https://github.com/dasch-swiss/dsp-tools/issues/1565)) ([ceac23c](https://github.com/dasch-swiss/dsp-tools/commit/ceac23cb7092a773701adac2e5658994ea5f1ffd))
* run `uv sync` before `just lint`, to prevent parallelism issues ([#1562](https://github.com/dasch-swiss/dsp-tools/issues/1562)) ([cbe35e1](https://github.com/dasch-swiss/dsp-tools/commit/cbe35e19137d18568db26013fa076ab9c1f91f9a))
* Update versions 2025.03.03 ([#1563](https://github.com/dasch-swiss/dsp-tools/issues/1563)) ([3c12484](https://github.com/dasch-swiss/dsp-tools/commit/3c124847dc38efc5ad85921e4a42332dd323d6e8))
* upgrade pytest (DEV-3786) ([#1568](https://github.com/dasch-swiss/dsp-tools/issues/1568)) ([a99bd00](https://github.com/dasch-swiss/dsp-tools/commit/a99bd0029cc6883910b687787a6cab6679e0a123))
* **validate-data:** PostFiles ([#1554](https://github.com/dasch-swiss/dsp-tools/issues/1554)) ([21f33e6](https://github.com/dasch-swiss/dsp-tools/commit/21f33e61e836c51aa4a3b0bf0b0223a6f9cb1d0e))
* **validate-data:** remove ApiConnection, handle all network interaction in ListClient (DEV-4702) ([#1546](https://github.com/dasch-swiss/dsp-tools/issues/1546)) ([046da8b](https://github.com/dasch-swiss/dsp-tools/commit/046da8b4d6358ab9ade85ff37d3ea0355bfc9319))


### Documentation

* fix UI bug: admonition is not supported on pypi.org (DEV-4715) ([#1556](https://github.com/dasch-swiss/dsp-tools/issues/1556)) ([98bdc97](https://github.com/dasch-swiss/dsp-tools/commit/98bdc974af4dc0650467a63ff277d555445fd08d))

## [11.0.0](https://github.com/dasch-swiss/dsp-tools/compare/v10.6.0...v11.0.0) (2025-03-19)


### ⚠ BREAKING CHANGES

* **create:** remove Excel folder reference from JSON project file (DEV-4687) ([#1521](https://github.com/dasch-swiss/dsp-tools/issues/1521))

### Enhancements

* **create:** remove Excel folder reference from JSON project file (DEV-4687) ([#1521](https://github.com/dasch-swiss/dsp-tools/issues/1521)) ([8185e12](https://github.com/dasch-swiss/dsp-tools/commit/8185e12162f358c778f8fa4fef076c56ba2765b4))
* **validate-data:** verify that the used license is allowed (DEV-4659) ([#1492](https://github.com/dasch-swiss/dsp-tools/issues/1492)) ([8701bf9](https://github.com/dasch-swiss/dsp-tools/commit/8701bf9ef8297145d8f3b73c524ac09abd0633db))


### Bug Fixes

* **ci:** trigger tests in release PR (DEV-4675) ([#1502](https://github.com/dasch-swiss/dsp-tools/issues/1502)) ([c2d0127](https://github.com/dasch-swiss/dsp-tools/commit/c2d01276c7e4453c012a95f0e66bae85edff65c1))
* **create:** prevent duplicate list nodes (DEV-3531, DEV-3632) ([#1507](https://github.com/dasch-swiss/dsp-tools/issues/1507)) ([f60badb](https://github.com/dasch-swiss/dsp-tools/commit/f60badba3e3e3324445b6024a3c85384cd79d23c))
* **ingest-xmlupload:** handle pretty-printed bitstream paths ([#1522](https://github.com/dasch-swiss/dsp-tools/issues/1522)) ([254b2f6](https://github.com/dasch-swiss/dsp-tools/commit/254b2f60e787c436dd1133a5997c4569537abc2e))
* **validate-data:** correct the way Values are targeted in the SHACL shapes (DEV-4672) ([#1499](https://github.com/dasch-swiss/dsp-tools/issues/1499)) ([3db100f](https://github.com/dasch-swiss/dsp-tools/commit/3db100f74390512595b455829ee3861455ee0674))
* **validate-data:** recognise if `DateValue` is used instead of `SimpleText` (DEV-4681) ([#1511](https://github.com/dasch-swiss/dsp-tools/issues/1511)) ([192af3f](https://github.com/dasch-swiss/dsp-tools/commit/192af3fb659198e5b55df0ef6047622e7e96005f))
* **xmlupload:** Better Error Message when API returns NotFoundException (DEV-4631) ([#1506](https://github.com/dasch-swiss/dsp-tools/issues/1506)) ([e100ce2](https://github.com/dasch-swiss/dsp-tools/commit/e100ce20805c0a637205bdadaa01281e5dc69f1a))


### Maintenance

* _handle_non_ok_responses() ([#1505](https://github.com/dasch-swiss/dsp-tools/issues/1505)) ([193d971](https://github.com/dasch-swiss/dsp-tools/commit/193d971621d67bbf47b386235363f21417e356a7))
* add some just linting commands ([#1509](https://github.com/dasch-swiss/dsp-tools/issues/1509)) ([1071e7f](https://github.com/dasch-swiss/dsp-tools/commit/1071e7fb08010fa33c10f59988e2e039ab052644))
* auto-fix ruff violations in `just format` ([#1553](https://github.com/dasch-swiss/dsp-tools/issues/1553)) ([c48aca8](https://github.com/dasch-swiss/dsp-tools/commit/c48aca8f59a8eef49f084b07286faee0ba2cca2a))
* **ci:** trigger tests in release PR, the second ([#1508](https://github.com/dasch-swiss/dsp-tools/issues/1508)) ([8909f91](https://github.com/dasch-swiss/dsp-tools/commit/8909f91487c63dfd0362535c315afe9484d6fbd6))
* **create:** rename 1 directory and 1 file ([#1543](https://github.com/dasch-swiss/dsp-tools/issues/1543)) ([0071b3d](https://github.com/dasch-swiss/dsp-tools/commit/0071b3d92749a6306325e920f668cdb2f75e1d62))
* don't spam log file with stack traces (DEV-4607) ([#1544](https://github.com/dasch-swiss/dsp-tools/issues/1544)) ([6011562](https://github.com/dasch-swiss/dsp-tools/commit/6011562d15c274c54514651ffd32cc19d02dde4b))
* remove unused markdownlint containers ([#1526](https://github.com/dasch-swiss/dsp-tools/issues/1526)) ([499c745](https://github.com/dasch-swiss/dsp-tools/commit/499c745479f01e112198fda0fce4a99e83f1650c))
* reorganise justfile ([#1512](https://github.com/dasch-swiss/dsp-tools/issues/1512)) ([3385226](https://github.com/dasch-swiss/dsp-tools/commit/3385226a8f3fb8e42824a866cd7ecb0189f25deb))
* speed up mypy with daemon (DEV-4684) ([#1516](https://github.com/dasch-swiss/dsp-tools/issues/1516)) ([d9bec53](https://github.com/dasch-swiss/dsp-tools/commit/d9bec533c38d395fc2ee117990303d4d2d1a31be))
* Update versions 2025.03.02 ([#1551](https://github.com/dasch-swiss/dsp-tools/issues/1551)) ([4f8c372](https://github.com/dasch-swiss/dsp-tools/commit/4f8c3729afd106f3e778a8a4c2cebcba3d0dd314))
* **validate-data:** add property shapes to Values ([#1513](https://github.com/dasch-swiss/dsp-tools/issues/1513)) ([101313d](https://github.com/dasch-swiss/dsp-tools/commit/101313dfaa80ecb575d8992a1152337c4c602d6f))
* **validate-data:** change creation of cardinalities for file value property ([#1536](https://github.com/dasch-swiss/dsp-tools/issues/1536)) ([eb1d8fe](https://github.com/dasch-swiss/dsp-tools/commit/eb1d8fe151b85fa5a70aa705e6d93a75e42bbbcd))
* **validate-data:** change extraction of resource IRI and type ([#1530](https://github.com/dasch-swiss/dsp-tools/issues/1530)) ([764ed53](https://github.com/dasch-swiss/dsp-tools/commit/764ed533be05a676c2060b2caadd703b91e4b855))
* **validate-data:** change ID names in test data ([#1510](https://github.com/dasch-swiss/dsp-tools/issues/1510)) ([2a30bdc](https://github.com/dasch-swiss/dsp-tools/commit/2a30bdcc5987ae7e543cd3811b0e700f36aa9a8a))
* **validate-data:** change resource IRI and type extraction during result queries ([#1525](https://github.com/dasch-swiss/dsp-tools/issues/1525)) ([2edb389](https://github.com/dasch-swiss/dsp-tools/commit/2edb3891a121d7f4b3be9c0e407b3b1f21a70b02))
* **validate-data:** change targeting of `knora-api:Values` (DEV-4690) ([#1528](https://github.com/dasch-swiss/dsp-tools/issues/1528)) ([77a9a54](https://github.com/dasch-swiss/dsp-tools/commit/77a9a540f7c67658905051609a12ca42be3d6a22))
* **validate-data:** group property and nodeshapes better together ([#1534](https://github.com/dasch-swiss/dsp-tools/issues/1534)) ([3107c93](https://github.com/dasch-swiss/dsp-tools/commit/3107c9388e8dc8ae231a8420b878ef176ede443b))
* **validate-data:** harmonise file value shapes ([#1494](https://github.com/dasch-swiss/dsp-tools/issues/1494)) ([dad04de](https://github.com/dasch-swiss/dsp-tools/commit/dad04de7dcef0ae9bbb6912cdc81178e201591bd))
* **validate-data:** make name property shapes for ontology properties instead of blank nodes ([#1537](https://github.com/dasch-swiss/dsp-tools/issues/1537)) ([3452180](https://github.com/dasch-swiss/dsp-tools/commit/3452180ef8c5cfc01f3b5c784c8c10dbef41b01d))
* **validate-data:** make order of information in turtle files consistent ([#1532](https://github.com/dasch-swiss/dsp-tools/issues/1532)) ([146d217](https://github.com/dasch-swiss/dsp-tools/commit/146d21744be9c2216f081454c62dfa37a68eccff))
* **validate-data:** move `FileValue` cardinalities ([#1535](https://github.com/dasch-swiss/dsp-tools/issues/1535)) ([da4a933](https://github.com/dasch-swiss/dsp-tools/commit/da4a933495b81e4eb7d1f2b24f3e72ca950a34e4))
* **validate-data:** re-organise SHACL property shapes of dsp in-built resources ([#1540](https://github.com/dasch-swiss/dsp-tools/issues/1540)) ([d00bb3a](https://github.com/dasch-swiss/dsp-tools/commit/d00bb3ae863b4fab9a9306c08c756bc632374a76))
* **validate-data:** remove duplication of file value errors ([#1527](https://github.com/dasch-swiss/dsp-tools/issues/1527)) ([a9fb0d1](https://github.com/dasch-swiss/dsp-tools/commit/a9fb0d1c2e4b96d6dd8ede211fabd90164e2c3d2))
* **validate-data:** rename class parameter ([#1523](https://github.com/dasch-swiss/dsp-tools/issues/1523)) ([67be1b6](https://github.com/dasch-swiss/dsp-tools/commit/67be1b663430c0590844a948ba00d993aef51102))
* **validate-data:** validate metadata of values directly on the value ([#1533](https://github.com/dasch-swiss/dsp-tools/issues/1533)) ([5e56bc4](https://github.com/dasch-swiss/dsp-tools/commit/5e56bc4587f051612f5a2e3e52cae07e00ea87fa))
* **xmllib:** don't manually interfere with xml serialisation (DEV-4230) ([#1503](https://github.com/dasch-swiss/dsp-tools/issues/1503)) ([50c4c67](https://github.com/dasch-swiss/dsp-tools/commit/50c4c67c26b2d36e3cb81c498b9b739973540a32))
* **xmlupload:** reorganise functions to create the upload order ([#1552](https://github.com/dasch-swiss/dsp-tools/issues/1552)) ([4db08fe](https://github.com/dasch-swiss/dsp-tools/commit/4db08fe697ebd9608ae9fa290887b97f8aba0f79))
* **xmlupload:** take apart the function to create the upload state ([#1549](https://github.com/dasch-swiss/dsp-tools/issues/1549)) ([756e633](https://github.com/dasch-swiss/dsp-tools/commit/756e633d179eb6e2afe5189438c395fa318bc416))


### Documentation

* add deprecation notes with admonitions ([#1514](https://github.com/dasch-swiss/dsp-tools/issues/1514)) ([c95947d](https://github.com/dasch-swiss/dsp-tools/commit/c95947d52f052669ae8fef54f271e33682eea6bc))
* communicate supported Python versions (DEV-4680) ([#1515](https://github.com/dasch-swiss/dsp-tools/issues/1515)) ([6f4ab31](https://github.com/dasch-swiss/dsp-tools/commit/6f4ab31f637aac2c9108a947388f73cae176759f))
* **xmlupload:** describe how to add authorship data ([#1542](https://github.com/dasch-swiss/dsp-tools/issues/1542)) ([005bcb3](https://github.com/dasch-swiss/dsp-tools/commit/005bcb3da09591877c544e6be2d36457ea8547a7))

## [10.6.0](https://github.com/dasch-swiss/dsp-tools/compare/v10.5.0...v10.6.0) (2025-03-05)


### Enhancements

* **validate-data:** validate if legal info exists for images (DEV-4655) ([#1490](https://github.com/dasch-swiss/dsp-tools/issues/1490)) ([4fdf287](https://github.com/dasch-swiss/dsp-tools/commit/4fdf287f0eb64bdacb434b4eae417536d8ab65d6))
* **validate-data:** validate if legal info is there for files (DEV-4654) ([#1487](https://github.com/dasch-swiss/dsp-tools/issues/1487)) ([6ff6d3f](https://github.com/dasch-swiss/dsp-tools/commit/6ff6d3fca845b7cf5c0512a093ad5e95b7b86553))
* **xmlupload:** add `LegalInfoClient` to post copyright holders (DEV-4639) ([#1478](https://github.com/dasch-swiss/dsp-tools/issues/1478)) ([a4f9e6d](https://github.com/dasch-swiss/dsp-tools/commit/a4f9e6d5bf698fbc6180d74267af0db0161ab906))
* **xmlupload:** integrate create copyright holders into xmlupload (DEV-4650) ([#1485](https://github.com/dasch-swiss/dsp-tools/issues/1485)) ([7a3aba5](https://github.com/dasch-swiss/dsp-tools/commit/7a3aba51394852ce5364145b8d6f2cc732f1919d))
* **xmlupload:** map authorship ids to actual values (DEV-4637) ([#1476](https://github.com/dasch-swiss/dsp-tools/issues/1476)) ([99cfaee](https://github.com/dasch-swiss/dsp-tools/commit/99cfaee212348eaa52cdb7d21c99d2b121552378))
* **xmlupload:** parse legal info for files from XML (DEV-4635) ([#1473](https://github.com/dasch-swiss/dsp-tools/issues/1473)) ([ef6df7f](https://github.com/dasch-swiss/dsp-tools/commit/ef6df7fd60db6bad870c782b4fc73533e9a2bcf1))
* **xmlupload:** Upload the legal info of the file values during the xmlupload (DEV-4638) ([#1484](https://github.com/dasch-swiss/dsp-tools/issues/1484)) ([29e59b5](https://github.com/dasch-swiss/dsp-tools/commit/29e59b58411b254bbce506bfd8d2d1fc13ebf1e0))


### Bug Fixes

* **validate-data:** add problem message to csv (DEV-4663) ([#1493](https://github.com/dasch-swiss/dsp-tools/issues/1493)) ([63c587f](https://github.com/dasch-swiss/dsp-tools/commit/63c587f6adf0fd8f4a6f7819f861f7c5cdb49bc1))
* **xmllib:** allow pathlib.Path as input for Resource.add_file() ([#1486](https://github.com/dasch-swiss/dsp-tools/issues/1486)) ([63d5fd6](https://github.com/dasch-swiss/dsp-tools/commit/63d5fd602a6dd8c3383d4b237fa6d36fc24fbdbc))
* **xmllib:** disallow colon as range separator in find_date_in_string() ([#1480](https://github.com/dasch-swiss/dsp-tools/issues/1480)) ([a908714](https://github.com/dasch-swiss/dsp-tools/commit/a90871426998459b4614a85673d94731565bf2ba))
* **xmllib:** is_nonempty_value(" ") should be false ([#1474](https://github.com/dasch-swiss/dsp-tools/issues/1474)) ([2550e80](https://github.com/dasch-swiss/dsp-tools/commit/2550e803f5fe4957d7712d1d6dde8d9bec139a39))
* **xmlupload:** communicate invalid filename ([#1497](https://github.com/dasch-swiss/dsp-tools/issues/1497)) ([1557894](https://github.com/dasch-swiss/dsp-tools/commit/1557894d59010af618f6519b7b2a5409a02b72b3))
* **xmlupload:** text encoding check should handle onto prefix in text properties (DEV-4664) ([#1495](https://github.com/dasch-swiss/dsp-tools/issues/1495)) ([e218b3b](https://github.com/dasch-swiss/dsp-tools/commit/e218b3b7f1436f636ffa03572337e6374ec22030))


### Maintenance

* bump stack to 2025.03.01 ([#1491](https://github.com/dasch-swiss/dsp-tools/issues/1491)) ([64b87e0](https://github.com/dasch-swiss/dsp-tools/commit/64b87e00bb2165fff0674c38a8b9372ed83822bc))
* fix typo ([#1489](https://github.com/dasch-swiss/dsp-tools/issues/1489)) ([e52c9bf](https://github.com/dasch-swiss/dsp-tools/commit/e52c9bf6e3646898fda1fa9ae00bbaac2882753a))
* move generic and static logging functions out from `ConnectionLive` to separate file ([#1479](https://github.com/dasch-swiss/dsp-tools/issues/1479)) ([2dd238a](https://github.com/dasch-swiss/dsp-tools/commit/2dd238a42996102ccb3933914c798c6c5031c8a3))
* move logging of request out of `ConnectionLive` into generic file ([#1482](https://github.com/dasch-swiss/dsp-tools/issues/1482)) ([9250b01](https://github.com/dasch-swiss/dsp-tools/commit/9250b01517b24b2e53bd38211ee590e6fea55403))
* use simpler loguru syntax (DEV-4615) ([#1501](https://github.com/dasch-swiss/dsp-tools/issues/1501)) ([9c7dbf8](https://github.com/dasch-swiss/dsp-tools/commit/9c7dbf88716f3d63cde50542a497def916b9f9bd))
* **validate-data:** add legal info to the validation ([#1488](https://github.com/dasch-swiss/dsp-tools/issues/1488)) ([209a1d1](https://github.com/dasch-swiss/dsp-tools/commit/209a1d19b818d0bd835691c0f733b0ac1c6662ad))
* **xmlupload:** make error handling clearer/simpler ([#1500](https://github.com/dasch-swiss/dsp-tools/issues/1500)) ([6199201](https://github.com/dasch-swiss/dsp-tools/commit/619920111f96ec661aa6f6026f0f61e33c775dd3))
* **xmlupload:** make file value graph ([#1483](https://github.com/dasch-swiss/dsp-tools/issues/1483)) ([689c0c8](https://github.com/dasch-swiss/dsp-tools/commit/689c0c873113c156481e0d6af2e1a672409f90f9))


### Documentation

* **xmllib:** clarify that find_date_in_string() finds only 1 date ([#1477](https://github.com/dasch-swiss/dsp-tools/issues/1477)) ([b4210dc](https://github.com/dasch-swiss/dsp-tools/commit/b4210dcf74dfd5db48da0b5ceba27601f37f812f))

## [10.5.0](https://github.com/dasch-swiss/dsp-tools/compare/v10.4.0...v10.5.0) (2025-02-26)


### Enhancements

* allow legal info in XML (DEV-4599) ([#1431](https://github.com/dasch-swiss/dsp-tools/issues/1431)) ([c3f1b15](https://github.com/dasch-swiss/dsp-tools/commit/c3f1b154f310fe14db497369d64ead746c3ef89a))
* parse migration metadata in `DataDeserialised` (DEV-4612) ([#1457](https://github.com/dasch-swiss/dsp-tools/issues/1457)) ([412a747](https://github.com/dasch-swiss/dsp-tools/commit/412a7477defbbb50b395bf67cab3f03badff0c6c))
* **xmllib:** implement license and copyright (DEV-4354) ([#1427](https://github.com/dasch-swiss/dsp-tools/issues/1427)) ([f48b827](https://github.com/dasch-swiss/dsp-tools/commit/f48b8277bfe38f49943c7f0d2633df35329dded4))
* **xmllib:** support "15 Jan 2025" in find_date_in_string() (RDU-75) ([#1461](https://github.com/dasch-swiss/dsp-tools/issues/1461)) ([1b17163](https://github.com/dasch-swiss/dsp-tools/commit/1b17163027ab4efd361645b21002fe4693b903db))
* **xmllib:** support german month names in find_date_in_string() (RDU-76) ([#1462](https://github.com/dasch-swiss/dsp-tools/issues/1462)) ([81aa0b9](https://github.com/dasch-swiss/dsp-tools/commit/81aa0b96b6b51c7788c7120daa61a81906f45391))
* **xmlupload:** change name of id2iri mapping file (DEV-4601) ([#1438](https://github.com/dasch-swiss/dsp-tools/issues/1438)) ([dd079ff](https://github.com/dasch-swiss/dsp-tools/commit/dd079fff12c1c22db58becf5937b8c449bca9fd9))


### Bug Fixes

* **excel2xml:** filter out blanks-only strings from create_json_excel_list_mapping() ([#1472](https://github.com/dasch-swiss/dsp-tools/issues/1472)) ([8ba9a18](https://github.com/dasch-swiss/dsp-tools/commit/8ba9a186ded6c519f8687dde29bf143c9943ba35))
* **xmllib:** don't spam user with dsp-tools internal logging/printing (DEV-4595) ([#1430](https://github.com/dasch-swiss/dsp-tools/issues/1430)) ([e7f6449](https://github.com/dasch-swiss/dsp-tools/commit/e7f644901febdbf73c4f0d0c2cf3dd3fa33205f9))
* **xmllib:** don't spam user with dsp-tools internal logging/printing, the second (DEV-4595) ([#1459](https://github.com/dasch-swiss/dsp-tools/issues/1459)) ([9b0847a](https://github.com/dasch-swiss/dsp-tools/commit/9b0847a0e504e334def6ead6ea78bd7f7c4dc89c))
* **xmllib:** fix authorship block ([#1460](https://github.com/dasch-swiss/dsp-tools/issues/1460)) ([a32f0af](https://github.com/dasch-swiss/dsp-tools/commit/a32f0af3dd0b3517c34590776ff6c6426a10729c))


### Maintenance

* add a UUID to the `ValueInformation` when parsing the XML (DEV-4617) ([#1458](https://github.com/dasch-swiss/dsp-tools/issues/1458)) ([b908d48](https://github.com/dasch-swiss/dsp-tools/commit/b908d48eadfe787a14ada3be857e2eac985cb0c7))
* bump dependencies ([#1432](https://github.com/dasch-swiss/dsp-tools/issues/1432)) ([cd703e8](https://github.com/dasch-swiss/dsp-tools/commit/cd703e8cfc04d22211e760dafd5647b84abccc9f))
* bump stack to DSP 2025.02.03 ([#1440](https://github.com/dasch-swiss/dsp-tools/issues/1440)) ([fb7ff98](https://github.com/dasch-swiss/dsp-tools/commit/fb7ff984b7d7d0792b45858d3cdbdcef2becf6aa))
* bump versions of GitHub actions ([#1433](https://github.com/dasch-swiss/dsp-tools/issues/1433)) ([3eb0be9](https://github.com/dasch-swiss/dsp-tools/commit/3eb0be9b727ed6d907b45d0aa33add965bfaad79))
* **create:** change structure of parsed project ([#1425](https://github.com/dasch-swiss/dsp-tools/issues/1425)) ([1a360fb](https://github.com/dasch-swiss/dsp-tools/commit/1a360fbd7c8faee64d57ea5200cd1fb02da8a279))
* **create:** move ontology creation to separate file ([#1426](https://github.com/dasch-swiss/dsp-tools/issues/1426)) ([3e4f23f](https://github.com/dasch-swiss/dsp-tools/commit/3e4f23f967314333e7d4d21fc9f2b5c8b8f31823))
* **create:** reorganise code ([#1424](https://github.com/dasch-swiss/dsp-tools/issues/1424)) ([decfa24](https://github.com/dasch-swiss/dsp-tools/commit/decfa242150bc2d82a7ce83f6f9adc4ab6731135))
* enable darglint only in `xmllib` ([#1449](https://github.com/dasch-swiss/dsp-tools/issues/1449)) ([dc91e54](https://github.com/dasch-swiss/dsp-tools/commit/dc91e5467a2af4446d412a70ba3af7d30e676882))
* fix too many blank lines for test-latest-be.yml ([#1429](https://github.com/dasch-swiss/dsp-tools/issues/1429)) ([28d36ec](https://github.com/dasch-swiss/dsp-tools/commit/28d36ececa7d072f434c34232e56ef74a5f4a888))
* move typing-extensions to dev-dependencies ([#1436](https://github.com/dasch-swiss/dsp-tools/issues/1436)) ([86f3415](https://github.com/dasch-swiss/dsp-tools/commit/86f3415d28a9ccd59d9996f3fef21a5ad7e3e2d2))
* move xml parsing and validation files ([#1445](https://github.com/dasch-swiss/dsp-tools/issues/1445)) ([7cd763f](https://github.com/dasch-swiss/dsp-tools/commit/7cd763fd0c2cf91d31f879b1ed5734f9920b08da))
* **release-please:** update uv.lock automatically (DEV-4596) ([#1435](https://github.com/dasch-swiss/dsp-tools/issues/1435)) ([5adaf04](https://github.com/dasch-swiss/dsp-tools/commit/5adaf04242b1b5818c0da4a06dcf5195361d8e1f))
* **release-please:** update uv.lock automatically, 2nd attempt (DEV-4596) ([#1446](https://github.com/dasch-swiss/dsp-tools/issues/1446)) ([4bdac59](https://github.com/dasch-swiss/dsp-tools/commit/4bdac598eebf94d5466c1f177fd1008e850bdaa0))
* **release-please:** update uv.lock automatically, 3rd attempt (DEV-4596) ([#1453](https://github.com/dasch-swiss/dsp-tools/issues/1453)) ([33842e4](https://github.com/dasch-swiss/dsp-tools/commit/33842e4347e83dbf19623669b198997df379e0b5))
* remove copyright and license tags from xsd ([#1423](https://github.com/dasch-swiss/dsp-tools/issues/1423)) ([6bdf2c6](https://github.com/dasch-swiss/dsp-tools/commit/6bdf2c60164cdf9aad98a7eb83bfe14e3cb1bd21))
* remove redundant text encoding check ([#1452](https://github.com/dasch-swiss/dsp-tools/issues/1452)) ([d504513](https://github.com/dasch-swiss/dsp-tools/commit/d5045134ba10dcffd02e05c60599321d072fced0))
* reorganise XML cleaning functions ([#1456](https://github.com/dasch-swiss/dsp-tools/issues/1456)) ([da07379](https://github.com/dasch-swiss/dsp-tools/commit/da07379240feaf9484169b2d054ccb16f0d5768d))
* separate asset value from others in deserialise xml (DEV-4610) ([#1448](https://github.com/dasch-swiss/dsp-tools/issues/1448)) ([b7467d8](https://github.com/dasch-swiss/dsp-tools/commit/b7467d8929d0ad4e152fc31f399bacad71bd21ec))
* unpin dependencies ([#1439](https://github.com/dasch-swiss/dsp-tools/issues/1439)) ([4a88d10](https://github.com/dasch-swiss/dsp-tools/commit/4a88d10fbbb634df4028cbe29e22e10215b58118))
* Update uv.lock after version pinning is removed from pyproject.toml ([#1441](https://github.com/dasch-swiss/dsp-tools/issues/1441)) ([db5c1ee](https://github.com/dasch-swiss/dsp-tools/commit/db5c1eefef91b86901ca45cfba8a808b5af9792d))
* Update uv.lock with new version number ([#1421](https://github.com/dasch-swiss/dsp-tools/issues/1421)) ([e049458](https://github.com/dasch-swiss/dsp-tools/commit/e04945888442100c57ac20fef738e25f24201be9))
* **validate-data:** move parsing files to utils ([#1447](https://github.com/dasch-swiss/dsp-tools/issues/1447)) ([a61d7b6](https://github.com/dasch-swiss/dsp-tools/commit/a61d7b6c9fa06706d4df9d4c0ee7a0d2660f097c))
* **xmllib:** move file value serialisation out of the classes ([#1434](https://github.com/dasch-swiss/dsp-tools/issues/1434)) ([51b0414](https://github.com/dasch-swiss/dsp-tools/commit/51b04144f8d3b0dae298cf982ff8bcebcb8773f4))
* **xmllib:** move resource serialisation out of the class ([#1437](https://github.com/dasch-swiss/dsp-tools/issues/1437)) ([e52539e](https://github.com/dasch-swiss/dsp-tools/commit/e52539e4f7659dd4bb99607ff61dd649224dde31))
* **xmlupload:** create `Stash` from `IntermediaryResource` ([#1467](https://github.com/dasch-swiss/dsp-tools/issues/1467)) ([96afbc2](https://github.com/dasch-swiss/dsp-tools/commit/96afbc2aa34b5cd1da7398a599a996efe42b0bae))
* **xmlupload:** create info for graph from `DataDeserialised` (DEV-4622) ([#1464](https://github.com/dasch-swiss/dsp-tools/issues/1464)) ([568f526](https://github.com/dasch-swiss/dsp-tools/commit/568f526ffd43faf21c94e37cd129cf139d191a26))
* **xmlupload:** extract information from graph from `IntermediaryResource` ([#1468](https://github.com/dasch-swiss/dsp-tools/issues/1468)) ([bb97e76](https://github.com/dasch-swiss/dsp-tools/commit/bb97e7672d5fc4b8b603cdd9f7036aeb96375f66))
* **xmlupload:** make listnode lookup congruent with `DataDeserialised` ([#1471](https://github.com/dasch-swiss/dsp-tools/issues/1471)) ([f3f784a](https://github.com/dasch-swiss/dsp-tools/commit/f3f784ac0a904250322656fee671b4d7771695f9))
* **xmlupload:** move resource transformation files ([#1469](https://github.com/dasch-swiss/dsp-tools/issues/1469)) ([c379a66](https://github.com/dasch-swiss/dsp-tools/commit/c379a66acfd2501a25a027aa85763349c5caa39d))
* **xmlupload:** move transformed resource into the `UploadState` ([#1444](https://github.com/dasch-swiss/dsp-tools/issues/1444)) ([47577c2](https://github.com/dasch-swiss/dsp-tools/commit/47577c2e31d805a7d1b41a8cfe7e6cc91d8bcda0))
* **xmlupload:** re-organise circular reference files ([#1463](https://github.com/dasch-swiss/dsp-tools/issues/1463)) ([92a4465](https://github.com/dasch-swiss/dsp-tools/commit/92a446521f61f670ae0a8d9fa9729d4f3f5a91cc))
* **xmlupload:** remove creation of UUID from circular references models constructor ([#1466](https://github.com/dasch-swiss/dsp-tools/issues/1466)) ([9cc0d80](https://github.com/dasch-swiss/dsp-tools/commit/9cc0d80c7a95f654c31a79d1a1d769a558e7e7a7))
* **xmlupload:** use `IntermediaryFileValue` for ingest upload ([#1443](https://github.com/dasch-swiss/dsp-tools/issues/1443)) ([c3c121e](https://github.com/dasch-swiss/dsp-tools/commit/c3c121e208d2f82ee774ec944669f95c313ce84c))
* **xmlupload:** wrap info for circular references in class ([#1465](https://github.com/dasch-swiss/dsp-tools/issues/1465)) ([258f871](https://github.com/dasch-swiss/dsp-tools/commit/258f8718068a8c88b8b1eee43476d74959c1155f))

## [10.4.0](https://github.com/dasch-swiss/dsp-tools/compare/v10.3.0...v10.4.0) (2025-02-12)


### Enhancements

* **excel2json:** allow list names to contain colons (DEV-4580) ([#1418](https://github.com/dasch-swiss/dsp-tools/issues/1418)) ([5007fb2](https://github.com/dasch-swiss/dsp-tools/commit/5007fb29185e4c7de2092409447825c48e31bc29))


### Maintenance

* bump stack to 2025.02.02 ([#1420](https://github.com/dasch-swiss/dsp-tools/issues/1420)) ([0ebe609](https://github.com/dasch-swiss/dsp-tools/commit/0ebe60938cf0d9865a6bee12f2b1ff09db727886))
* **optimise release process:** deduce api commit hash from version tag ([#1410](https://github.com/dasch-swiss/dsp-tools/issues/1410)) ([ee1b39e](https://github.com/dasch-swiss/dsp-tools/commit/ee1b39e82a06c66d4b394feb89f9fe4c232fdba9))
* **test:** don't print user facing warnings during test runs ([#1415](https://github.com/dasch-swiss/dsp-tools/issues/1415)) ([55bff2e](https://github.com/dasch-swiss/dsp-tools/commit/55bff2e07d58bef9b1907c55c80bf2dc8b37f1bb))
* Update uv.lock ([#1404](https://github.com/dasch-swiss/dsp-tools/issues/1404)) ([8e48113](https://github.com/dasch-swiss/dsp-tools/commit/8e481133a80e7213b8e368a1b1514ffb69888431))
* **validate-data:** class structure of `InputProblem` ([#1406](https://github.com/dasch-swiss/dsp-tools/issues/1406)) ([7c6b6a6](https://github.com/dasch-swiss/dsp-tools/commit/7c6b6a637b098d3c19428fe4d417e7319b9b2483))
* **validate-data:** harmonise datatype of `ValidationResult` parameters ([#1416](https://github.com/dasch-swiss/dsp-tools/issues/1416)) ([1ff12ac](https://github.com/dasch-swiss/dsp-tools/commit/1ff12ac055f8a14063b38525166188198d21c2fd))
* **validate-data:** make instance variable names uniform ([#1407](https://github.com/dasch-swiss/dsp-tools/issues/1407)) ([b02bd1e](https://github.com/dasch-swiss/dsp-tools/commit/b02bd1ee2680ff1878f93b0e043d746d12730749))
* **validate-data:** move mappers and constants to own file ([#1409](https://github.com/dasch-swiss/dsp-tools/issues/1409)) ([4057609](https://github.com/dasch-swiss/dsp-tools/commit/40576094e04c764d83ae3b0ceba551999893f2d4))
* **validate-data:** simplify cardinality message construction ([#1417](https://github.com/dasch-swiss/dsp-tools/issues/1417)) ([29bccf7](https://github.com/dasch-swiss/dsp-tools/commit/29bccf7b79a2dfd8ac80602ffe72df4e1e38c04d))
* **validate-data:** simplify mapping from violation to user facing problem ([#1411](https://github.com/dasch-swiss/dsp-tools/issues/1411)) ([06c0bc7](https://github.com/dasch-swiss/dsp-tools/commit/06c0bc70f7f8d89e87396b12dabacf07ede5b0dc))
* **validate-data:** simplify validation query class structure ([#1408](https://github.com/dasch-swiss/dsp-tools/issues/1408)) ([2319e6b](https://github.com/dasch-swiss/dsp-tools/commit/2319e6bddbee0d33e934c64bdae031e685658392))

## [10.3.0](https://github.com/dasch-swiss/dsp-tools/compare/v10.2.0...v10.3.0) (2025-02-05)


### Enhancements

* **start-stack:** remove special docker compose for validation (DEV-4548) ([#1386](https://github.com/dasch-swiss/dsp-tools/issues/1386)) ([a0f8116](https://github.com/dasch-swiss/dsp-tools/commit/a0f8116150e3185b8bae6b0feb3895c349c28d83))
* **validate-data:** add `AudioSegment` and `VideoSegment` (DEV-4464) ([#1384](https://github.com/dasch-swiss/dsp-tools/issues/1384)) ([0106a35](https://github.com/dasch-swiss/dsp-tools/commit/0106a351f0f69ea250b974b63cf2f8b8e47740ea))
* **validate-data:** add permissions cardinalities (DEV-4528) ([#1381](https://github.com/dasch-swiss/dsp-tools/issues/1381)) ([2534792](https://github.com/dasch-swiss/dsp-tools/commit/2534792f4dd1979b76c24d41125210f7c78dd4db))
* **validate-data:** validate target of stand-off links (DEV-4443) ([#1392](https://github.com/dasch-swiss/dsp-tools/issues/1392)) ([b37d43c](https://github.com/dasch-swiss/dsp-tools/commit/b37d43cfb08c3a9fc297ec64a0ae39b2f1f7f0f9))
* **xmllib:** add footnotes helper functions (DEV-4561) ([#1398](https://github.com/dasch-swiss/dsp-tools/issues/1398)) ([c53aca8](https://github.com/dasch-swiss/dsp-tools/commit/c53aca8060852aaecf4730387146cceb715a7c9a))
* **xmllib:** add helper function to create standoff link tags (DEV-4563) ([#1401](https://github.com/dasch-swiss/dsp-tools/issues/1401)) ([5714ba4](https://github.com/dasch-swiss/dsp-tools/commit/5714ba4a09cd6190ed89e59060b0ad2319e96c40))


### Bug Fixes

* **validate-data:** add correct query parameter for requesting lists (DEV-4550) ([#1388](https://github.com/dasch-swiss/dsp-tools/issues/1388)) ([443a8da](https://github.com/dasch-swiss/dsp-tools/commit/443a8da135017a0975b9b1cd819f0a03ba539941))
* **validate-data:** include LinkValueProperty in knora-subset and remove witespaces (DEV-4547) ([#1385](https://github.com/dasch-swiss/dsp-tools/issues/1385)) ([28699b6](https://github.com/dasch-swiss/dsp-tools/commit/28699b6dc78168d350ecf8d83f1bcdb831bdad08))


### Maintenance

* `just clean` removes also built documentation site ([#1402](https://github.com/dasch-swiss/dsp-tools/issues/1402)) ([9c9045d](https://github.com/dasch-swiss/dsp-tools/commit/9c9045de390a7bd5313b460a13b49856f8b7a78e))
* bump dsp-ingest to v0.18.1 ([#1403](https://github.com/dasch-swiss/dsp-tools/issues/1403)) ([cd01da7](https://github.com/dasch-swiss/dsp-tools/commit/cd01da7f0bea32ed0e7957844f81b3f4b804ad68))
* bump versions for 2025.02.01 ([#1394](https://github.com/dasch-swiss/dsp-tools/issues/1394)) ([dce7910](https://github.com/dasch-swiss/dsp-tools/commit/dce7910f6be638ae2a7d4d882af81526e78f676f))
* bump versions for 2025.02.01 [#2](https://github.com/dasch-swiss/dsp-tools/issues/2) ([#1397](https://github.com/dasch-swiss/dsp-tools/issues/1397)) ([7719419](https://github.com/dasch-swiss/dsp-tools/commit/771941993e235df37c84fe1135b880307dbb8b69))
* revert to previous version ([#1395](https://github.com/dasch-swiss/dsp-tools/issues/1395)) ([fd497ce](https://github.com/dasch-swiss/dsp-tools/commit/fd497ce2952de56c63c98f70da2261f8ad7b727d))
* Update uv.lock after new release ([#1382](https://github.com/dasch-swiss/dsp-tools/issues/1382)) ([60a963c](https://github.com/dasch-swiss/dsp-tools/commit/60a963cd51ca9ab9f5906d0df13b4a9a1a11de3f))
* **xmllib:** generalise escape reserved characters function ([#1400](https://github.com/dasch-swiss/dsp-tools/issues/1400)) ([2e57f4b](https://github.com/dasch-swiss/dsp-tools/commit/2e57f4b447026d134ac8ea3c025d0e68a6ad7035))


### Documentation

* **validate-data:** final notes of MVP ([#1396](https://github.com/dasch-swiss/dsp-tools/issues/1396)) ([4385d47](https://github.com/dasch-swiss/dsp-tools/commit/4385d4746207ad5b000378fe821b7e46332ad511))
* **validate-data:** write documentation (DEV-4532) ([#1387](https://github.com/dasch-swiss/dsp-tools/issues/1387)) ([30f822a](https://github.com/dasch-swiss/dsp-tools/commit/30f822ad7aca12e5b49343ed0e6a6d8aeaa2cbd7))

## [10.2.0](https://github.com/dasch-swiss/dsp-tools/compare/v10.1.1...v10.2.0) (2025-01-23)


### Enhancements

* **validate-data:** `seqnum` and `isPartOf` (DEV-4242) ([#1373](https://github.com/dasch-swiss/dsp-tools/issues/1373)) ([832fc4f](https://github.com/dasch-swiss/dsp-tools/commit/832fc4f875a99e835394d26a07900e5641236676))
* **validate-data:** improve performance time for SHACL construction (DEV-4523) ([#1378](https://github.com/dasch-swiss/dsp-tools/issues/1378)) ([a9bdaac](https://github.com/dasch-swiss/dsp-tools/commit/a9bdaac875fd90a3de279cf575ee9c661abf9b19))
* **validate-data:** prevent erroneous ontology for `seqnum` and `isPartOf`(DEV-4517) ([#1374](https://github.com/dasch-swiss/dsp-tools/issues/1374)) ([070fef7](https://github.com/dasch-swiss/dsp-tools/commit/070fef74a901054232abeb7433339273bc183a39))
* **validate-data:** validate `hasComment` on values (DEV-4472) ([#1371](https://github.com/dasch-swiss/dsp-tools/issues/1371)) ([33f6339](https://github.com/dasch-swiss/dsp-tools/commit/33f6339e90958dce92ece9dca6ef7e3957155f53))
* **validate-data:** validate `knora-api:Region` (DEV-4462) ([#1380](https://github.com/dasch-swiss/dsp-tools/issues/1380)) ([0b954d6](https://github.com/dasch-swiss/dsp-tools/commit/0b954d6a00a3d44aba2b53ba4ffcf815b82d32b5))


### Maintenance

* bump dependencies / fix new linter errors / format according to new formatter rules ([#1368](https://github.com/dasch-swiss/dsp-tools/issues/1368)) ([4d32cfb](https://github.com/dasch-swiss/dsp-tools/commit/4d32cfb58893a076270159ce13482f29b9571e5c))
* bump versions for 2025.01.02 DSP release ([#1379](https://github.com/dasch-swiss/dsp-tools/issues/1379)) ([65f57e8](https://github.com/dasch-swiss/dsp-tools/commit/65f57e8b6af53bf96b4d66901b5cc194caef54a9))
* upgrade `rdflib` and fix typing ([#1370](https://github.com/dasch-swiss/dsp-tools/issues/1370)) ([adbe88c](https://github.com/dasch-swiss/dsp-tools/commit/adbe88cfa1be54dae84261ae5f13e56e730396b9))
* **validate-data:** add logging ([#1377](https://github.com/dasch-swiss/dsp-tools/issues/1377)) ([92f36c7](https://github.com/dasch-swiss/dsp-tools/commit/92f36c7c5ace0180df5ac56a2fe6573d9111107d))
* **validate-data:** change SHACLValidator structure ([#1375](https://github.com/dasch-swiss/dsp-tools/issues/1375)) ([57df7eb](https://github.com/dasch-swiss/dsp-tools/commit/57df7ebb7e0f759af9ad6a5632c3ede0256cbd51))
* **validate-data:** improve user message ([#1363](https://github.com/dasch-swiss/dsp-tools/issues/1363)) ([77684f0](https://github.com/dasch-swiss/dsp-tools/commit/77684f08c954477acdd9353054f437d97e21a8c3))
* **validate-data:** simplify internal representation of file values ([#1367](https://github.com/dasch-swiss/dsp-tools/issues/1367)) ([c9665ca](https://github.com/dasch-swiss/dsp-tools/commit/c9665cae816ce913ea55b1367f5398a372b322bc))

## [10.1.1](https://github.com/dasch-swiss/dsp-tools/compare/v10.1.0...v10.1.1) (2025-01-15)


### Maintenance

* **validate-data:** simplify internal Python representation of values ([#1362](https://github.com/dasch-swiss/dsp-tools/issues/1362)) ([3058055](https://github.com/dasch-swiss/dsp-tools/commit/305805567f52f90ad11fc0f1d2995f4f0f4bd807))


### Documentation

* remove mermaid2 plugin ([#1365](https://github.com/dasch-swiss/dsp-tools/issues/1365)) ([c126b13](https://github.com/dasch-swiss/dsp-tools/commit/c126b138b708bcd5fef2152626fc2561d5756fa5))

## [10.1.0](https://github.com/dasch-swiss/dsp-tools/compare/v10.0.0...v10.1.0) (2025-01-15)


### Enhancements

* **xmllib:** dsp-base resources: add checks and improve robustness of serialisation (DEV-4485) ([#1354](https://github.com/dasch-swiss/dsp-tools/issues/1354)) ([5b20bc0](https://github.com/dasch-swiss/dsp-tools/commit/5b20bc091be4bef06d642ab4f2d3baea1255c003))
* **xmllib:** make checks for non-empty input consistent (DEV-4435) ([#1353](https://github.com/dasch-swiss/dsp-tools/issues/1353)) ([0acc6dd](https://github.com/dasch-swiss/dsp-tools/commit/0acc6ddcb480ca1c0b3fcd1a092dbaf73bf60403))


### Maintenance

* bump start-stack to 2025.01.01 ([#1364](https://github.com/dasch-swiss/dsp-tools/issues/1364)) ([35d0e8f](https://github.com/dasch-swiss/dsp-tools/commit/35d0e8ffe1c48e99e56dfcc95129e08134ae60f3))
* upgrade `rdflib` dependency ([#1351](https://github.com/dasch-swiss/dsp-tools/issues/1351)) ([58ff473](https://github.com/dasch-swiss/dsp-tools/commit/58ff47380337dc66021d0a34bfddadbbf88eb8c3))
* **upload-files:** stream big files (DEV-4469) ([#1335](https://github.com/dasch-swiss/dsp-tools/issues/1335)) ([201c515](https://github.com/dasch-swiss/dsp-tools/commit/201c51541ff9c0cd638532d8f5043385c4d284c0))
* **validate-data:** consolidate constants ([#1358](https://github.com/dasch-swiss/dsp-tools/issues/1358)) ([b60a40f](https://github.com/dasch-swiss/dsp-tools/commit/b60a40f11054ec45d024d12131bfc588c644c1a3))
* **validate-data:** make structure of deserialised dataclasses more generic ([#1360](https://github.com/dasch-swiss/dsp-tools/issues/1360)) ([5563ee0](https://github.com/dasch-swiss/dsp-tools/commit/5563ee0558c585949369af9bf31b1b219ba63fd6))
* **xmllib:** simplify serialisation of values ([#1355](https://github.com/dasch-swiss/dsp-tools/issues/1355)) ([895274b](https://github.com/dasch-swiss/dsp-tools/commit/895274b9a6a634b728946851a952b157812cc262))


### Documentation

* fix mermaid rendering ([#1361](https://github.com/dasch-swiss/dsp-tools/issues/1361)) ([d1eaed6](https://github.com/dasch-swiss/dsp-tools/commit/d1eaed6a0ba339e11bd28db46300cfc1d6877557))

## [10.0.0](https://github.com/dasch-swiss/dsp-tools/compare/v9.2.0...v10.0.0) (2024-12-18)


### ⚠ BREAKING CHANGES

* remove support for knora-base:Annotation (DEV-4430) ([#1314](https://github.com/dasch-swiss/dsp-tools/issues/1314))

### Enhancements

* remove support for knora-base:Annotation (DEV-4430) ([#1314](https://github.com/dasch-swiss/dsp-tools/issues/1314)) ([469473a](https://github.com/dasch-swiss/dsp-tools/commit/469473a66be630423b85a947dbd6dcbe4e903287))
* **validate-data:** `knora-api:LinkObj` (DEV-4463) ([#1342](https://github.com/dasch-swiss/dsp-tools/issues/1342)) ([f9dee0f](https://github.com/dasch-swiss/dsp-tools/commit/f9dee0f220be4c279d93c1c2f0895860a04d28f6))
* **validate-data:** change message for files added to resources without representation (DEV-4453) ([#1333](https://github.com/dasch-swiss/dsp-tools/issues/1333)) ([738ad7f](https://github.com/dasch-swiss/dsp-tools/commit/738ad7f867c2b8743898ddc2be84919269219c67))
* **validate-data:** validate `DocumentRepresentation`, `ArchiveRepresentation`, `TextRepresentation` (DEV-4334) ([#1331](https://github.com/dasch-swiss/dsp-tools/issues/1331)) ([c3d69d2](https://github.com/dasch-swiss/dsp-tools/commit/c3d69d2fefb8eabe5ac06b3878ff8e1e3651c2e6))
* **validate-data:** validate `StillImageRepresentation` (DEV-4336) ([#1330](https://github.com/dasch-swiss/dsp-tools/issues/1330)) ([15cdf26](https://github.com/dasch-swiss/dsp-tools/commit/15cdf2658c10f7cee3aeb636067b3c9631ea5a7f))
* **validate-data:** validate AudioFileValue (DEV-4332) ([#1326](https://github.com/dasch-swiss/dsp-tools/issues/1326)) ([e0988c6](https://github.com/dasch-swiss/dsp-tools/commit/e0988c6a5d99b50190372ce0f23ade810eafe92b))
* **xmllib:** add examples to docstrings (DEV-4423) ([#1316](https://github.com/dasch-swiss/dsp-tools/issues/1316)) ([bfbc2ed](https://github.com/dasch-swiss/dsp-tools/commit/bfbc2edefa05589f3de32a57a97a429d5ab7820d))
* **xmllib:** ensure that non-empty lists are found during add multiple values (DEV-4421) ([#1311](https://github.com/dasch-swiss/dsp-tools/issues/1311)) ([44b1418](https://github.com/dasch-swiss/dsp-tools/commit/44b1418f3fb7e340055fd1ff5beaf7c5bb716799))
* **xmllib:** expose lib through init and enable colored printing (RDU-39) ([#1315](https://github.com/dasch-swiss/dsp-tools/issues/1315)) ([c5f594d](https://github.com/dasch-swiss/dsp-tools/commit/c5f594d202ffda3ff3294638386b870ab76e927b))
* **xmllib:** remove `add_comment` method from base resources if they are mandatory (DEV-4415) ([#1307](https://github.com/dasch-swiss/dsp-tools/issues/1307)) ([fc0f143](https://github.com/dasch-swiss/dsp-tools/commit/fc0f143ee472b5d14202873e13660a270a6b07ba))
* **xmllib:** simplify creation of geometry-prop with classes (RDU-55) ([#1300](https://github.com/dasch-swiss/dsp-tools/issues/1300)) ([b8fb42f](https://github.com/dasch-swiss/dsp-tools/commit/b8fb42f84d87a2ffcd5d5c6c8445ea16b13e9d72))
* **xmlupload:** add license / copyright as optional attributes in `iiif-uri` and `bitstream` (DEV-4355) ([#1293](https://github.com/dasch-swiss/dsp-tools/issues/1293)) ([d401a49](https://github.com/dasch-swiss/dsp-tools/commit/d401a4927fa11d13742834973503667512df487d))


### Bug Fixes

* **ingest-xmlupload:** remove leading slash ([#1321](https://github.com/dasch-swiss/dsp-tools/issues/1321)) ([ca3b2aa](https://github.com/dasch-swiss/dsp-tools/commit/ca3b2aa510e9354c23564f50a48cc8cb3ceaffa6))
* remove wrong min cardinality for `hasComment` in `LinkObj`(DEV-4465) ([#1343](https://github.com/dasch-swiss/dsp-tools/issues/1343)) ([0f0aa2e](https://github.com/dasch-swiss/dsp-tools/commit/0f0aa2e2ef603c97dfc7a873e9cc5f4bd3e08386))
* **start-stack:** allow erasing project on localhost (DEV-4422) ([#1338](https://github.com/dasch-swiss/dsp-tools/issues/1338)) ([0783bde](https://github.com/dasch-swiss/dsp-tools/commit/0783bdebe67588cb70b47997ed6d61086c09d815))
* **validate-data:** ensure turtle files are in the distribution (DEV-4423) ([#1313](https://github.com/dasch-swiss/dsp-tools/issues/1313)) ([37846cf](https://github.com/dasch-swiss/dsp-tools/commit/37846cfbabcba197375b956521fffe721318842e))
* **validate-data:** message of LinkValue in SHACL (DEV-4471) ([#1344](https://github.com/dasch-swiss/dsp-tools/issues/1344)) ([b90f043](https://github.com/dasch-swiss/dsp-tools/commit/b90f043a90c14ef870dc1d94ed57fdf87adff0a8))
* **xmllib:** allow single quotes and plus in URI ([#1332](https://github.com/dasch-swiss/dsp-tools/issues/1332)) ([8285bb3](https://github.com/dasch-swiss/dsp-tools/commit/8285bb336a19577cad8a4c4610ac9d3aed77c397))
* **xmllib:** check if richtext input is string like before value conversion (DEV-4418) ([#1308](https://github.com/dasch-swiss/dsp-tools/issues/1308)) ([5d35058](https://github.com/dasch-swiss/dsp-tools/commit/5d350587122c9ca8f4068ed0b3697642bcc9db87))
* **xmllib:** correct `LinkObj` cardinalities according to `knora-base` (DEV-4434) ([#1317](https://github.com/dasch-swiss/dsp-tools/issues/1317)) ([144d779](https://github.com/dasch-swiss/dsp-tools/commit/144d779298b2a1135030a348e51fb53c6217af16))
* **xmllib:** don't crash if comment input is `nan` (DEV-4399) ([#1297](https://github.com/dasch-swiss/dsp-tools/issues/1297)) ([d16769f](https://github.com/dasch-swiss/dsp-tools/commit/d16769f206353d56801e317fd5aa246c3a56bc56))
* **xmllib:** parse richtext correctly (DEV-4419) ([#1309](https://github.com/dasch-swiss/dsp-tools/issues/1309)) ([5a9d9e7](https://github.com/dasch-swiss/dsp-tools/commit/5a9d9e7fbe3998efb6b865eea17dbc4d11472723))
* **xmllib:** remove outdated information in docstring (RDU-66) ([#1347](https://github.com/dasch-swiss/dsp-tools/issues/1347)) ([ac36864](https://github.com/dasch-swiss/dsp-tools/commit/ac36864821b322ddb5f4c65a331db98ee69df64e))
* **xmlupload:** inform user if resource transformation failed (DEV-4456) ([#1336](https://github.com/dasch-swiss/dsp-tools/issues/1336)) ([c797d78](https://github.com/dasch-swiss/dsp-tools/commit/c797d787153737b8f74a111fc26f160f1f5f8325))
* **xmlupload:** stop complete crash if an error ocurrs during serialisation (DEV-4419) ([#1310](https://github.com/dasch-swiss/dsp-tools/issues/1310)) ([88b8350](https://github.com/dasch-swiss/dsp-tools/commit/88b83506f836d34f13fefc79ead92d70d6092be6))


### Maintenance

* bump start-stack to 2024.12.01 ([#1329](https://github.com/dasch-swiss/dsp-tools/issues/1329)) ([502b9f9](https://github.com/dasch-swiss/dsp-tools/commit/502b9f9b8515afb53b471367cabad23b2b6f11eb))
* **just:** `just clean`: ignore errors ([#1334](https://github.com/dasch-swiss/dsp-tools/issues/1334)) ([4c0df87](https://github.com/dasch-swiss/dsp-tools/commit/4c0df8729de6f40d98a1f518ac61e3f64a4a1c8a))
* upgrade deps / fix new typing errors of types-lxml / resolve 1 warning ([#1323](https://github.com/dasch-swiss/dsp-tools/issues/1323)) ([7253422](https://github.com/dasch-swiss/dsp-tools/commit/725342219460682fdc1d4be8624b74668ee6fafe))
* **validate-data:** change deserialisation in preparation for dsp in-built resource validation ([#1340](https://github.com/dasch-swiss/dsp-tools/issues/1340)) ([fd92906](https://github.com/dasch-swiss/dsp-tools/commit/fd929067d22d42ee35896a7529791f71d3f5ef6a))
* **validate-data:** change exclusion of properties from gui-order to `isEditable` (DEV-4281) ([#1337](https://github.com/dasch-swiss/dsp-tools/issues/1337)) ([d8867cd](https://github.com/dasch-swiss/dsp-tools/commit/d8867cd0c1c24772daf6e2e6188215d84fe8c5d2))
* **validate-data:** change graph creation ([#1346](https://github.com/dasch-swiss/dsp-tools/issues/1346)) ([c0435bd](https://github.com/dasch-swiss/dsp-tools/commit/c0435bd298c4da41c356357eca46c018acba8639))
* **validate-data:** rename cardinality turtle file ([#1341](https://github.com/dasch-swiss/dsp-tools/issues/1341)) ([acfd1f1](https://github.com/dasch-swiss/dsp-tools/commit/acfd1f11d4da3e9ad87ea7029222cec96bafbb4a))
* **xmllib:** change boolean conversion ([#1324](https://github.com/dasch-swiss/dsp-tools/issues/1324)) ([363fbb6](https://github.com/dasch-swiss/dsp-tools/commit/363fbb6e02d8f859764c50cfe5626dee886458ff))
* **xmlupload:** adapt intermediary resource transformation ([#1319](https://github.com/dasch-swiss/dsp-tools/issues/1319)) ([087ac5e](https://github.com/dasch-swiss/dsp-tools/commit/087ac5ec87a557055ab5dabd1bdb2f29344e4aee))
* **xmlupload:** allow pretty printing bitstream and iiif-uri (DEV-4404) ([#1306](https://github.com/dasch-swiss/dsp-tools/issues/1306)) ([0e46387](https://github.com/dasch-swiss/dsp-tools/commit/0e46387579f3feaa7d13ff065640f88361f058f2))
* **xmlupload:** correct `isSegmentOf` into the correct property name when parsing the XML ([#1305](https://github.com/dasch-swiss/dsp-tools/issues/1305)) ([a8098e8](https://github.com/dasch-swiss/dsp-tools/commit/a8098e837590f112217429df82f30725bfd251bb))
* **xmlupload:** create intermediary class structure for data ([#1304](https://github.com/dasch-swiss/dsp-tools/issues/1304)) ([207a04f](https://github.com/dasch-swiss/dsp-tools/commit/207a04f54014b9b08f003ed8741020652521ee3d))
* **xmlupload:** create resource with rdflib ([#1339](https://github.com/dasch-swiss/dsp-tools/issues/1339)) ([f5d66a5](https://github.com/dasch-swiss/dsp-tools/commit/f5d66a5a180b8b8563fe624623cdb2a47988c44c))
* **xmlupload:** group file for the preparation of an upload ([#1328](https://github.com/dasch-swiss/dsp-tools/issues/1328)) ([78717d3](https://github.com/dasch-swiss/dsp-tools/commit/78717d3ee39c8f20b3654918a671bbe0199dcf36))
* **xmlupload:** integrate intermediary class structure into upload ([#1320](https://github.com/dasch-swiss/dsp-tools/issues/1320)) ([9889219](https://github.com/dasch-swiss/dsp-tools/commit/9889219bb8b5262064c2e7f6d8c220a27e374055))
* **xmlupload:** serialise file values with rdflib ([#1288](https://github.com/dasch-swiss/dsp-tools/issues/1288)) ([e47d38c](https://github.com/dasch-swiss/dsp-tools/commit/e47d38c818fc221a1b9252564c369374f3ce0c2b))


### Documentation

* fix indentation and content of ingest-xmlupload ([#1301](https://github.com/dasch-swiss/dsp-tools/issues/1301)) ([d61d83f](https://github.com/dasch-swiss/dsp-tools/commit/d61d83f0c7b986aae2f1d0b0649258b1993e6d1c))
* **xmllib:** alphabetical ordering for non-classes ([#1292](https://github.com/dasch-swiss/dsp-tools/issues/1292)) ([09cda09](https://github.com/dasch-swiss/dsp-tools/commit/09cda093b7fbdb942492b8ed5e7057123d23b58d))
* **xmllib:** fix small mistakes ([#1312](https://github.com/dasch-swiss/dsp-tools/issues/1312)) ([6f8f526](https://github.com/dasch-swiss/dsp-tools/commit/6f8f526bf8fdaa5510805ca5a74353f35710b80a))

## [9.2.0](https://github.com/dasch-swiss/dsp-tools/compare/v9.1.0...v9.2.0) (2024-11-25)


### Enhancements

* allow uploading JSON files as assets (DEV-4327) ([#1267](https://github.com/dasch-swiss/dsp-tools/issues/1267)) ([8f6be06](https://github.com/dasch-swiss/dsp-tools/commit/8f6be06ee1f75eb63a26c929aecbb107805843a6))
* rename CLI command `xml-validate` to `validate-data` (DEV-4219) ([#1203](https://github.com/dasch-swiss/dsp-tools/issues/1203)) ([8c10f83](https://github.com/dasch-swiss/dsp-tools/commit/8c10f83f55fc306465b1c5a272c08d648cfcb2f8))
* **start-stack:** make api version necessary for validation accessible through a flag (DEV-4200) ([#1194](https://github.com/dasch-swiss/dsp-tools/issues/1194)) ([081a6f2](https://github.com/dasch-swiss/dsp-tools/commit/081a6f2af2c2569355ba2d17f36c3ccc24606438))
* **validate-data:** add unique value constraint (DEV-4202) ([#1236](https://github.com/dasch-swiss/dsp-tools/issues/1236)) ([595bb11](https://github.com/dasch-swiss/dsp-tools/commit/595bb116ac4493dc7963124a440f41cd41e82dbc))
* **validate-data:** check file value cardinality (DEV-4338) ([#1264](https://github.com/dasch-swiss/dsp-tools/issues/1264)) ([cefc466](https://github.com/dasch-swiss/dsp-tools/commit/cefc466b4301f8d85e89fc5cffd3e9bec6140329))
* **validate-data:** ensure only known resources are used (DEV-4268) ([#1263](https://github.com/dasch-swiss/dsp-tools/issues/1263)) ([dbbaefe](https://github.com/dasch-swiss/dsp-tools/commit/dbbaefe6c77d988e3367ca0ee3f697a84b796f6e))
* **validate-data:** make content validation conform with `dash` syntax (DEV-4233) ([#1211](https://github.com/dasch-swiss/dsp-tools/issues/1211)) ([2af7a69](https://github.com/dasch-swiss/dsp-tools/commit/2af7a69d60b9b1a63b246e1aa1d3985867e58e6d))
* **validate-data:** validate `MovingImageRepresentation` (DEV-4333) ([#1268](https://github.com/dasch-swiss/dsp-tools/issues/1268)) ([4594ff9](https://github.com/dasch-swiss/dsp-tools/commit/4594ff9d4ee3c52d8d935e42d4bf44ada790af99))
* **validate-data:** validate cardinality with `dash:closedByTypes` (DEV-4231) ([#1209](https://github.com/dasch-swiss/dsp-tools/issues/1209)) ([e883cbb](https://github.com/dasch-swiss/dsp-tools/commit/e883cbbf59fc5f3c27e9de3338ef67827d03e37f))
* **validate-data:** validate generic content of values (DEV-4225) ([#1208](https://github.com/dasch-swiss/dsp-tools/issues/1208)) ([86042ff](https://github.com/dasch-swiss/dsp-tools/commit/86042ffa6564e73e3b1ca4e39a17176f45c88a1b))
* **validate-data:** validate link value class type (DEV-4237) ([#1215](https://github.com/dasch-swiss/dsp-tools/issues/1215)) ([9e306c2](https://github.com/dasch-swiss/dsp-tools/commit/9e306c2954b25535b5417e12b4491e2d2d50b21f))
* **validate-data:** validate list nodes (DEV-4131) ([#1240](https://github.com/dasch-swiss/dsp-tools/issues/1240)) ([332387a](https://github.com/dasch-swiss/dsp-tools/commit/332387a1ab48cea0355340e671ce3e7b6602a986))
* **validate-data:** validate text value type (DEV-4209) ([#1205](https://github.com/dasch-swiss/dsp-tools/issues/1205)) ([cafca60](https://github.com/dasch-swiss/dsp-tools/commit/cafca60d1c77e56487370167539af36018be633e))
* **xmllib:** add `create_label_to_name_list_node_mapping()` to lib (DEV-4293) ([#1245](https://github.com/dasch-swiss/dsp-tools/issues/1245)) ([c0cdbeb](https://github.com/dasch-swiss/dsp-tools/commit/c0cdbebf63171397f585d66c013fb58ea1990a69))
* **xmllib:** add english and german to boolean value converter (DEV-4311) ([#1260](https://github.com/dasch-swiss/dsp-tools/issues/1260)) ([9b70810](https://github.com/dasch-swiss/dsp-tools/commit/9b70810c5c9fc9d83f13e38917ec1dcb0742fa82))
* **xmllib:** add factory method to resources (DEV-4189) ([#1185](https://github.com/dasch-swiss/dsp-tools/issues/1185)) ([99c76ea](https://github.com/dasch-swiss/dsp-tools/commit/99c76ea07de47327b58866e7188cac100194bfbc))
* **xmllib:** add helpers from `excel2xml` to `xmllib` (DEV-4316) ([#1261](https://github.com/dasch-swiss/dsp-tools/issues/1261)) ([fb88558](https://github.com/dasch-swiss/dsp-tools/commit/fb88558457515e50a79d774e2abab91187e05de9))
* **xmllib:** add migration metadata to resources (DEV-4194) ([#1190](https://github.com/dasch-swiss/dsp-tools/issues/1190)) ([1784065](https://github.com/dasch-swiss/dsp-tools/commit/1784065118328a13a45931a390975160d06bc606))
* **xmllib:** add optional value to dsp base resource (DEV-4289) ([#1244](https://github.com/dasch-swiss/dsp-tools/issues/1244)) ([ef309ba](https://github.com/dasch-swiss/dsp-tools/commit/ef309ba0b4f6fd64e919db94f770da8bec2565d2))
* **xmllib:** change order of parameters in add values (DEV-4255) ([#1232](https://github.com/dasch-swiss/dsp-tools/issues/1232)) ([44b3d44](https://github.com/dasch-swiss/dsp-tools/commit/44b3d44ecc10b5d2f465d641143ba48e6d6a9205))
* **xmllib:** check tags of richtext values (RDU-58) ([#1282](https://github.com/dasch-swiss/dsp-tools/issues/1282)) ([289251a](https://github.com/dasch-swiss/dsp-tools/commit/289251a80a926a0c9599c4666132a0fd7f333c77))
* **xmllib:** create permissions (DEV-4192) ([#1191](https://github.com/dasch-swiss/dsp-tools/issues/1191)) ([cfe95aa](https://github.com/dasch-swiss/dsp-tools/commit/cfe95aabc9cc8f90fb060677128f39caba509793))
* **xmllib:** rename add multiple function (DEV-4249) ([#1223](https://github.com/dasch-swiss/dsp-tools/issues/1223)) ([df5f87f](https://github.com/dasch-swiss/dsp-tools/commit/df5f87f0aa38e254c0223d064dbbb78be6aa6ae2))
* **xmllib:** rename default permissions enum (DEV-4248) ([#1222](https://github.com/dasch-swiss/dsp-tools/issues/1222)) ([8b5f858](https://github.com/dasch-swiss/dsp-tools/commit/8b5f858752fdec9e615c60fef1263be5b7835d60))
* **xmllib:** replace newline with XML tag (DEV-4195) ([#1189](https://github.com/dasch-swiss/dsp-tools/issues/1189)) ([3419b34](https://github.com/dasch-swiss/dsp-tools/commit/3419b34c7c8fdc00f9ef5176c40a7be7dbdf7b31))
* **xmlvalidate:** add CLI command (DEV-4119) ([#1193](https://github.com/dasch-swiss/dsp-tools/issues/1193)) ([1db3135](https://github.com/dasch-swiss/dsp-tools/commit/1db31352cc2c41f5f7df5ae8324687107735c1e3))
* **xmlvalidate:** add save graph flag to CLI (DEV-4206) ([#1199](https://github.com/dasch-swiss/dsp-tools/issues/1199)) ([aa55a2f](https://github.com/dasch-swiss/dsp-tools/commit/aa55a2fb9682344968ca069028ebede647646c4a))
* **xmlvalidate:** reformat validation results graph (DEV-4133) ([#1187](https://github.com/dasch-swiss/dsp-tools/issues/1187)) ([e655d98](https://github.com/dasch-swiss/dsp-tools/commit/e655d985a7358d7804ed51bb409b482f0c028811))
* **xmlvalidate:** save large number of errors as csv (DEV-4208) ([#1200](https://github.com/dasch-swiss/dsp-tools/issues/1200)) ([841975a](https://github.com/dasch-swiss/dsp-tools/commit/841975ab60f36a1e8e9932e85279d45a0ecb4a42))
* **xmlvalidate:** send validation request to API (DEV-4177) ([#1186](https://github.com/dasch-swiss/dsp-tools/issues/1186)) ([57099e4](https://github.com/dasch-swiss/dsp-tools/commit/57099e4c00fe1e2d2675169dcb09cdf9d342198a))
* **xmlvalidate:** value type checks (DEV-4122) ([#1197](https://github.com/dasch-swiss/dsp-tools/issues/1197)) ([bf509cd](https://github.com/dasch-swiss/dsp-tools/commit/bf509cd96b496c5ea6379e9e57f9157521c87f34))


### Bug Fixes

* add missing dependency in xmllib (DEV-4254) ([#1228](https://github.com/dasch-swiss/dsp-tools/issues/1228)) ([26bd3dc](https://github.com/dasch-swiss/dsp-tools/commit/26bd3dc23f9072ed06e1d005d2fb75d4cb876399))
* **ci:** pin the python version used in the CI ([#1230](https://github.com/dasch-swiss/dsp-tools/issues/1230)) ([ec75682](https://github.com/dasch-swiss/dsp-tools/commit/ec756829fd0b2adc10fcfb1564e3b31f33117bd8))
* **create:** always respect admin status of user in JSON file (DEV-4239) ([#1217](https://github.com/dasch-swiss/dsp-tools/issues/1217)) ([0e3c654](https://github.com/dasch-swiss/dsp-tools/commit/0e3c65439ada1cff6f4589263f959a9ca53428b0))
* **ingest-xmlupload:** correctly encode special chars / support absolute paths (DEV-4156, DEV-4166) ([#1247](https://github.com/dasch-swiss/dsp-tools/issues/1247)) ([435e283](https://github.com/dasch-swiss/dsp-tools/commit/435e2839022e64cd8a38dc41962e59c85a4e333c))
* **ingest-xmlupload:** strip leading `/` of absolute paths before sending to ingest (DEV-4300) ([#1252](https://github.com/dasch-swiss/dsp-tools/issues/1252)) ([695b189](https://github.com/dasch-swiss/dsp-tools/commit/695b189aad9bbaff74f59502627705c730d37af8))
* **ingest:** escape slash in filepath / improve error communication ([#1291](https://github.com/dasch-swiss/dsp-tools/issues/1291)) ([b580f89](https://github.com/dasch-swiss/dsp-tools/commit/b580f891a0a036cfeb495bd29b54e067faab8754))
* **validate-data:** don't crash if list nodes have special characters (DEV-4299) ([#1251](https://github.com/dasch-swiss/dsp-tools/issues/1251)) ([e7871fc](https://github.com/dasch-swiss/dsp-tools/commit/e7871fc9043d4c1c25f33845c98eb9ee9adf7fe3))
* **validate-data:** enable usage of other ontologies besides the default ontology (DEV-4263) ([#1235](https://github.com/dasch-swiss/dsp-tools/issues/1235)) ([a2f7959](https://github.com/dasch-swiss/dsp-tools/commit/a2f7959285049ea45dda365db029cfe86f6de7f9))
* **validate-data:** extract richtext as string if it starts with a tag (DEV-4280) ([#1250](https://github.com/dasch-swiss/dsp-tools/issues/1250)) ([71eaa23](https://github.com/dasch-swiss/dsp-tools/commit/71eaa23f2bfd1581cf0eb3f8a4ea9d9f651f08e0))
* **validate-data:** fix inheritance cardinality violations in properties (DEV-4278) ([#1241](https://github.com/dasch-swiss/dsp-tools/issues/1241)) ([e745e2a](https://github.com/dasch-swiss/dsp-tools/commit/e745e2aac06ab50296c0be5f6a9cd47a80ba62e0))
* **validate-data:** prevent SimpleText Class shape to be used at the wrong place (DEV-4224) ([#1206](https://github.com/dasch-swiss/dsp-tools/issues/1206)) ([e0e686f](https://github.com/dasch-swiss/dsp-tools/commit/e0e686fe15bc22a305f9dc4a571d2dbf4dfd57f0))
* **validate-data:** revert to exclusion of properties through gui-order (DEV-4279) ([#1242](https://github.com/dasch-swiss/dsp-tools/issues/1242)) ([e78f4f8](https://github.com/dasch-swiss/dsp-tools/commit/e78f4f8a5287b08815ea07b0e7a3ab98c2034113))
* **xmllib:** make permission serialisation into correct string (DEV-4256) ([#1225](https://github.com/dasch-swiss/dsp-tools/issues/1225)) ([1be649a](https://github.com/dasch-swiss/dsp-tools/commit/1be649af6db6f8fc6c113d9c1a15f52f059933a2))
* **xmllib:** resolve typing issues (RDU-57) ([#1270](https://github.com/dasch-swiss/dsp-tools/issues/1270)) ([172054c](https://github.com/dasch-swiss/dsp-tools/commit/172054c3e44c77cc48d918e6763031c8a3e32881))
* **xmllib:** turn `Resource.new()` into `staticmethod` (DEV-4250) ([#1220](https://github.com/dasch-swiss/dsp-tools/issues/1220)) ([00a66d9](https://github.com/dasch-swiss/dsp-tools/commit/00a66d923e87a57f43d047ef7669e27d92f317b3))
* **xmlupload:** downgrade fuseki to prevent backend from crashing ([#1201](https://github.com/dasch-swiss/dsp-tools/issues/1201)) ([12ebe12](https://github.com/dasch-swiss/dsp-tools/commit/12ebe12ce8a0917c551f106092479ba1568ede6f))
* **xmlvalidate:** duplicate cardinalities of LinkValues (DEV-4203) ([#1198](https://github.com/dasch-swiss/dsp-tools/issues/1198)) ([a8a67ab](https://github.com/dasch-swiss/dsp-tools/commit/a8a67abf2731870d20e3c08b2e2a75b9533eb7ec))


### Maintenance

* bump dependencies ([#1231](https://github.com/dasch-swiss/dsp-tools/issues/1231)) ([bb10677](https://github.com/dasch-swiss/dsp-tools/commit/bb106773b972eebf22a68595a99211f8cd8c3099))
* bump start-stack to 2024.11.01 ([#1290](https://github.com/dasch-swiss/dsp-tools/issues/1290)) ([4de93b8](https://github.com/dasch-swiss/dsp-tools/commit/4de93b83e2d5eef19279625651f5a29c0020a33b))
* change default permissions to new standard (RDU-48) ([#1180](https://github.com/dasch-swiss/dsp-tools/issues/1180)) ([8dedbe2](https://github.com/dasch-swiss/dsp-tools/commit/8dedbe251a07ae088abe1d931db55f3aac4b741a))
* **ci:** delegate python installation to uv ([#1218](https://github.com/dasch-swiss/dsp-tools/issues/1218)) ([0d7f91c](https://github.com/dasch-swiss/dsp-tools/commit/0d7f91c0635f4db183e98eb8db7cd95de31fbd6a))
* **ci:** use uv publish instead of twine ([#1219](https://github.com/dasch-swiss/dsp-tools/issues/1219)) ([39f91d8](https://github.com/dasch-swiss/dsp-tools/commit/39f91d82162ab8f662708228bfd84cd70d0781f1))
* fix `just clean` recipe ([#1269](https://github.com/dasch-swiss/dsp-tools/issues/1269)) ([5ce8b6f](https://github.com/dasch-swiss/dsp-tools/commit/5ce8b6f57488ebaadf2908a3376d67104120e46d))
* make info string of schema validation more precise ([#1202](https://github.com/dasch-swiss/dsp-tools/issues/1202)) ([59bd01a](https://github.com/dasch-swiss/dsp-tools/commit/59bd01ada348f1a82387654ab8b5f14db7f8e758))
* Move authentication out of general purpose connection (DEV-3762) ([#1238](https://github.com/dasch-swiss/dsp-tools/issues/1238)) ([4456c56](https://github.com/dasch-swiss/dsp-tools/commit/4456c56462b5e8812a553c58c121fe341241540f))
* remove obsolete python version definitions ([#1221](https://github.com/dasch-swiss/dsp-tools/issues/1221)) ([a34b45d](https://github.com/dasch-swiss/dsp-tools/commit/a34b45d721b2335be8b7aea19f68d2ff7e5cc81c))
* remove some pre-commit-hooks (DEV-4295) ([#1243](https://github.com/dasch-swiss/dsp-tools/issues/1243)) ([f1e7894](https://github.com/dasch-swiss/dsp-tools/commit/f1e78944bec4d690dae307db70c8c487394ecbd2))
* rename folder with test data ([#1204](https://github.com/dasch-swiss/dsp-tools/issues/1204)) ([e147d55](https://github.com/dasch-swiss/dsp-tools/commit/e147d55a0ea7950164d85e0e36a4fc03782ddb54))
* tidy up generated data after ingest e2e tests ([#1275](https://github.com/dasch-swiss/dsp-tools/issues/1275)) ([8599250](https://github.com/dasch-swiss/dsp-tools/commit/85992502270d8089d099d3c17bfefaaa57c47cb1))
* **validate-data:** change base info extraction from validation report (DEV-4258) ([#1227](https://github.com/dasch-swiss/dsp-tools/issues/1227)) ([c1f78a2](https://github.com/dasch-swiss/dsp-tools/commit/c1f78a28137b1b8a951f1c0e49fb055ddb6a9f06))
* **validate-data:** change identification of FileValue cardinality violation (DEV-4342) ([#1286](https://github.com/dasch-swiss/dsp-tools/issues/1286)) ([bd85640](https://github.com/dasch-swiss/dsp-tools/commit/bd856405f266ecd404001c6415080c455bf87088))
* **validate-data:** change identification of property from guiOrder to isEditable (DEV-4241) ([#1234](https://github.com/dasch-swiss/dsp-tools/issues/1234)) ([ec57ba1](https://github.com/dasch-swiss/dsp-tools/commit/ec57ba120c2b3cd991e985cf077aef167df453da))
* **validate-data:** extract requests to api from clients (DEV-4294) ([#1246](https://github.com/dasch-swiss/dsp-tools/issues/1246)) ([84df21c](https://github.com/dasch-swiss/dsp-tools/commit/84df21c5a948f505a54de9ed5f33474e31d8e1df))
* **validate-data:** include onotlogy name in LinkValue violation message (DEV-4275) ([#1262](https://github.com/dasch-swiss/dsp-tools/issues/1262)) ([d42b363](https://github.com/dasch-swiss/dsp-tools/commit/d42b3635254a8b7677063fba5a78e39754250bc0))
* **validate-data:** make abstract methods explicit ([#1276](https://github.com/dasch-swiss/dsp-tools/issues/1276)) ([cd2f940](https://github.com/dasch-swiss/dsp-tools/commit/cd2f940e27e68e15a82b12dc359fef3a0022b38e))
* **validate-data:** move prefix constants to separate file ([#1210](https://github.com/dasch-swiss/dsp-tools/issues/1210)) ([a4b08f7](https://github.com/dasch-swiss/dsp-tools/commit/a4b08f7b83d2e8d5620e04271d9d6c806b64aa38))
* **validate-data:** optimise queries for user results (DEV-4244) ([#1224](https://github.com/dasch-swiss/dsp-tools/issues/1224)) ([2e42602](https://github.com/dasch-swiss/dsp-tools/commit/2e4260274a26bb37badb8defb29e15fde768e47f))
* **validate-data:** refactor `ShaclValidator` (DEV-4199) ([#1239](https://github.com/dasch-swiss/dsp-tools/issues/1239)) ([f0cb819](https://github.com/dasch-swiss/dsp-tools/commit/f0cb819493b8624eaf0fe0cb72ee04c3d71e007e))
* **validate-data:** separate cardinality and content validation (DEV-4217) ([#1207](https://github.com/dasch-swiss/dsp-tools/issues/1207)) ([c0b057e](https://github.com/dasch-swiss/dsp-tools/commit/c0b057e60026ca13d4b55c4b5779ee81416b7395))
* **xmllib:** check and convert erroneous input datatypes (DEV-4190) ([#1184](https://github.com/dasch-swiss/dsp-tools/issues/1184)) ([8ea7914](https://github.com/dasch-swiss/dsp-tools/commit/8ea7914ef2b30dc03f3fdfea6795a41d85bdaaa8))
* **xmllib:** fix typing in XMLRoot ([#1229](https://github.com/dasch-swiss/dsp-tools/issues/1229)) ([2f60f0e](https://github.com/dasch-swiss/dsp-tools/commit/2f60f0e3cd0e9ec4c3b20762da0826dfa2d45c36))
* **xmllib:** improve decimal checks ([#1195](https://github.com/dasch-swiss/dsp-tools/issues/1195)) ([324e7ca](https://github.com/dasch-swiss/dsp-tools/commit/324e7caf3082adafae75bab8a48c00299d0a8354))
* **xmllib:** remove "title" parameter from (Video|Audio)SegmentResource.create_new() ([#1258](https://github.com/dasch-swiss/dsp-tools/issues/1258)) ([99478f1](https://github.com/dasch-swiss/dsp-tools/commit/99478f1de3af99b84074976621f9f5249779e637))
* **xmlupload:** bundle resource serialisation scripts ([#1289](https://github.com/dasch-swiss/dsp-tools/issues/1289)) ([b3960a4](https://github.com/dasch-swiss/dsp-tools/commit/b3960a4ed6af60114927c71ff319cbac1798cc2a))
* **xmlupload:** change serialisation of date value ([#1277](https://github.com/dasch-swiss/dsp-tools/issues/1277)) ([2b31398](https://github.com/dasch-swiss/dsp-tools/commit/2b3139893ac17d73c30465224c847112098705ef))
* **xmlupload:** change serialisation of file value ([#1273](https://github.com/dasch-swiss/dsp-tools/issues/1273)) ([a8b1b68](https://github.com/dasch-swiss/dsp-tools/commit/a8b1b6865936e35f0e80b980cc48043723b9a5f1))
* **xmlupload:** change serialisation of values ([#1279](https://github.com/dasch-swiss/dsp-tools/issues/1279)) ([f82383a](https://github.com/dasch-swiss/dsp-tools/commit/f82383a39206eae2387cd5970775c7b4e6966585))
* **xmlupload:** change serialisation of values with rdflib ([#1274](https://github.com/dasch-swiss/dsp-tools/issues/1274)) ([ec14df4](https://github.com/dasch-swiss/dsp-tools/commit/ec14df40617af882006f6cc042b46780441d5375))
* **xmlupload:** make value transformers ([#1280](https://github.com/dasch-swiss/dsp-tools/issues/1280)) ([f8466e2](https://github.com/dasch-swiss/dsp-tools/commit/f8466e2ea1b8ce732a3fb5352b4aec97ff7ea2e8))
* **xmlupload:** move create resource out of `resource_create_client` ([#1283](https://github.com/dasch-swiss/dsp-tools/issues/1283)) ([7f66210](https://github.com/dasch-swiss/dsp-tools/commit/7f66210407e7c8785a0b2d8862c440ea864743a0))
* **xmlupload:** serialise all values with rdflib ([#1287](https://github.com/dasch-swiss/dsp-tools/issues/1287)) ([3728089](https://github.com/dasch-swiss/dsp-tools/commit/37280897110aac6cba73e6582617b40230dbf0fe))
* **xmlupload:** serialise color prop in class ([#1271](https://github.com/dasch-swiss/dsp-tools/issues/1271)) ([46ce0d1](https://github.com/dasch-swiss/dsp-tools/commit/46ce0d1d2d587f1ec2974ff6a50a3d9267ee9066))
* **xmlupload:** serialise resource ([#1278](https://github.com/dasch-swiss/dsp-tools/issues/1278)) ([839bb2e](https://github.com/dasch-swiss/dsp-tools/commit/839bb2e5ace443c4aac09ad6af50a276b2b4ee84))
* **xmlupload:** serialise values in classes ([#1272](https://github.com/dasch-swiss/dsp-tools/issues/1272)) ([0279615](https://github.com/dasch-swiss/dsp-tools/commit/0279615229ef00ca8ef230eed6a391e8f304392b))
* **xmlvalidate:** ignore built-in dsp-properties (DEV-4191) ([#1192](https://github.com/dasch-swiss/dsp-tools/issues/1192)) ([3c01cfb](https://github.com/dasch-swiss/dsp-tools/commit/3c01cfb28e0b95b33a22dfc944eb5b6f2a598bcc))
* **xmlvalidate:** improve error message (DEV-4201) ([#1196](https://github.com/dasch-swiss/dsp-tools/issues/1196)) ([6b386e9](https://github.com/dasch-swiss/dsp-tools/commit/6b386e90ad8e8ee2103bc0f0e2b12fc86d57f917))


### Documentation

* fix documentation of `--no-iiif-uri-validation` ([#1237](https://github.com/dasch-swiss/dsp-tools/issues/1237)) ([755a8f0](https://github.com/dasch-swiss/dsp-tools/commit/755a8f06ca2e64cf3e285b7ad8045e2d2640da84))
* **start-stack:** describe how to login in locally running DSP-APP (RDU-54) ([#1266](https://github.com/dasch-swiss/dsp-tools/issues/1266)) ([6ae63d1](https://github.com/dasch-swiss/dsp-tools/commit/6ae63d122794ee5fb36e117c7b4d4132a764efdb))
* **xmllib:** add minimal docstrings (DEV-4297) ([#1257](https://github.com/dasch-swiss/dsp-tools/issues/1257)) ([4c029f1](https://github.com/dasch-swiss/dsp-tools/commit/4c029f100c075b0d94dbd512f0a6d6da9c734e79))
* **xmllib:** make args consistent (DEV-4314) ([#1259](https://github.com/dasch-swiss/dsp-tools/issues/1259)) ([fb5f5a9](https://github.com/dasch-swiss/dsp-tools/commit/fb5f5a948c7786ad4e3912cf1f87464e07493218))
* **xmllib:** serve docstrings on docs.dasch.swiss (DEV-4298) ([#1256](https://github.com/dasch-swiss/dsp-tools/issues/1256)) ([7db2f94](https://github.com/dasch-swiss/dsp-tools/commit/7db2f946f24cb2f478953ade4e387bbc5568812b))

## [9.1.0](https://github.com/dasch-swiss/dsp-tools/compare/v9.0.2...v9.1.0) (2024-10-01)


### Enhancements

* **validate:** reformat input XML data (DEV-4124) ([#1164](https://github.com/dasch-swiss/dsp-tools/issues/1164)) ([45af782](https://github.com/dasch-swiss/dsp-tools/commit/45af782b15c9d0703daf6ee0e76066331632b95c))
* **validate:** Write SHACL Shapes Turtle File (api-shapes) (DEV-4120) ([#1163](https://github.com/dasch-swiss/dsp-tools/issues/1163)) ([afb2a21](https://github.com/dasch-swiss/dsp-tools/commit/afb2a21e3ada980600fb118a69013372bbd9f412))
* **xmllib:** new functionality (RDU-38) ([#1129](https://github.com/dasch-swiss/dsp-tools/issues/1129)) ([1dc09f8](https://github.com/dasch-swiss/dsp-tools/commit/1dc09f8b2342f67830110a887688da5acafd17fa))
* **xmlvalidate:** add cardinalitiy restrictions to resource (DEV-4121) ([#1178](https://github.com/dasch-swiss/dsp-tools/issues/1178)) ([d2536c7](https://github.com/dasch-swiss/dsp-tools/commit/d2536c73d86306e7554ffe242ee3ed72b238db31))
* **xmlvalidate:** get ontologies from API (DEV-4150) ([#1171](https://github.com/dasch-swiss/dsp-tools/issues/1171)) ([2e599bd](https://github.com/dasch-swiss/dsp-tools/commit/2e599bd81506ca04f9bc70ff1acb19eec023ca69))
* **xmlvalidate:** SPARQL create resource SHACL (DEV-4123) ([#1174](https://github.com/dasch-swiss/dsp-tools/issues/1174)) ([ff550b3](https://github.com/dasch-swiss/dsp-tools/commit/ff550b3b8ddd274c35d9e722618b260e8c8cd109))


### Bug Fixes

* **excel2json:** write newlines correctly into the "description" field of the JSON file (RDU-45) ([#1170](https://github.com/dasch-swiss/dsp-tools/issues/1170)) ([889d11f](https://github.com/dasch-swiss/dsp-tools/commit/889d11f86e0b447606419d017d347ee04b567c24))
* **ingest-xmlupload:** only convert absolute path from mapping CSV to relative path if necessary ([#1176](https://github.com/dasch-swiss/dsp-tools/issues/1176)) ([72ee250](https://github.com/dasch-swiss/dsp-tools/commit/72ee2506d19e58d1818db3eabf17e1941155cd9f))
* progress bar recovers after resizing the Terminal window (DEV-4110) ([#1161](https://github.com/dasch-swiss/dsp-tools/issues/1161)) ([7b4cc12](https://github.com/dasch-swiss/dsp-tools/commit/7b4cc12f668cacad3d57fd94671265f6efaa1d2b))
* **start-stack:** `--latest` flag ships latest versions of all backend components, instead of only API (DEV-4100) ([#1159](https://github.com/dasch-swiss/dsp-tools/issues/1159)) ([6bbec2c](https://github.com/dasch-swiss/dsp-tools/commit/6bbec2c18f269e427185d0806df094d3d0fee557))
* **xmlupload:** allow more URLs ([#1177](https://github.com/dasch-swiss/dsp-tools/issues/1177)) ([f9aa882](https://github.com/dasch-swiss/dsp-tools/commit/f9aa882675f72a4438e50e49a7e012b82c43495c))
* **xmlupload:** increase timeout for file uploads to 10 min ([#1169](https://github.com/dasch-swiss/dsp-tools/issues/1169)) ([a5766ee](https://github.com/dasch-swiss/dsp-tools/commit/a5766ee7a779d839b0137cf3da64c166a688cc2b))
* **xmlupload:** subpar output of onto consistency check (DEV-3727) ([#1143](https://github.com/dasch-swiss/dsp-tools/issues/1143)) ([edb58a9](https://github.com/dasch-swiss/dsp-tools/commit/edb58a9d74db5acbd1e62a05633840281c9ff452))


### Maintenance

* bump ruff ([#1172](https://github.com/dasch-swiss/dsp-tools/issues/1172)) ([e65c753](https://github.com/dasch-swiss/dsp-tools/commit/e65c75315da8039fa9533ca3b79e3a4802768cd8))
* bump stack to 2024.09.01 ([#1183](https://github.com/dasch-swiss/dsp-tools/issues/1183)) ([28a9f1c](https://github.com/dasch-swiss/dsp-tools/commit/28a9f1c431f4b0ff2ca6799c511aca1b243bd486))
* **deps-dev:** bump the all-dependencies group across 1 directory with 9 updates ([#1148](https://github.com/dasch-swiss/dsp-tools/issues/1148)) ([07910b6](https://github.com/dasch-swiss/dsp-tools/commit/07910b67d2b86b87babe3bcefef3ee36984882b5))
* migrate from poetry to uv (DEV-4040) ([#1160](https://github.com/dasch-swiss/dsp-tools/issues/1160)) ([6845b1a](https://github.com/dasch-swiss/dsp-tools/commit/6845b1a9489d0d77bf6fd49710414d644bd4646c))
* Revert "chore: Fix tests not being executed on release-please branch" ([#1158](https://github.com/dasch-swiss/dsp-tools/issues/1158)) ([3af3d91](https://github.com/dasch-swiss/dsp-tools/commit/3af3d9166078e77b3e873e51caf3ee38f0978504))
* **xmllib:** make dsp built-in resources interface consistent (DEV-4186) ([#1182](https://github.com/dasch-swiss/dsp-tools/issues/1182)) ([1f10fb3](https://github.com/dasch-swiss/dsp-tools/commit/1f10fb3f5aefe6c7b152c51c447846faf1d24661))
* **xmlupload:** remove lineColor key from geometry value JSON object (DEV-4132) ([#1166](https://github.com/dasch-swiss/dsp-tools/issues/1166)) ([8169cce](https://github.com/dasch-swiss/dsp-tools/commit/8169cce79f92f8131639115fe5ac06e0ce50bcee))
* **xmlvalidate:** change qname transformation ([#1168](https://github.com/dasch-swiss/dsp-tools/issues/1168)) ([9efe030](https://github.com/dasch-swiss/dsp-tools/commit/9efe0305c2a084c4950b76285c966df84286ba9d))
* **xmlvalidate:** change structure of XML deserialisation (DEV-4125) ([#1173](https://github.com/dasch-swiss/dsp-tools/issues/1173)) ([50a35e3](https://github.com/dasch-swiss/dsp-tools/commit/50a35e36b06d0a7818ac27cdd91aad59c2286369))
* **xmlvalidate:** rename test fixtures files ([#1175](https://github.com/dasch-swiss/dsp-tools/issues/1175)) ([b023c6d](https://github.com/dasch-swiss/dsp-tools/commit/b023c6d346e4a019520b729a251a41577a7d4c3d))
* **xmlvalidate:** replace value BN with IRI (DEV-4187) ([#1181](https://github.com/dasch-swiss/dsp-tools/issues/1181)) ([1a34288](https://github.com/dasch-swiss/dsp-tools/commit/1a3428861f7818054469c6c28ad61c7d42c3704a))


### Documentation

* fix syntax mistakes in ontology.md ([#1162](https://github.com/dasch-swiss/dsp-tools/issues/1162)) ([dba4770](https://github.com/dasch-swiss/dsp-tools/commit/dba477078c3435e02764fdc91cb8def899bfde48))

## [9.0.2](https://github.com/dasch-swiss/dsp-tools/compare/v9.0.1...v9.0.2) (2024-09-04)


### Maintenance

* Add comment to CI so that this does not get broken again ([#1156](https://github.com/dasch-swiss/dsp-tools/issues/1156)) ([7e3c2ec](https://github.com/dasch-swiss/dsp-tools/commit/7e3c2ec5e2a346570e2b1d29e8d517a34feb4118))
* Attempt to fix release issues by bringing back the GH_TOKEN ([#1153](https://github.com/dasch-swiss/dsp-tools/issues/1153)) ([0853e25](https://github.com/dasch-swiss/dsp-tools/commit/0853e2547007bb2301d20e696b98512aedf6e03f))
* Fix release issues by using DASCHBOT PAT ([#1154](https://github.com/dasch-swiss/dsp-tools/issues/1154)) ([4684c91](https://github.com/dasch-swiss/dsp-tools/commit/4684c91509e8968b9738d4a231c40fd97d14e5cf))

## [9.0.1](https://github.com/dasch-swiss/dsp-tools/compare/v9.0.0...v9.0.1) (2024-09-04)


### Bug Fixes

* bump stack to 2024.08.02 ([#1149](https://github.com/dasch-swiss/dsp-tools/issues/1149)) ([9190dbf](https://github.com/dasch-swiss/dsp-tools/commit/9190dbf3d0b5f077e309790ea80a0b52adf01b10))


### Maintenance

* Fix releasing to PyPI (DEV-3972) ([#1151](https://github.com/dasch-swiss/dsp-tools/issues/1151)) ([b1ba08b](https://github.com/dasch-swiss/dsp-tools/commit/b1ba08b0e072f54dc8a2ca11c48e7e281dc61720))
* Fix tests not being executed on release-please branch ([#1152](https://github.com/dasch-swiss/dsp-tools/issues/1152)) ([325006b](https://github.com/dasch-swiss/dsp-tools/commit/325006b5b1df77fc82c3d6d5cd169ad0bc601168))

## [9.0.0](https://github.com/dasch-swiss/dsp-tools/compare/v8.5.0...v9.0.0) (2024-09-03)


### ⚠ BREAKING CHANGES

* **xmlupload:** change representation of <video-segment> and <audio-segment> in XML due to XSD schema validation problems (DEV-3964) ([#1101](https://github.com/dasch-swiss/dsp-tools/issues/1101))

### Enhancements

* **xmlupload:** add resource type to error message when checking for encoding mistakes (RDU-25) ([#1145](https://github.com/dasch-swiss/dsp-tools/issues/1145)) ([7279b69](https://github.com/dasch-swiss/dsp-tools/commit/7279b6981b0c6a44b95ef5d907d2364d27fbdc71))


### Bug Fixes

* **excel2json-lists:** remove erroneous warning if comments column exist (RDU-23) ([#1141](https://github.com/dasch-swiss/dsp-tools/issues/1141)) ([4ed0a7e](https://github.com/dasch-swiss/dsp-tools/commit/4ed0a7e0178e03829efbc54a4009b7f450b5db48))
* **excel2json:** don't crash if json_header.xlsx is present when using the default command (RDU-24) ([#1144](https://github.com/dasch-swiss/dsp-tools/issues/1144)) ([4c4738e](https://github.com/dasch-swiss/dsp-tools/commit/4c4738eb8200eb0a7121ab8cfd5c460b5c7f1d26))
* **xmlupload:** change representation of &lt;video-segment&gt; and <audio-segment> in XML due to XSD schema validation problems (DEV-3964) ([#1101](https://github.com/dasch-swiss/dsp-tools/issues/1101)) ([1476eca](https://github.com/dasch-swiss/dsp-tools/commit/1476eca2b1da17bcf731057a81292a0baa9637fd))
* **xmlupload:** don't rely on requests.Response.json() in case of unsuccessful request (DEV-4035) ([#1132](https://github.com/dasch-swiss/dsp-tools/issues/1132)) ([ff0b1de](https://github.com/dasch-swiss/dsp-tools/commit/ff0b1de7eb9e146c659774454125b20f4cb85cf9))


### Maintenance

* bump stack to 2024.08.02 ([#1147](https://github.com/dasch-swiss/dsp-tools/issues/1147)) ([86e764b](https://github.com/dasch-swiss/dsp-tools/commit/86e764bd75455ef4ab83595b026e073c224df43a))
* don't ignore ARG001 in pre-commit hooks ([#1136](https://github.com/dasch-swiss/dsp-tools/issues/1136)) ([7ea83f7](https://github.com/dasch-swiss/dsp-tools/commit/7ea83f7464353c8b7047f9d59143a903947dc07c))
* remove codecov-integration (DEV-4043) ([#1142](https://github.com/dasch-swiss/dsp-tools/issues/1142)) ([042cf06](https://github.com/dasch-swiss/dsp-tools/commit/042cf0675421f6207d9683ae4331ad18065e40d1))
* **start-stack:** change message for docker prune (DEV-4027) ([#1126](https://github.com/dasch-swiss/dsp-tools/issues/1126)) ([73c7823](https://github.com/dasch-swiss/dsp-tools/commit/73c7823fadf4e8de8e94826e0798dfd436349cd2))
* surround angular brackets in docstrings by backticks (DEV-4014) ([#1135](https://github.com/dasch-swiss/dsp-tools/issues/1135)) ([7e746e2](https://github.com/dasch-swiss/dsp-tools/commit/7e746e2ae195329a9646113a7b29173588d93d2e))
* turn XMLResource and XMLProperty into dataclasses ([#1137](https://github.com/dasch-swiss/dsp-tools/issues/1137)) ([6c4fe5d](https://github.com/dasch-swiss/dsp-tools/commit/6c4fe5d04f5439d330035aca1162cdeb3e5c082c))


### Documentation

* **excel2xml:** fix params of make_hasSegmentBounds_prop() ([#1138](https://github.com/dasch-swiss/dsp-tools/issues/1138)) ([95b7a84](https://github.com/dasch-swiss/dsp-tools/commit/95b7a84d941468b7849c75e0cd6bbe658317d185))
* mention fixed order of video/audio segments ([#1139](https://github.com/dasch-swiss/dsp-tools/issues/1139)) ([7ed7b93](https://github.com/dasch-swiss/dsp-tools/commit/7ed7b937a13ec131ffba0dfe09fc61466b536bff))

## [8.5.0](https://github.com/dasch-swiss/dsp-tools/compare/v8.4.0...v8.5.0) (2024-08-21)


### Enhancements

* **exce2xml-lib:** make xsd compatible string without uuid (DEV-4026) ([#1127](https://github.com/dasch-swiss/dsp-tools/issues/1127)) ([50ef476](https://github.com/dasch-swiss/dsp-tools/commit/50ef476e9ac3e67011258ac29d7f6c78f0f709af))
* **excel2json-lists:** enable to add comments to list nodes (RDU-18) ([#1111](https://github.com/dasch-swiss/dsp-tools/issues/1111)) ([54ba206](https://github.com/dasch-swiss/dsp-tools/commit/54ba20615c150ed77c548041a8be8011ce82c14c))


### Bug Fixes

* **cli:** resume-xmlupload --skip-first-resource now works (DEV-3744) ([#1084](https://github.com/dasch-swiss/dsp-tools/issues/1084)) ([7f99287](https://github.com/dasch-swiss/dsp-tools/commit/7f9928794a680b0a417a8a4f603cbac4ac4df2bd))
* **xmlupload:** allow non-prefixed custom groups, and custom groups with dash (DEV-3979) ([#1098](https://github.com/dasch-swiss/dsp-tools/issues/1098)) ([e5a19eb](https://github.com/dasch-swiss/dsp-tools/commit/e5a19ebd2ecf34f7e1db45ad4781ab90183aac66))


### Maintenance

* bump dependencies and fix new linter errors ([#1122](https://github.com/dasch-swiss/dsp-tools/issues/1122)) ([212e6e5](https://github.com/dasch-swiss/dsp-tools/commit/212e6e545d10c5f8b7c3726584dbe0f25a4097f4))
* bump stack to 2024.08.01 ([#1128](https://github.com/dasch-swiss/dsp-tools/issues/1128)) ([400ddbe](https://github.com/dasch-swiss/dsp-tools/commit/400ddbe7a2e9dddb4e2edc685b3076e0e919d400))
* **excel2json-lists:** access columns differently ([#1109](https://github.com/dasch-swiss/dsp-tools/issues/1109)) ([154f88f](https://github.com/dasch-swiss/dsp-tools/commit/154f88f03e9c94091dd9adb1467b764067d84a3b))
* **excel2json-lists:** add excel name to lists problem classes ([#1089](https://github.com/dasch-swiss/dsp-tools/issues/1089)) ([6112506](https://github.com/dasch-swiss/dsp-tools/commit/61125060fd16b2cc36324036c616095c26a770c2))
* **excel2json-lists:** add filename to sheet class ([#1090](https://github.com/dasch-swiss/dsp-tools/issues/1090)) ([2f9e30e](https://github.com/dasch-swiss/dsp-tools/commit/2f9e30e44fb24fdd9970aa661859b4b67d77ed20))
* **excel2json-lists:** change error message format ([#1118](https://github.com/dasch-swiss/dsp-tools/issues/1118)) ([f479aa4](https://github.com/dasch-swiss/dsp-tools/commit/f479aa49e2ce08fcf6a0c44655bed65f9c871d38))
* **excel2json-lists:** change find missing translations ([#1112](https://github.com/dasch-swiss/dsp-tools/issues/1112)) ([ab54d96](https://github.com/dasch-swiss/dsp-tools/commit/ab54d961c58e57a607666333887b06c6d1605d26))
* **excel2json-lists:** change location of column info extraction ([#1115](https://github.com/dasch-swiss/dsp-tools/issues/1115)) ([bd163cf](https://github.com/dasch-swiss/dsp-tools/commit/bd163cfd3844a1ebcfe7d3bb17414eba8bff48e0))
* **excel2json-lists:** change paramter to ExcelSheet in functions ([#1091](https://github.com/dasch-swiss/dsp-tools/issues/1091)) ([a4086c2](https://github.com/dasch-swiss/dsp-tools/commit/a4086c21cb95cb9a34e5d5433f75ce71bfb5c529))
* **excel2json-lists:** change sorting of columns ([#1110](https://github.com/dasch-swiss/dsp-tools/issues/1110)) ([4670085](https://github.com/dasch-swiss/dsp-tools/commit/46700856a9f629e39af71a3959fa17c545b29f81))
* **excel2json-lists:** remove dead check ([#1120](https://github.com/dasch-swiss/dsp-tools/issues/1120)) ([463c992](https://github.com/dasch-swiss/dsp-tools/commit/463c992a89dd2f7e7fc6215e817e2bb5ec386ff2))
* **excel2json-lists:** remove file hierarchy from code ([#1094](https://github.com/dasch-swiss/dsp-tools/issues/1094)) ([3b554a3](https://github.com/dasch-swiss/dsp-tools/commit/3b554a3289d318efa4bd4399979b652065c9b24a))
* **excel2json-lists:** remove file hierarchy from Problem classes ([#1093](https://github.com/dasch-swiss/dsp-tools/issues/1093)) ([56bd84d](https://github.com/dasch-swiss/dsp-tools/commit/56bd84d9d0cb12a5e27fc2a12a1ad30ae8be0d76))
* **excel2json-lists:** remove unnecessary checks ([#1107](https://github.com/dasch-swiss/dsp-tools/issues/1107)) ([71339f7](https://github.com/dasch-swiss/dsp-tools/commit/71339f77f4f9e67f9a52e840f1e0211e3757bc28))
* **excel2json-lists:** wrap file structure in classes ([#1086](https://github.com/dasch-swiss/dsp-tools/issues/1086)) ([e60002a](https://github.com/dasch-swiss/dsp-tools/commit/e60002a7c5581deaa5258700d963fa414284c648))
* **excel2json-new-lists:** change order of functions ([#1100](https://github.com/dasch-swiss/dsp-tools/issues/1100)) ([0b9a429](https://github.com/dasch-swiss/dsp-tools/commit/0b9a429ed2748f4ecd1eacc309c3defa2fa038a5))
* **excel2json-new-lists:** extract fixtures for compliance tests ([#1104](https://github.com/dasch-swiss/dsp-tools/issues/1104)) ([f2b05ac](https://github.com/dasch-swiss/dsp-tools/commit/f2b05ac58856856bb0dfb6fec5aa1c41bf9874be))
* **excel2json:** lists delete duplicate tests ([#1082](https://github.com/dasch-swiss/dsp-tools/issues/1082)) ([90280c1](https://github.com/dasch-swiss/dsp-tools/commit/90280c130fdc2237cbac0f11fa05f3eb98f91f28))
* **github-action:** allow referencing RDU tickets in PR titles (RDU-13) ([#1095](https://github.com/dasch-swiss/dsp-tools/issues/1095)) ([c0f360c](https://github.com/dasch-swiss/dsp-tools/commit/c0f360c59d1496b822ad83588240fe5f034e6cdf))
* **new-lists:** reorganise files ([#1096](https://github.com/dasch-swiss/dsp-tools/issues/1096)) ([866f6bd](https://github.com/dasch-swiss/dsp-tools/commit/866f6bd1db0114e273a03773d1ed49e4262dc62a))
* preparation for new &lt;video-segment&gt; ([#1125](https://github.com/dasch-swiss/dsp-tools/issues/1125)) ([57dd646](https://github.com/dasch-swiss/dsp-tools/commit/57dd646a6112a539fe535caa997ee6cab62262d0))
* send X-Asset-Ingested header only when needed ([#1117](https://github.com/dasch-swiss/dsp-tools/issues/1117)) ([a5279f1](https://github.com/dasch-swiss/dsp-tools/commit/a5279f1b6493463f006ecefa89086ea1ae3478b2))
* small adaptions to docs + docstrings ([#1121](https://github.com/dasch-swiss/dsp-tools/issues/1121)) ([705c2f7](https://github.com/dasch-swiss/dsp-tools/commit/705c2f77a2f2bdc5f6b0c93e7efd58f6f4cb2bb5))
* tidy up readme ([#1106](https://github.com/dasch-swiss/dsp-tools/issues/1106)) ([6663276](https://github.com/dasch-swiss/dsp-tools/commit/66632760a4517ae21dd8f28cda0c77fc23704295))


### Documentation

* **CLI:** add flag for IIIF validation in xmlupload in documentation ([#1103](https://github.com/dasch-swiss/dsp-tools/issues/1103)) ([d00f1cf](https://github.com/dasch-swiss/dsp-tools/commit/d00f1cfcd7efbbe6d6e98f25e96f7de08873dff4))
* **excel2json:** mention old and new at the top ([#1123](https://github.com/dasch-swiss/dsp-tools/issues/1123)) ([cc58c68](https://github.com/dasch-swiss/dsp-tools/commit/cc58c68daea1f09fb26ff5b7a135489acdc61e2b))

## [8.4.0](https://github.com/dasch-swiss/dsp-tools/compare/v8.3.0...v8.4.0) (2024-08-07)


### Enhancements

* **excel2json:** add option to create header with Excel file (DEV-3898) ([#1065](https://github.com/dasch-swiss/dsp-tools/issues/1065)) ([353d8e9](https://github.com/dasch-swiss/dsp-tools/commit/353d8e95d70b0327edaa5a891eda4592d353080d))
* New workflow for big xmluploads: add commands `upload-files` and `ingest-files` (DEV-3905) ([#1067](https://github.com/dasch-swiss/dsp-tools/issues/1067)) ([b4c2912](https://github.com/dasch-swiss/dsp-tools/commit/b4c291266cdb4af07f8293f24904747e44f7033c))


### Bug Fixes

* don't use copyrighted testdata any more (DEV-3906) ([#1068](https://github.com/dasch-swiss/dsp-tools/issues/1068)) ([1558408](https://github.com/dasch-swiss/dsp-tools/commit/1558408fe25c7e6608e4f55ccd336904dbd6464b))
* **ingest-xmlupload:** allow uppercased file extensions (DEV-3963) ([#1075](https://github.com/dasch-swiss/dsp-tools/issues/1075)) ([51a4703](https://github.com/dasch-swiss/dsp-tools/commit/51a470344c5cbddcf08ded3871f7a31a9b9752fb))
* Urlencode filenames when uploading files to ingesta (DEV-3865) ([#1045](https://github.com/dasch-swiss/dsp-tools/issues/1045)) ([4edfbd3](https://github.com/dasch-swiss/dsp-tools/commit/4edfbd3d2beb8c269e93647514abbf341edd6de8))


### Maintenance

* add logging of requests made in DspIngestClientLive (DEV-3761) ([#1064](https://github.com/dasch-swiss/dsp-tools/issues/1064)) ([84c6101](https://github.com/dasch-swiss/dsp-tools/commit/84c6101aa57cf39c3e6297c0ecbea1cd6b8dbdef))
* bump start-stack to 2024.07.02 ([#1078](https://github.com/dasch-swiss/dsp-tools/issues/1078)) ([2a74978](https://github.com/dasch-swiss/dsp-tools/commit/2a74978c4829b9a5c4b002c03122fefa4bbe57cd))
* **deps:** bump the all-dependencies group with 16 updates ([#1071](https://github.com/dasch-swiss/dsp-tools/issues/1071)) ([a893aca](https://github.com/dasch-swiss/dsp-tools/commit/a893aca6d94741cd985ec76c52fd1adf3df2e4c7))
* **excel2json:** change serialisation json header (DEV-3877) ([#1046](https://github.com/dasch-swiss/dsp-tools/issues/1046)) ([f4c6088](https://github.com/dasch-swiss/dsp-tools/commit/f4c6088d9e80217dc38bfb32da216de68aaeb798))
* **excel2json:** find duplicate excel sheet names ([#1054](https://github.com/dasch-swiss/dsp-tools/issues/1054)) ([83bb96a](https://github.com/dasch-swiss/dsp-tools/commit/83bb96a856d30df19cfceaaef6c0b5bca36e53fa))
* **excel2json:** generalise InvalidContentInSheetProblem ([#1051](https://github.com/dasch-swiss/dsp-tools/issues/1051)) ([c55603c](https://github.com/dasch-swiss/dsp-tools/commit/c55603c16e05cc8a9ebc0ec959acf8edbc9aa88d))
* **excel2json:** improve checks for classes sheet in resources.xlsx ([#1061](https://github.com/dasch-swiss/dsp-tools/issues/1061)) ([1839d98](https://github.com/dasch-swiss/dsp-tools/commit/1839d9848f17b7a2311f65b92b87829d34aca47a))
* **excel2json:** move list problems to separate file ([#1049](https://github.com/dasch-swiss/dsp-tools/issues/1049)) ([353c002](https://github.com/dasch-swiss/dsp-tools/commit/353c0021b1a473ad119c48cade4d99d51f982fe3))
* **excel2json:** properties collect problems before raising error ([#1063](https://github.com/dasch-swiss/dsp-tools/issues/1063)) ([5ba6fc1](https://github.com/dasch-swiss/dsp-tools/commit/5ba6fc1db2ad52ce052170aa5a28f5c134632919))
* **excel2json:** reorder the functions in resources.py ([#1060](https://github.com/dasch-swiss/dsp-tools/issues/1060)) ([6295b02](https://github.com/dasch-swiss/dsp-tools/commit/6295b022931a4bc226a15f715b8fefc38a8d3a86))
* **excel2json:** replace ListExcelProblem with ExcelFileProblem ([#1052](https://github.com/dasch-swiss/dsp-tools/issues/1052)) ([b84a185](https://github.com/dasch-swiss/dsp-tools/commit/b84a185d512711a83f168c7e9105a974c5ca5a26))
* **excel2json:** restructure and rename find missing values function (DEV-3909) ([#1070](https://github.com/dasch-swiss/dsp-tools/issues/1070)) ([d42595e](https://github.com/dasch-swiss/dsp-tools/commit/d42595e37a468360801f75dcef0bebc495b10351))
* **excel2json:** serialise property with dataclass ([#1059](https://github.com/dasch-swiss/dsp-tools/issues/1059)) ([0e33238](https://github.com/dasch-swiss/dsp-tools/commit/0e332380fbffdb5ba22db94c23ed2017c0566a91))
* **excel2json:** serialise resources with dataclass ([#1062](https://github.com/dasch-swiss/dsp-tools/issues/1062)) ([df11148](https://github.com/dasch-swiss/dsp-tools/commit/df111480334a291ceeeb34c4f2b4621b449a5eb9))
* **excel2json:** validate classes sheet in resources.xlsx ([#1057](https://github.com/dasch-swiss/dsp-tools/issues/1057)) ([96b38f7](https://github.com/dasch-swiss/dsp-tools/commit/96b38f7174f845579d95a8b819751d93337cccc4))
* ignore ARG001 (unused function argument) in .pre-commit-config.yaml ([#1066](https://github.com/dasch-swiss/dsp-tools/issues/1066)) ([06b41d9](https://github.com/dasch-swiss/dsp-tools/commit/06b41d9f3a901dde9c27f964ae952ac266a97406))
* **performance:** add initial k6 excel2json performance test (DEV-3885) ([#1056](https://github.com/dasch-swiss/dsp-tools/issues/1056)) ([3625c62](https://github.com/dasch-swiss/dsp-tools/commit/3625c62df9a0013c7f45bef0f5735242376353bf))
* **test:** renaming ([#1048](https://github.com/dasch-swiss/dsp-tools/issues/1048)) ([a7f0bca](https://github.com/dasch-swiss/dsp-tools/commit/a7f0bcad95e5b92bc65db2d2b11669f0a32e0b67))
* **test:** take apart assertions for test_project.py ([#1055](https://github.com/dasch-swiss/dsp-tools/issues/1055)) ([da31d19](https://github.com/dasch-swiss/dsp-tools/commit/da31d196e9e94eeb254f876e4c0c079915ab280e))
* **upload-files:** adapt timeout, so that big files don't fail  ([#1077](https://github.com/dasch-swiss/dsp-tools/issues/1077)) ([1f7b43b](https://github.com/dasch-swiss/dsp-tools/commit/1f7b43be275d9b6b986a0a3174f3d38c1b0fe75f))
* **xmlupload:** video-segment and audio-segment: clarify docs / allow custom creation date ([#1076](https://github.com/dasch-swiss/dsp-tools/issues/1076)) ([1196afc](https://github.com/dasch-swiss/dsp-tools/commit/1196afcb31b5e543865d9ab6e6e7fe9d814d03cb))


### Documentation

* add missing commands to docs/index.md ([#1079](https://github.com/dasch-swiss/dsp-tools/issues/1079)) ([231a6b7](https://github.com/dasch-swiss/dsp-tools/commit/231a6b72becb3ef27dc3b4f21883f73147b84b9c))
* tidy up dev docs ([#1080](https://github.com/dasch-swiss/dsp-tools/issues/1080)) ([eeaccc6](https://github.com/dasch-swiss/dsp-tools/commit/eeaccc63af9f3f3ded17028229d2d88da5276915))

## [8.3.0](https://github.com/dasch-swiss/dsp-tools/compare/v8.2.0...v8.3.0) (2024-07-11)


### Enhancements

* **excel2json:** creating classes without any cardinalities (DEV-3755) ([#1029](https://github.com/dasch-swiss/dsp-tools/issues/1029)) ([9e19aa1](https://github.com/dasch-swiss/dsp-tools/commit/9e19aa1c495c59baa54f1d3c8150420733454a8a))


### Bug Fixes

* **excel2json-lists:** assignment of wrong parent ID if the node names are identical (DEV-3844) ([#1040](https://github.com/dasch-swiss/dsp-tools/issues/1040)) ([51af556](https://github.com/dasch-swiss/dsp-tools/commit/51af5567c56d231bd1b911d86e76ac22371ce4aa))
* harmonize supported file extensions in docs, test data, and prod code (DEV-3788) ([#1028](https://github.com/dasch-swiss/dsp-tools/issues/1028)) ([728b782](https://github.com/dasch-swiss/dsp-tools/commit/728b7826d4de044ec8ee8d5fd89a6a02c04c3273))
* **new-excel2json:** don't crash when Excel files are upper-cased (DEV-3808) ([#1032](https://github.com/dasch-swiss/dsp-tools/issues/1032)) ([2a5cc31](https://github.com/dasch-swiss/dsp-tools/commit/2a5cc31607f7cce51afbcb14edd79a53b4fa52ea))
* **xmlupload:** allow angular brackets in SimpleText (DEV-3814) ([#1033](https://github.com/dasch-swiss/dsp-tools/issues/1033)) ([cf8e410](https://github.com/dasch-swiss/dsp-tools/commit/cf8e410aaa476921c85017352a233588c2a5b370))
* **xmlupload:** don't omit any stashed links (DEV-3827) ([#1037](https://github.com/dasch-swiss/dsp-tools/issues/1037)) ([20e7eac](https://github.com/dasch-swiss/dsp-tools/commit/20e7eac679b95b4121e88265e6781c570e391fa7))


### Maintenance

* Add db configuration to ingest container ([#1039](https://github.com/dasch-swiss/dsp-tools/issues/1039)) ([48e39ea](https://github.com/dasch-swiss/dsp-tools/commit/48e39eaaaaa3bcd06dfb40577f648a3afbf9769d))
* bump ruff ([#1035](https://github.com/dasch-swiss/dsp-tools/issues/1035)) ([720d7e9](https://github.com/dasch-swiss/dsp-tools/commit/720d7e915c25b07f38593bee1d5dccc3b40b95d5))
* bump start-stack to 2024.07.01 ([#1043](https://github.com/dasch-swiss/dsp-tools/issues/1043)) ([af6ad29](https://github.com/dasch-swiss/dsp-tools/commit/af6ad29778b47c05ab8d6c37e05dbe81d1546c71))
* **create:** inform user that project membership has to be assinged manually (DEV-3800) ([#1030](https://github.com/dasch-swiss/dsp-tools/issues/1030)) ([5494267](https://github.com/dasch-swiss/dsp-tools/commit/54942674a0290b97d0e87b8bcd0e88adc53763e3))
* **deps:** bump certifi from 2024.6.2 to 2024.7.4 ([#1041](https://github.com/dasch-swiss/dsp-tools/issues/1041)) ([550b1cf](https://github.com/dasch-swiss/dsp-tools/commit/550b1cf5b63988d9122737d410050ff414bfa9bd))
* **deps:** bump the all-dependencies group with 12 updates ([#1036](https://github.com/dasch-swiss/dsp-tools/issues/1036)) ([797f351](https://github.com/dasch-swiss/dsp-tools/commit/797f3513c54f496d8b070c6aacbbb6d6a652b34e))
* don't crash when offline ([#1034](https://github.com/dasch-swiss/dsp-tools/issues/1034)) ([c39d610](https://github.com/dasch-swiss/dsp-tools/commit/c39d6107c98e97330031fb8b9549450bbba3ba91))
* downgrade pytest, until Assertion Rewriting is fixed (DEV-3786) ([#1026](https://github.com/dasch-swiss/dsp-tools/issues/1026)) ([d2c8ede](https://github.com/dasch-swiss/dsp-tools/commit/d2c8ede4f7a099c5155f8b677888ece4eb17fae9))
* downgrade pytest, until Assertion Rewriting is fixed (DEV-3786) ([#1038](https://github.com/dasch-swiss/dsp-tools/issues/1038)) ([d8d8d72](https://github.com/dasch-swiss/dsp-tools/commit/d8d8d722041a5c9bb8e8bb18a0539a14e5e6da4c))
* Enable erasing projects locally ([#1042](https://github.com/dasch-swiss/dsp-tools/issues/1042)) ([807db71](https://github.com/dasch-swiss/dsp-tools/commit/807db71aca58575b54d62667c23e4e426a68ba32))
* improve error messages according to consulting with RDU  ([#1031](https://github.com/dasch-swiss/dsp-tools/issues/1031)) ([e9c9507](https://github.com/dasch-swiss/dsp-tools/commit/e9c9507136211719a4f95006194dedfad9343eaf))

## [8.2.0](https://github.com/dasch-swiss/dsp-tools/compare/v8.1.0...v8.2.0) (2024-06-19)


### Enhancements

* add flag to suppress warning when using old dsp-tools version (DEV-3707) ([#1001](https://github.com/dasch-swiss/dsp-tools/issues/1001)) ([e28ba2e](https://github.com/dasch-swiss/dsp-tools/commit/e28ba2ea9345262bd29ed80a0e35276177a6f765))
* display progress in xmlupload as progress bar (DEV-3708) ([#1022](https://github.com/dasch-swiss/dsp-tools/issues/1022)) ([4ccf628](https://github.com/dasch-swiss/dsp-tools/commit/4ccf628a9e4d7bb8671eeb807de722459389d200))


### Bug Fixes

* **ci:** bump release-please action (DEV-3526) ([#992](https://github.com/dasch-swiss/dsp-tools/issues/992)) ([891a889](https://github.com/dasch-swiss/dsp-tools/commit/891a8890c9acaf19ac252d1c9c525b2dea79bdda))
* **ci:** fix flaky CI tests in rosetta repo (DEV-3733) ([#990](https://github.com/dasch-swiss/dsp-tools/issues/990)) ([544923f](https://github.com/dasch-swiss/dsp-tools/commit/544923fe59f51724010b93c668b557c0260e1bb0))
* **ci:** fix release-please (DEV-3730) ([#999](https://github.com/dasch-swiss/dsp-tools/issues/999)) ([4798d77](https://github.com/dasch-swiss/dsp-tools/commit/4798d77ef0d76f820f64c0209cd9fc5ff2e7d4be))
* **ci:** move changelog (DEV-3730) ([#1000](https://github.com/dasch-swiss/dsp-tools/issues/1000)) ([0fae3e7](https://github.com/dasch-swiss/dsp-tools/commit/0fae3e75d952dbf31931ba840e90aea0bb983082))
* **ci:** use GITHUB_TOKEN instead of GH_TOKEN, move CHANGELOG.md back (DEV-3730) ([#1002](https://github.com/dasch-swiss/dsp-tools/issues/1002)) ([1f149de](https://github.com/dasch-swiss/dsp-tools/commit/1f149de76b77b4f36a65bb602faf07750fb35281))
* **excel2xml:** support backslash in make_text_prop() (DEV-3377) ([#991](https://github.com/dasch-swiss/dsp-tools/issues/991)) ([6e301d0](https://github.com/dasch-swiss/dsp-tools/commit/6e301d016168d44d3f1957f5751ac4467759a332))
* **excel2xml:** support named character references in make_text_prop() (DEV-3738) ([#1007](https://github.com/dasch-swiss/dsp-tools/issues/1007)) ([324c00a](https://github.com/dasch-swiss/dsp-tools/commit/324c00a80c46091cefaa63411604bb76c3a18b47))
* remove GH_TOKEN from release workflows (DEV-3737) ([#1006](https://github.com/dasch-swiss/dsp-tools/issues/1006)) ([1c4f6f1](https://github.com/dasch-swiss/dsp-tools/commit/1c4f6f1814c9f536bf3866f4cb65b593f40c4acc))
* **start-stack:** fix display issue in DSP-APP on localhost (DEV-3745) ([#1008](https://github.com/dasch-swiss/dsp-tools/issues/1008)) ([b2d51ca](https://github.com/dasch-swiss/dsp-tools/commit/b2d51ca97f05bba16e76d36dea7451b3602b0a16))
* **xmlupload:** OntologyConstraintException should not interrupt an xmlupload (DEV-3724) ([#995](https://github.com/dasch-swiss/dsp-tools/issues/995)) ([50ab6bf](https://github.com/dasch-swiss/dsp-tools/commit/50ab6bfd4c4c0fbced6a4bbaed4bee371276b673))


### Maintenance

* add yamlfmt to pre-commit ([#1009](https://github.com/dasch-swiss/dsp-tools/issues/1009)) ([569c161](https://github.com/dasch-swiss/dsp-tools/commit/569c161cf2c286765734e7f690212d160a2058ac))
* bump start-stack to 2024.06.01 ([#1024](https://github.com/dasch-swiss/dsp-tools/issues/1024)) ([991c6bc](https://github.com/dasch-swiss/dsp-tools/commit/991c6bce2132ed744cfae6a4e1611945a9dae90c))
* **ci:** after every PR merge, upload test coverage report for main (DEV-3731) ([#1010](https://github.com/dasch-swiss/dsp-tools/issues/1010)) ([c76b787](https://github.com/dasch-swiss/dsp-tools/commit/c76b787446005dc738a23d08c2a5c58b5a3f40f0))
* **ci:** only post codecov comment if coverage changes ([#1015](https://github.com/dasch-swiss/dsp-tools/issues/1015)) ([8bee0ec](https://github.com/dasch-swiss/dsp-tools/commit/8bee0ec03758042407fb4d1243c820518260748a))
* **deps-dev:** bump the all-dependencies group with 6 updates ([#998](https://github.com/dasch-swiss/dsp-tools/issues/998)) ([99ef810](https://github.com/dasch-swiss/dsp-tools/commit/99ef810b0847f13629818146740ec34bf210ab77))
* **deps:** bump the all-dependencies group with 4 updates ([#1013](https://github.com/dasch-swiss/dsp-tools/issues/1013)) ([5a1ac6e](https://github.com/dasch-swiss/dsp-tools/commit/5a1ac6ef36886bbdf73ecd2dfbd4845b1a7efe22))
* **deps:** bump urllib3 from 2.2.1 to 2.2.2 ([#1023](https://github.com/dasch-swiss/dsp-tools/issues/1023)) ([bac6c69](https://github.com/dasch-swiss/dsp-tools/commit/bac6c69196952bf80694aacb720e6685d9d9091c))
* fix some low-hanging linter warnings ([#1019](https://github.com/dasch-swiss/dsp-tools/issues/1019)) ([70beea3](https://github.com/dasch-swiss/dsp-tools/commit/70beea3467143d8f5e80f318718a6f75fad572a9))
* fix typo ([#1018](https://github.com/dasch-swiss/dsp-tools/issues/1018)) ([df59932](https://github.com/dasch-swiss/dsp-tools/commit/df59932d4e72a3f465d5beeddd0aee6c1d5f9649))
* replace deprecated PR title checker (DEV-3750) ([#1016](https://github.com/dasch-swiss/dsp-tools/issues/1016)) ([e4cd784](https://github.com/dasch-swiss/dsp-tools/commit/e4cd784293db8dc3a3a99c9e060f837b9e8688a8))
* **start-stack:** don't print that stack is ready before it is ready ([#997](https://github.com/dasch-swiss/dsp-tools/issues/997)) ([9317df2](https://github.com/dasch-swiss/dsp-tools/commit/9317df24904338782892cd0194dcfdb97b2588e9))
* **test:** add typing for test_ingest.py ([#1020](https://github.com/dasch-swiss/dsp-tools/issues/1020)) ([c959d31](https://github.com/dasch-swiss/dsp-tools/commit/c959d311df7789d0d1f5f0d06d3c455b836888ff))
* use yamllint ([#1011](https://github.com/dasch-swiss/dsp-tools/issues/1011)) ([ddb47fd](https://github.com/dasch-swiss/dsp-tools/commit/ddb47fd9c904268ebc02d739c768093a41955a79))
* **xmlupload:** serialise boolean value (DEV-3713) ([#988](https://github.com/dasch-swiss/dsp-tools/issues/988)) ([92d3c64](https://github.com/dasch-swiss/dsp-tools/commit/92d3c643e0d4f560a7d2ece4278718d4fc112c6b))


### Documentation

* fix hierarchy of headings in cli-commands ([#1012](https://github.com/dasch-swiss/dsp-tools/issues/1012)) ([210965d](https://github.com/dasch-swiss/dsp-tools/commit/210965d399615d400610bfe7533fef900937ac72))

## [8.1.0](https://github.com/dasch-swiss/dsp-tools/compare/v8.0.0...v8.1.0) (2024-06-04)


### Enhancements

* add IIIF image support (DEV-3507) ([#946](https://github.com/dasch-swiss/dsp-tools/issues/946)) ([aa3eabb](https://github.com/dasch-swiss/dsp-tools/commit/aa3eabb1451c52c97091d0ed86c830379b052d22))
* **xmlupload:** interrupt if a resource cannot be created due to server failure (DEV-3444) ([#954](https://github.com/dasch-swiss/dsp-tools/issues/954)) ([debc0b3](https://github.com/dasch-swiss/dsp-tools/commit/debc0b3eee4a669933e5c6dcbf175673f8ef3f04))


### Bug Fixes

* **xmlupload:** improve ingest performance by reusing session (DEV-3714) ([#986](https://github.com/dasch-swiss/dsp-tools/issues/986)) ([d818f5d](https://github.com/dasch-swiss/dsp-tools/commit/d818f5d885c0cc94d9169f16a3921f97ec0cfc18))


### Maintenance

* **deps:** bump the all-dependencies group with 9 updates ([#984](https://github.com/dasch-swiss/dsp-tools/issues/984)) ([1611d65](https://github.com/dasch-swiss/dsp-tools/commit/1611d6506452f65b12946b1ae4b020aa3478f378))
* fix `poetry exec clean` ([#983](https://github.com/dasch-swiss/dsp-tools/issues/983)) ([1721b1c](https://github.com/dasch-swiss/dsp-tools/commit/1721b1c926a0d6c629872f611e54c7dc0e022fbc))
* **start-stack:** print useful error if Docker is not running ([#980](https://github.com/dasch-swiss/dsp-tools/issues/980)) ([25c036c](https://github.com/dasch-swiss/dsp-tools/commit/25c036c38bd84bdfdabb17244ab6d2893d9abfcd))
* **start-stack:** remove network from docker-compose.yml ([#981](https://github.com/dasch-swiss/dsp-tools/issues/981)) ([ea6fa08](https://github.com/dasch-swiss/dsp-tools/commit/ea6fa0861359d825e3eb6b2c122ecff67ccbb5af))
* **start-stack:** remove unnecessary config from docker-compose.yml ([#982](https://github.com/dasch-swiss/dsp-tools/issues/982)) ([549d053](https://github.com/dasch-swiss/dsp-tools/commit/549d053506f8d3fd7b1a2e7aedd9d99eeeb751d3))
* update dependencies ([#977](https://github.com/dasch-swiss/dsp-tools/issues/977)) ([9473a7e](https://github.com/dasch-swiss/dsp-tools/commit/9473a7ef6448f25f25143c17c6717b6470cff0f5))


### Documentation

* **create:** fix: descriptions are required in JSON  ([#985](https://github.com/dasch-swiss/dsp-tools/issues/985)) ([00c8072](https://github.com/dasch-swiss/dsp-tools/commit/00c80722cb2d21f0f70027d71f4d49352ad0181f))

## [8.0.0](https://github.com/dasch-swiss/dsp-tools/compare/v7.2.0...v8.0.0) (2024-05-22)


### ⚠ BREAKING CHANGES

* add support for video and audio segments, remove isSequenceOf and standalone interval value (DEV-3439) ([#933](https://github.com/dasch-swiss/dsp-tools/issues/933))

### Enhancements

* add support for video and audio segments, remove isSequenceOf and standalone interval value (DEV-3439) ([#933](https://github.com/dasch-swiss/dsp-tools/issues/933)) ([391da7f](https://github.com/dasch-swiss/dsp-tools/commit/391da7fb82252d2152f386aa489d57c58839bbe3))


### Bug Fixes

* **excel2json:** erroneous groupby in new-excel2json lists (DEV-3660) ([#963](https://github.com/dasch-swiss/dsp-tools/issues/963)) ([46fbe95](https://github.com/dasch-swiss/dsp-tools/commit/46fbe9533b5b7fe7c0d59f7004b4e28fb056744a))
* **excel2json:** resources don't crash if optional columns are missing (DEV-3516) ([#974](https://github.com/dasch-swiss/dsp-tools/issues/974)) ([db2df0a](https://github.com/dasch-swiss/dsp-tools/commit/db2df0adafde5c3235374ecc56d31fca83e09189))
* **mypy:** prevent possibly unbound variables (DEV-3657) ([#962](https://github.com/dasch-swiss/dsp-tools/issues/962)) ([1be2259](https://github.com/dasch-swiss/dsp-tools/commit/1be22590506d98f88040e7cbcb6a486f85b9d784))
* **xmlupload:** permission for uri value serialise (DEV-3630) ([#958](https://github.com/dasch-swiss/dsp-tools/issues/958)) ([79a11bb](https://github.com/dasch-swiss/dsp-tools/commit/79a11bbfebcd6820bf072cddb37977fa8b54e3c9))


### Maintenance

* bump start-stack to 2024.05.02 ([#975](https://github.com/dasch-swiss/dsp-tools/issues/975)) ([6c02a6a](https://github.com/dasch-swiss/dsp-tools/commit/6c02a6a11b53492d3b76498d433f00adec34f4f8))
* **deps:** bump requests from 2.31.0 to 2.32.0 ([#972](https://github.com/dasch-swiss/dsp-tools/issues/972)) ([092d4f7](https://github.com/dasch-swiss/dsp-tools/commit/092d4f7ec465bda8b6e5d36ddb5c7420010cf061))
* do not use ingest client in bulk upload scenario (DEV-3665) ([#966](https://github.com/dasch-swiss/dsp-tools/issues/966)) ([8614bbe](https://github.com/dasch-swiss/dsp-tools/commit/8614bbee598f731da36b01a73957830a7a234b6a))
* fix unbound variable error ([#961](https://github.com/dasch-swiss/dsp-tools/issues/961)) ([7c41507](https://github.com/dasch-swiss/dsp-tools/commit/7c41507841b75408945e560e12bb3490e6a3527c))
* reduce number of arguments in some functions ([#967](https://github.com/dasch-swiss/dsp-tools/issues/967)) ([f38f6b4](https://github.com/dasch-swiss/dsp-tools/commit/f38f6b4047385d43c9529ab28e864ebbe06df247))
* **ruff:** Update ruff to 0.4.4 ([#951](https://github.com/dasch-swiss/dsp-tools/issues/951)) ([316a736](https://github.com/dasch-swiss/dsp-tools/commit/316a736e9ecaad4c8311cdd944a2f3fd6e089267))
* streamline shared logic between upload workflows ([#969](https://github.com/dasch-swiss/dsp-tools/issues/969)) ([17750e0](https://github.com/dasch-swiss/dsp-tools/commit/17750e0bcac776b3c8f2dbd1b6166a88253a78d9))
* Use dsp-ingest instead of sipi for upload of assets  (DEV-3620) ([#959](https://github.com/dasch-swiss/dsp-tools/issues/959)) ([c797010](https://github.com/dasch-swiss/dsp-tools/commit/c7970109a9c0d4543d383a91edaa093b2c76aaac))
* **xmlupload:** add serialise value for URI (DEV-3624) ([#955](https://github.com/dasch-swiss/dsp-tools/issues/955)) ([0289294](https://github.com/dasch-swiss/dsp-tools/commit/0289294ce6cccf8a0c1ca9bef0873f708bd537cf))
* **xmlupload:** disallow +/- in interval property ([#952](https://github.com/dasch-swiss/dsp-tools/issues/952)) ([871f312](https://github.com/dasch-swiss/dsp-tools/commit/871f312dde2f19788203b3dde05de5cdfd20f7e6))
* **xmlupload:** handle error wider above in the call stack ([#960](https://github.com/dasch-swiss/dsp-tools/issues/960)) ([c7ba637](https://github.com/dasch-swiss/dsp-tools/commit/c7ba637ad22ab62eed71e3d9b5ca7d7d0a436fae))
* **xmlupload:** refactor resource creation ([#917](https://github.com/dasch-swiss/dsp-tools/issues/917)) ([cdad095](https://github.com/dasch-swiss/dsp-tools/commit/cdad095f46f8eeded0b521b80341ef95ce0823e5))
* **xmlupload:** reorganise models file ([#953](https://github.com/dasch-swiss/dsp-tools/issues/953)) ([6d90b8f](https://github.com/dasch-swiss/dsp-tools/commit/6d90b8fb401965dd2a651b1dc114ef0226bfd3a0))
* **xmlupload:** serialise int value with rdflib (DEV-3626) ([#957](https://github.com/dasch-swiss/dsp-tools/issues/957)) ([0150fd6](https://github.com/dasch-swiss/dsp-tools/commit/0150fd6c5cf5e0301aeadef06f92de719ec167cf))
* **xmlupload:** value models ([#949](https://github.com/dasch-swiss/dsp-tools/issues/949)) ([c69c963](https://github.com/dasch-swiss/dsp-tools/commit/c69c96363b0184637d1a043c07f35194579d5b72))

## [7.2.0](https://github.com/dasch-swiss/dsp-tools/compare/v7.1.3...v7.2.0) (2024-05-08)


### Enhancements

* **excel2xml:** if value is not valid, print warning instead of raising an error (only where it is possible) (DEV-3571) ([#938](https://github.com/dasch-swiss/dsp-tools/issues/938)) ([3ae536d](https://github.com/dasch-swiss/dsp-tools/commit/3ae536df478bc4fa1c871d151c199de03f608239))
* **new-excel2json:** new lists section and excel (DEV-3462) ([#916](https://github.com/dasch-swiss/dsp-tools/issues/916)) ([92cf58d](https://github.com/dasch-swiss/dsp-tools/commit/92cf58dee25edcd1e078720b6eba950ce2fd1a10))
* **start-stack:** make pre-loaded projects on localhost optional (DEV-3560) ([#932](https://github.com/dasch-swiss/dsp-tools/issues/932)) ([d8ab847](https://github.com/dasch-swiss/dsp-tools/commit/d8ab84769fc6c7c7a451c41dc30fccc4184f9468))


### Bug Fixes

* warning_config recursive calls (DEV-3542) ([#929](https://github.com/dasch-swiss/dsp-tools/issues/929)) ([20b8517](https://github.com/dasch-swiss/dsp-tools/commit/20b8517b3cd686c927ac181830ed306713a7b822))


### Maintenance

* add DspToolsUserWarning class  ([#936](https://github.com/dasch-swiss/dsp-tools/issues/936)) ([fd0871d](https://github.com/dasch-swiss/dsp-tools/commit/fd0871daf6ad19cc3548b1baab1d1ffd666f37df))
* add ruff ignore to pre-commit hook ([#940](https://github.com/dasch-swiss/dsp-tools/issues/940)) ([9b14121](https://github.com/dasch-swiss/dsp-tools/commit/9b14121e1de28c2e05ba383925d566c9a6bf81b5))
* bump start-stack to 2024.05.01 (DEV-3612) ([#944](https://github.com/dasch-swiss/dsp-tools/issues/944)) ([b1e5a46](https://github.com/dasch-swiss/dsp-tools/commit/b1e5a46718f4ce7f3c4a0344749921bff58c5136))
* **deps-dev:** bump jinja2 from 3.1.3 to 3.1.4 ([#942](https://github.com/dasch-swiss/dsp-tools/issues/942)) ([5499e3b](https://github.com/dasch-swiss/dsp-tools/commit/5499e3bd015e44801897c1575d166cf2614bbe4f))
* **deps:** bump the all-dependencies group with 15 updates ([#934](https://github.com/dasch-swiss/dsp-tools/issues/934)) ([548b6b4](https://github.com/dasch-swiss/dsp-tools/commit/548b6b44bdb352bde3c95dbef919f32ebbb43d1d))
* fix typo ([#927](https://github.com/dasch-swiss/dsp-tools/issues/927)) ([e52a8ce](https://github.com/dasch-swiss/dsp-tools/commit/e52a8ce03d53205e42e1a9235afa62967a1fac07))
* prepend warning message with category ([#937](https://github.com/dasch-swiss/dsp-tools/issues/937)) ([e5bbb83](https://github.com/dasch-swiss/dsp-tools/commit/e5bbb83e79fb254ea8e96251845e2be332812d67))

## [7.1.3](https://github.com/dasch-swiss/dsp-tools/compare/v7.1.2...v7.1.3) (2024-04-24)


### Bug Fixes

* allow slashes and semicola in query part of URL (DEV-3480) ([#910](https://github.com/dasch-swiss/dsp-tools/issues/910)) ([af02895](https://github.com/dasch-swiss/dsp-tools/commit/af02895d444340aad8370f4fa3d66882dabbfe77))


### Maintenance

* add "Deprecated" section in release notes ([#918](https://github.com/dasch-swiss/dsp-tools/issues/918)) ([8b24372](https://github.com/dasch-swiss/dsp-tools/commit/8b24372bf8ff9559e32350864e2afb7f19ef1ae5))
* bump start-stack to 2024.04.02 ([#923](https://github.com/dasch-swiss/dsp-tools/issues/923)) ([daacd16](https://github.com/dasch-swiss/dsp-tools/commit/daacd16b5568365e627452e077a9dfb8293f9605))
* bump versions of pre-commit hooks ([#914](https://github.com/dasch-swiss/dsp-tools/issues/914)) ([7102e94](https://github.com/dasch-swiss/dsp-tools/commit/7102e9463d86020bfc33308f8271b65526e8dacc))
* **ci:** fix ruff format checking ([#915](https://github.com/dasch-swiss/dsp-tools/issues/915)) ([270dc6f](https://github.com/dasch-swiss/dsp-tools/commit/270dc6f71d7334270364766c3cb1a07b62b68293))
* **deps:** bump idna from 3.6 to 3.7 ([#912](https://github.com/dasch-swiss/dsp-tools/issues/912)) ([4c7bc29](https://github.com/dasch-swiss/dsp-tools/commit/4c7bc29759cf15aaa1113510fd9cbfbbc836c064))
* fix excel2xml testdata ([#921](https://github.com/dasch-swiss/dsp-tools/issues/921)) ([1771f5f](https://github.com/dasch-swiss/dsp-tools/commit/1771f5fe3a4a11fde32f174fd90a07162012d062))
* small fixes in pyproject.toml ([#913](https://github.com/dasch-swiss/dsp-tools/issues/913)) ([ffa6cf3](https://github.com/dasch-swiss/dsp-tools/commit/ffa6cf36b3e437b5785c9cefe81fe9e1b28aa729))


### Deprecated

* deprecate isSequenceOf (DEV-3525) ([#920](https://github.com/dasch-swiss/dsp-tools/issues/920)) ([b742ef8](https://github.com/dasch-swiss/dsp-tools/commit/b742ef89441c7591149717dbcb66f6b04b856787))

## [7.1.2](https://github.com/dasch-swiss/dsp-tools/compare/v7.1.1...v7.1.2) (2024-04-10)


### Bug Fixes

* **excel2json:** if gui_order is empty no warning is longer displayed (DEV-3469) ([#908](https://github.com/dasch-swiss/dsp-tools/issues/908)) ([a278e3e](https://github.com/dasch-swiss/dsp-tools/commit/a278e3e0f9b623978dc46772b3fd1b0ea4e98c73))
* excel2properties no longer crashes if optional columns are missing (DEV-3468) ([#907](https://github.com/dasch-swiss/dsp-tools/issues/907)) ([523d55b](https://github.com/dasch-swiss/dsp-tools/commit/523d55b410ad3e1ae1e7c80c8c47d600000c960d))


### Maintenance

* add type annotations for pandas and networkx ([#896](https://github.com/dasch-swiss/dsp-tools/issues/896)) ([bb0b3c6](https://github.com/dasch-swiss/dsp-tools/commit/bb0b3c6eb027eeba4f4b4024646362ae5b4bb51b))
* bump start-stack to 2024.04.01 ([#905](https://github.com/dasch-swiss/dsp-tools/issues/905)) ([04faeec](https://github.com/dasch-swiss/dsp-tools/commit/04faeec660fdf26d1935881794dfedfd3953a08a))
* **deps:** bump the all-dependencies group with 10 updates ([#894](https://github.com/dasch-swiss/dsp-tools/issues/894)) ([0e66199](https://github.com/dasch-swiss/dsp-tools/commit/0e661991df1cf2bbf91a253c0149e50dd77c849d))
* remove .gitmodules file  ([#897](https://github.com/dasch-swiss/dsp-tools/issues/897)) ([64e4fe3](https://github.com/dasch-swiss/dsp-tools/commit/64e4fe3d0ed7b0adceb14b32cbd24afa403b38ed))
* set api log level in docker-compose.yml ([#899](https://github.com/dasch-swiss/dsp-tools/issues/899)) ([2a8d574](https://github.com/dasch-swiss/dsp-tools/commit/2a8d5744c03c1829b3527d4bc385f7678d5ed6de))


### Documentation

* precise resume-xmlupload ([#900](https://github.com/dasch-swiss/dsp-tools/issues/900)) ([9611115](https://github.com/dasch-swiss/dsp-tools/commit/9611115c4d4a80fbca7b18feed2bbca389d8ff5a))
* reformulate incremental xmlupload ([#902](https://github.com/dasch-swiss/dsp-tools/issues/902)) ([e7063d0](https://github.com/dasch-swiss/dsp-tools/commit/e7063d0f697c87f9f2e6dac7f1effde29e8c372f))

## [7.1.1](https://github.com/dasch-swiss/dsp-tools/compare/v7.1.0...v7.1.1) (2024-03-27)


### Maintenance

* bump start-stack to 2024.03.02-hotfix ([#892](https://github.com/dasch-swiss/dsp-tools/issues/892)) ([d4733c6](https://github.com/dasch-swiss/dsp-tools/commit/d4733c63aaa215b88af0ea6354968342e0818766))

## [7.1.0](https://github.com/dasch-swiss/dsp-tools/compare/v7.0.0...v7.1.0) (2024-03-27)


### Enhancements

* **excel2xml:** allow for single tags in XML text (DEV-3427) ([#885](https://github.com/dasch-swiss/dsp-tools/issues/885)) ([c73b126](https://github.com/dasch-swiss/dsp-tools/commit/c73b126f040ce4432ca7a6bad952a3249c208133))
* save warnings and errors in second file with loguru (DEV-3406) ([#883](https://github.com/dasch-swiss/dsp-tools/issues/883)) ([7818325](https://github.com/dasch-swiss/dsp-tools/commit/781832568110c8d52e5ca8cfb0b81d4b53016554))


### Bug Fixes

* **create:** fix crash when no project is on the server new error (DEV-3420) ([#882](https://github.com/dasch-swiss/dsp-tools/issues/882)) ([ca9a674](https://github.com/dasch-swiss/dsp-tools/commit/ca9a6745477ec55f534ead020deb2eea3219c659))
* **xmlupload:** don't stop xmlupload when resource is wrong (DEV-3419) ([#880](https://github.com/dasch-swiss/dsp-tools/issues/880)) ([86795ec](https://github.com/dasch-swiss/dsp-tools/commit/86795ec5a12d84666a1707a571bb75a3e098396a))


### Maintenance

* bump start-stack to 2024.03.02 ([#891](https://github.com/dasch-swiss/dsp-tools/issues/891)) ([ce8d6be](https://github.com/dasch-swiss/dsp-tools/commit/ce8d6be663b2f68a0b7d2b9add2ef55567851863))
* **ci:** make logging file available after e2e test (DEV-3436) ([#887](https://github.com/dasch-swiss/dsp-tools/issues/887)) ([5825b3c](https://github.com/dasch-swiss/dsp-tools/commit/5825b3c191b4c905ee6ec671fa71e8fe5127f834))
* fix typo ([#889](https://github.com/dasch-swiss/dsp-tools/issues/889)) ([be0ae62](https://github.com/dasch-swiss/dsp-tools/commit/be0ae622654e9f042a6b90a17a68250030471ea1))
* remove timestamp from warnings.log ([#888](https://github.com/dasch-swiss/dsp-tools/issues/888)) ([8fb0842](https://github.com/dasch-swiss/dsp-tools/commit/8fb08429212feca3dbe62a2e3bdeaf7442abd902))
* **test:** make tests smaller in test_excel2xml_cli.py ([#884](https://github.com/dasch-swiss/dsp-tools/issues/884)) ([7418870](https://github.com/dasch-swiss/dsp-tools/commit/7418870f43011e721741e2bc41d9fe8c6bf95934))
* **test:** use regex.escape everywhere ([#886](https://github.com/dasch-swiss/dsp-tools/issues/886)) ([d0061db](https://github.com/dasch-swiss/dsp-tools/commit/d0061db9213bb1a206d965c416b412c5ea4f78b3))


### Documentation

* reformulate text-property and gui element ([#890](https://github.com/dasch-swiss/dsp-tools/issues/890)) ([8d7bb79](https://github.com/dasch-swiss/dsp-tools/commit/8d7bb79c291f219a2ed2530f5379ebe3851c5dc2))

## [7.0.0](https://github.com/dasch-swiss/dsp-tools/compare/v6.0.0...v7.0.0) (2024-03-13)


### ⚠ BREAKING CHANGES

* remove --verbose flag from xmlupload (DEV-3389) ([#869](https://github.com/dasch-swiss/dsp-tools/issues/869))

### Enhancements

* prompt before continuing when using an outdated version (DEV-3350) ([#850](https://github.com/dasch-swiss/dsp-tools/issues/850)) ([38907fa](https://github.com/dasch-swiss/dsp-tools/commit/38907faf4e2fc90832cd0c673076b12111e39dfb))
* remove --verbose flag from xmlupload (DEV-3389) ([#869](https://github.com/dasch-swiss/dsp-tools/issues/869)) ([1e2e170](https://github.com/dasch-swiss/dsp-tools/commit/1e2e170441d15dc7b3054aa50d6f9a93536e1fc0))
* resume an interrupted xmlupload (DEV-3323) ([#853](https://github.com/dasch-swiss/dsp-tools/issues/853)) ([4acf841](https://github.com/dasch-swiss/dsp-tools/commit/4acf8415674e33f5fb1a115f06208a89fb8bc3b1))
* **resume-xmlupload:** add option to skip the first resource (DEV-3412) ([#878](https://github.com/dasch-swiss/dsp-tools/issues/878)) ([a53785f](https://github.com/dasch-swiss/dsp-tools/commit/a53785ffe7926f9a8d7ca52549025260e6d92e70))


### Bug Fixes

* add "packaging" as dependency (DEV-3368) ([#856](https://github.com/dasch-swiss/dsp-tools/issues/856)) ([81508b0](https://github.com/dasch-swiss/dsp-tools/commit/81508b0c48599719c0bec84d19b680264592782d))
* **create:** fix crash when no project is on the server (DEV-3405) ([#875](https://github.com/dasch-swiss/dsp-tools/issues/875)) ([9607799](https://github.com/dasch-swiss/dsp-tools/commit/96077993fd5b5af5858960289b06a497d4f6f51b))
* don't retry on 404 project not found (DEV-3362) ([#857](https://github.com/dasch-swiss/dsp-tools/issues/857)) ([5c19f60](https://github.com/dasch-swiss/dsp-tools/commit/5c19f60375e7d0e073e895446714748ca3345255))
* don't retry on errors in the 400 range (DEV-3349) ([#877](https://github.com/dasch-swiss/dsp-tools/issues/877)) ([c543274](https://github.com/dasch-swiss/dsp-tools/commit/c5432740fa580547e7b935fbca32478b1d8f4602))
* **ingest:** ingest container must be part of knora-net (DEV-3370) ([#858](https://github.com/dasch-swiss/dsp-tools/issues/858)) ([cd018ee](https://github.com/dasch-swiss/dsp-tools/commit/cd018eed0a808ece566f39853a1f0a8d949e5687))
* **pypi:** prevent that PR merged into PR is published to pypi (DEV-3394) ([#871](https://github.com/dasch-swiss/dsp-tools/issues/871)) ([3d5e071](https://github.com/dasch-swiss/dsp-tools/commit/3d5e07195e84f8d5b79a85572d74d94a875a06e9))
* **release-please:** adapt version check (DEV-3363) ([#854](https://github.com/dasch-swiss/dsp-tools/issues/854)) ([d04b731](https://github.com/dasch-swiss/dsp-tools/commit/d04b73199a0d4728927e0766948a8c6771e80745))
* **resume-xmlupload:** make it impossible to resume after all resources have been created (DEV-3398) ([#865](https://github.com/dasch-swiss/dsp-tools/issues/865)) ([8aa5d30](https://github.com/dasch-swiss/dsp-tools/commit/8aa5d30831ff3a015ffef96c8bc8c1cd4e56ecb2))
* **resume-xmlupload:** make resource counting more user friendly (DEV-3397) ([#864](https://github.com/dasch-swiss/dsp-tools/issues/864)) ([2b5295d](https://github.com/dasch-swiss/dsp-tools/commit/2b5295d12f9650a8a480eb60f7344c3738681889))
* **xmlupload:** don't crash if the project has more than 50 errors (DEV-3364) ([#855](https://github.com/dasch-swiss/dsp-tools/issues/855)) ([a0be38e](https://github.com/dasch-swiss/dsp-tools/commit/a0be38efc1f94c9221e1338154c1edf7b73e350e))
* **xmlupload:** don't loose elements when stashing standoff properties (DEV-3151) ([#870](https://github.com/dasch-swiss/dsp-tools/issues/870)) ([c8e8966](https://github.com/dasch-swiss/dsp-tools/commit/c8e8966068f8f6d80b4d92137b9ba1fb15ae134d))
* **xmlupload:** exit with code 0 if xmlupload finishes with batch (DEV-3396) ([#863](https://github.com/dasch-swiss/dsp-tools/issues/863)) ([8a15973](https://github.com/dasch-swiss/dsp-tools/commit/8a159738ce0c920ad97e28a6a8d6d87a1f813c17))
* **xmlupload:** fix xmlupload text as xml when uploading stash (DEV-3361) ([#851](https://github.com/dasch-swiss/dsp-tools/issues/851)) ([79a643a](https://github.com/dasch-swiss/dsp-tools/commit/79a643a4916175e7404b920864147c8963f9608c))


### Maintenance

* bump start-stack to 2024.03.01 ([#879](https://github.com/dasch-swiss/dsp-tools/issues/879)) ([b1c8262](https://github.com/dasch-swiss/dsp-tools/commit/b1c8262134a5661a2563460e53ab1fcc37a7c9f9))
* **connection:** call specific error response codes (DEV-3339) ([#832](https://github.com/dasch-swiss/dsp-tools/issues/832)) ([d8531bd](https://github.com/dasch-swiss/dsp-tools/commit/d8531bdfc74704226717039d0466b3577c167105))
* **deps-dev:** bump the all-dependencies group with 5 updates ([#849](https://github.com/dasch-swiss/dsp-tools/issues/849)) ([4c8b942](https://github.com/dasch-swiss/dsp-tools/commit/4c8b9425114863d40a0eaa147693cf3b403626e3))
* **excel2xml:** better error message for invalid text values ([#861](https://github.com/dasch-swiss/dsp-tools/issues/861)) ([914acd8](https://github.com/dasch-swiss/dsp-tools/commit/914acd82877bc66461aa98a755f7a08b4bbf0f91))
* fix test_xml_validation_low_level.py ([#837](https://github.com/dasch-swiss/dsp-tools/issues/837)) ([3e758c7](https://github.com/dasch-swiss/dsp-tools/commit/3e758c7c64d832412448f701221cbf5ef69228b6))
* **project create:** add erroneously removed exc_info in logging (DEV-3294) ([#866](https://github.com/dasch-swiss/dsp-tools/issues/866)) ([19d1f25](https://github.com/dasch-swiss/dsp-tools/commit/19d1f2502d42b390b3ccbb208d17458803386bbf))
* ruff reformatting ([#867](https://github.com/dasch-swiss/dsp-tools/issues/867)) ([5ed62fc](https://github.com/dasch-swiss/dsp-tools/commit/5ed62fc3b132007bba5805066e2fbf4c6d7f3aca))
* ruff.lint.isort: force-single-line ([#840](https://github.com/dasch-swiss/dsp-tools/issues/840)) ([fb3c1d9](https://github.com/dasch-swiss/dsp-tools/commit/fb3c1d940b6aa6e91d5e224f64a1981f401a7b21))
* **test:** make integration test excel2json ([#841](https://github.com/dasch-swiss/dsp-tools/issues/841)) ([e5b0206](https://github.com/dasch-swiss/dsp-tools/commit/e5b0206326d06188ce8edca3886638a175678535))
* **test:** make integration test excel2xml ([#842](https://github.com/dasch-swiss/dsp-tools/issues/842)) ([8b12f8b](https://github.com/dasch-swiss/dsp-tools/commit/8b12f8b6d4b0f63aabbcdfea225cbfb5469d4c8e))
* **test:** make integration test general commands ([#846](https://github.com/dasch-swiss/dsp-tools/issues/846)) ([0e61eef](https://github.com/dasch-swiss/dsp-tools/commit/0e61eef6b37a16f53019c072559d50c7c75e6052))
* **test:** make integration test ingest-xmlupload ([#843](https://github.com/dasch-swiss/dsp-tools/issues/843)) ([fb58779](https://github.com/dasch-swiss/dsp-tools/commit/fb5877972fa6e76fc7b5f120b3b84b80caec88a5))
* **test:** make integration test project ([#844](https://github.com/dasch-swiss/dsp-tools/issues/844)) ([a7e0fc6](https://github.com/dasch-swiss/dsp-tools/commit/a7e0fc62fd67a0b4f227284d68e9cb7d5df2fed0))
* **test:** make integration test utils ([#847](https://github.com/dasch-swiss/dsp-tools/issues/847)) ([089c41d](https://github.com/dasch-swiss/dsp-tools/commit/089c41dc4899b3212f2227b0f887bd5f3a951da7))
* **test:** make integration test xmlupload ([#845](https://github.com/dasch-swiss/dsp-tools/issues/845)) ([f80cc90](https://github.com/dasch-swiss/dsp-tools/commit/f80cc9076ae4cca30e1bd87f190550fafbb9d218))
* xmlupload ([#852](https://github.com/dasch-swiss/dsp-tools/issues/852)) ([c8e6284](https://github.com/dasch-swiss/dsp-tools/commit/c8e6284739914babc9d1b73dcab92c9de7220140))


### Documentation

* add guarantee note for resume-xmlupload ([#868](https://github.com/dasch-swiss/dsp-tools/issues/868)) ([8747edd](https://github.com/dasch-swiss/dsp-tools/commit/8747edd671507203dd69598aa3e7cd688aa517b8))
* **excel2xml:** code examples in docstrings: prepend function names with their namespace ([#859](https://github.com/dasch-swiss/dsp-tools/issues/859)) ([7923a8c](https://github.com/dasch-swiss/dsp-tools/commit/7923a8cf912a437f990336d36fd8b0d671fa47cd))

## [6.0.0](https://github.com/dasch-swiss/dsp-tools/compare/v5.8.1...v6.0.0) (2024-02-28)


### ⚠ BREAKING CHANGES

* Remove fast-xmlupload command (DEV-3324) ([#830](https://github.com/dasch-swiss/dsp-tools/issues/830))

### Enhancements

* Remove fast-xmlupload command (DEV-3324) ([#830](https://github.com/dasch-swiss/dsp-tools/issues/830)) ([0c9d077](https://github.com/dasch-swiss/dsp-tools/commit/0c9d07775f9a48412a3ad7bf1cc8a0563ef180ce))
* **xmlupload:** check if text encoding in data conforms to type specified in ontology (DEV-3279) ([#821](https://github.com/dasch-swiss/dsp-tools/issues/821)) ([449f780](https://github.com/dasch-swiss/dsp-tools/commit/449f780e60ad3a0639d7600809be0b34e3a7e766))
* **xmlupload:** check if the encoding in the text-prop is consistent (DEV-3296) ([#818](https://github.com/dasch-swiss/dsp-tools/issues/818)) ([4ae8469](https://github.com/dasch-swiss/dsp-tools/commit/4ae8469262805d5983cf370a8842a65c7ae265ae))


### Bug Fixes

* don't crash when dsp-tools is run offline (DEV-3338) ([#833](https://github.com/dasch-swiss/dsp-tools/issues/833)) ([901b86d](https://github.com/dasch-swiss/dsp-tools/commit/901b86de4928d6995f77e996993ba6689aa5b5a0))
* **excel2json:** allow resources to have no cardinalities (DEV-3333) ([#834](https://github.com/dasch-swiss/dsp-tools/issues/834)) ([b55224a](https://github.com/dasch-swiss/dsp-tools/commit/b55224a5f98beee0bdbe1bea1a4e1741e6e7f0a7))


### Maintenance

* bump start-stack to 2024.02.02 ([#836](https://github.com/dasch-swiss/dsp-tools/issues/836)) ([f83ce78](https://github.com/dasch-swiss/dsp-tools/commit/f83ce78dc3188d5ebf8a3451de998c2433f4004f))
* correct docs in regard to gui-element of hasComment ([#816](https://github.com/dasch-swiss/dsp-tools/issues/816)) ([3f869d9](https://github.com/dasch-swiss/dsp-tools/commit/3f869d999fd3fce6bb1d2eafa770e946292ba115))
* fix typo in check_consistency_with_ontology.py ([#813](https://github.com/dasch-swiss/dsp-tools/issues/813)) ([bc01027](https://github.com/dasch-swiss/dsp-tools/commit/bc010274f221abae9d0544104bd7c9fb01cc067a))
* **ontology_client:** make retrieval of ontologies more flexible (DEV-3308) ([#820](https://github.com/dasch-swiss/dsp-tools/issues/820)) ([327f61e](https://github.com/dasch-swiss/dsp-tools/commit/327f61ee31ba82ad0839ac67e1828508cea5f7ac))
* refactor validate xml in preparation for extension ([#814](https://github.com/dasch-swiss/dsp-tools/issues/814)) ([652aa9f](https://github.com/dasch-swiss/dsp-tools/commit/652aa9f62991fe2b83dd0dea1944bb4878502ba0))
* remove docker as dependency ([#835](https://github.com/dasch-swiss/dsp-tools/issues/835)) ([7f98945](https://github.com/dasch-swiss/dsp-tools/commit/7f989453cacd84f5488e6dc8f63927c4c8ee6d7e))
* renaming functions of ontology checks in xmlupload ([#817](https://github.com/dasch-swiss/dsp-tools/issues/817)) ([e6b0e7d](https://github.com/dasch-swiss/dsp-tools/commit/e6b0e7d041b690136808dba4df12e0e01a4fb619))
* **test_xmlupload:** separate tests ([#824](https://github.com/dasch-swiss/dsp-tools/issues/824)) ([7333136](https://github.com/dasch-swiss/dsp-tools/commit/733313688f2c3b0b50d81b98c010ff15442cbd2f))
* **test:** add pytest entrypoint ([#823](https://github.com/dasch-swiss/dsp-tools/issues/823)) ([e31da78](https://github.com/dasch-swiss/dsp-tools/commit/e31da78a53e0e43bef2e1404ca2966505827581c))
* **test:** test_shared.py turn into pytest ([#826](https://github.com/dasch-swiss/dsp-tools/issues/826)) ([46e7743](https://github.com/dasch-swiss/dsp-tools/commit/46e774374be8c8d63dcc1b5ae40e04230d0a1ff3))
* **test:** test_upload_stashed_xml_texts.py turn into pytest ([#825](https://github.com/dasch-swiss/dsp-tools/issues/825)) ([755323f](https://github.com/dasch-swiss/dsp-tools/commit/755323fdab9c5cba218f0829f9b9cacabb4c717d))
* **test:** turn into pytest test_xmlupload.py ([#827](https://github.com/dasch-swiss/dsp-tools/issues/827)) ([c0d1c97](https://github.com/dasch-swiss/dsp-tools/commit/c0d1c977a1eed11c815c72cb62d56851ed935d19))
* **test:** turn xml_utils.py into pytest ([#828](https://github.com/dasch-swiss/dsp-tools/issues/828)) ([e97084f](https://github.com/dasch-swiss/dsp-tools/commit/e97084f28a1020d1bf37bfb6b768c55c450cd8a5))
* update data.xsd regarding TextValue encoding for hasComment ([#811](https://github.com/dasch-swiss/dsp-tools/issues/811)) ([af86b94](https://github.com/dasch-swiss/dsp-tools/commit/af86b94b1d6c357b270c9e3f7fa425c29d786f35))
* **xml_validation:** turn into pytest ([#815](https://github.com/dasch-swiss/dsp-tools/issues/815)) ([516a2de](https://github.com/dasch-swiss/dsp-tools/commit/516a2def27dc9fbba65faac13e13787a71a2dde6))
* **xmlupload:** improve parse xml function ([#819](https://github.com/dasch-swiss/dsp-tools/issues/819)) ([9947607](https://github.com/dasch-swiss/dsp-tools/commit/9947607039127a185d373b0b48537904110bd5e9))


### Documentation

* DSP-API uses "just" instead of "make" (DEV-3212) ([#753](https://github.com/dasch-swiss/dsp-tools/issues/753)) ([d5c8f97](https://github.com/dasch-swiss/dsp-tools/commit/d5c8f9722a6becbde46cad9ad5adf210206fb97c))

## [5.8.1](https://github.com/dasch-swiss/dsp-tools/compare/v5.8.0...v5.8.1) (2024-02-14)


### Maintenance

* bump start-stack to 2024.02.01 ([#806](https://github.com/dasch-swiss/dsp-tools/issues/806)) ([9080f47](https://github.com/dasch-swiss/dsp-tools/commit/9080f4734a387bd306c0bf78baa9dd6472210e81))
* **models-project:** remove all project update code ([#802](https://github.com/dasch-swiss/dsp-tools/issues/802)) ([1aa39a1](https://github.com/dasch-swiss/dsp-tools/commit/1aa39a1b61b7893eee4e54e4020d9a683b29ebb2))
* **models-user-project:** delete dead code ([#800](https://github.com/dasch-swiss/dsp-tools/issues/800)) ([12813bc](https://github.com/dasch-swiss/dsp-tools/commit/12813bc02c126c0caf49753506888f843598582f))
* remove dead parameter in ontology client ([#809](https://github.com/dasch-swiss/dsp-tools/issues/809)) ([8095ba3](https://github.com/dasch-swiss/dsp-tools/commit/8095ba37f9df897018d6fcfd43d70a34239b37c9))
* remove sourcery ([#805](https://github.com/dasch-swiss/dsp-tools/issues/805)) ([c3ccc36](https://github.com/dasch-swiss/dsp-tools/commit/c3ccc3646292a855682e1bdeb42f9dbab9f30e46))
* rename value.py file into formatted_text_value.py ([#807](https://github.com/dasch-swiss/dsp-tools/issues/807)) ([90af390](https://github.com/dasch-swiss/dsp-tools/commit/90af3906527f87dd33555be2c7cc344da60dded9))
* renaming functions in preparation for TextValue verification ([#808](https://github.com/dasch-swiss/dsp-tools/issues/808)) ([9f06f3f](https://github.com/dasch-swiss/dsp-tools/commit/9f06f3fe32ce49fa1241fda33bede08bff8e3a2b))
* **test-create-project:** turn unittests into pytests ([#804](https://github.com/dasch-swiss/dsp-tools/issues/804)) ([8c667a6](https://github.com/dasch-swiss/dsp-tools/commit/8c667a69d981d4dff0ca2f1fc3f8534c95d93ca0))

## [5.8.0](https://github.com/dasch-swiss/dsp-tools/compare/v5.7.0...v5.8.0) (2024-02-01)


### Enhancements

* **excel2json:** add optional column "subject" to properties.xlsx (DEV-3253) ([#777](https://github.com/dasch-swiss/dsp-tools/issues/777)) ([cf491e9](https://github.com/dasch-swiss/dsp-tools/commit/cf491e9499818f068bfbfb823a5652b63ddc7953))


### Bug Fixes

* don't crash if pip is not found (DEV-3256) ([#791](https://github.com/dasch-swiss/dsp-tools/issues/791)) ([15f6e31](https://github.com/dasch-swiss/dsp-tools/commit/15f6e310c20b2afe5a70c9c609aa86e362d3ff87))
* **xmlupload:** don't retry on OntologyConstraintException (DEV-3255) ([#783](https://github.com/dasch-swiss/dsp-tools/issues/783)) ([ef577ac](https://github.com/dasch-swiss/dsp-tools/commit/ef577ac5eb1a8c4a54820646b02b26e3cd6dbf4b))


### Maintenance

* bump start-stack to hotfixed 2024.01.01 ([#801](https://github.com/dasch-swiss/dsp-tools/issues/801)) ([b721fdd](https://github.com/dasch-swiss/dsp-tools/commit/b721fdd3b5c6c72137b74542b8f08620d61b7b2f))
* delete dead code fragments ([#792](https://github.com/dasch-swiss/dsp-tools/issues/792)) ([c5b9872](https://github.com/dasch-swiss/dsp-tools/commit/c5b987257fa41ba248fa43838edd03ee4ec3d3c6))
* **deps:** bump the all-dependencies group with 8 updates ([#787](https://github.com/dasch-swiss/dsp-tools/issues/787)) ([0c1a5e2](https://github.com/dasch-swiss/dsp-tools/commit/0c1a5e28ec400848a1a3c5225d69350cccfdd4d8))
* **excel2json-lists:** fix two ruff PLW0603 ([#778](https://github.com/dasch-swiss/dsp-tools/issues/778)) ([5f53c38](https://github.com/dasch-swiss/dsp-tools/commit/5f53c382741dfa7db270382ec3efa38e7258f6eb))
* **model-project:** fix one ruff PLR0912 ([#782](https://github.com/dasch-swiss/dsp-tools/issues/782)) ([25ad02d](https://github.com/dasch-swiss/dsp-tools/commit/25ad02d7fc808204cb578f78fcf4fc201371516e))
* **models-group:** delete unnecessary action object ([#794](https://github.com/dasch-swiss/dsp-tools/issues/794)) ([24fdc9f](https://github.com/dasch-swiss/dsp-tools/commit/24fdc9f287bda157fa66f8e4e89b995b0ed863e1))
* **models-listnode:** delete actions object ([#795](https://github.com/dasch-swiss/dsp-tools/issues/795)) ([f7a2ec9](https://github.com/dasch-swiss/dsp-tools/commit/f7a2ec976558f59ba31faae560f0487ceb0f5387))
* **models-listnode:** delete dead code ([#797](https://github.com/dasch-swiss/dsp-tools/issues/797)) ([fea23fd](https://github.com/dasch-swiss/dsp-tools/commit/fea23fdbd1e349b406df4f11fb819753f535e871))
* **models-ontology:** delete actions object ([#796](https://github.com/dasch-swiss/dsp-tools/issues/796)) ([28299fa](https://github.com/dasch-swiss/dsp-tools/commit/28299faca4315173e45a09d21ed55f277b6751ad))
* **models-project:** delete dead code ([#798](https://github.com/dasch-swiss/dsp-tools/issues/798)) ([dcdbaaf](https://github.com/dasch-swiss/dsp-tools/commit/dcdbaafcd473f925d68981e8714ff9b1bbb1b89a))
* **models-propertyclass:** fix PLR0912 ([#784](https://github.com/dasch-swiss/dsp-tools/issues/784)) ([51d4265](https://github.com/dasch-swiss/dsp-tools/commit/51d426541ff618f7ccb80cb32457bb011463d34b))
* **models-resourceclass:** fix ruff PLR0912 ([#788](https://github.com/dasch-swiss/dsp-tools/issues/788)) ([ed10c27](https://github.com/dasch-swiss/dsp-tools/commit/ed10c2718e440e7edc057c943488d7838ef3057e))
* **models-user:** fix three ruff PLR0912 ([#780](https://github.com/dasch-swiss/dsp-tools/issues/780)) ([820fc25](https://github.com/dasch-swiss/dsp-tools/commit/820fc254fe80cd277fa623011fcc320e48485d7f))
* **project_client:** delete dead code ([#793](https://github.com/dasch-swiss/dsp-tools/issues/793)) ([b5963de](https://github.com/dasch-swiss/dsp-tools/commit/b5963ded9a33756a03e096769a4725cdc61883a2))
* **project_validate:** fix one ruff PLR0912 ([#781](https://github.com/dasch-swiss/dsp-tools/issues/781)) ([9ccd2a7](https://github.com/dasch-swiss/dsp-tools/commit/9ccd2a7a8cced10af818fcaacc8ad60494d4cf0b))
* **propertyclass-resourceclass:** delete dead code ([#799](https://github.com/dasch-swiss/dsp-tools/issues/799)) ([d17b656](https://github.com/dasch-swiss/dsp-tools/commit/d17b656e5ab7181b2d6e266ab115117632be5f66))
* remove dead code with vulture ([#790](https://github.com/dasch-swiss/dsp-tools/issues/790)) ([aba9aef](https://github.com/dasch-swiss/dsp-tools/commit/aba9aefa8af8bf9086a102118b2f69d5856a84f2))
* remove ruff ignore PLR0912 (Too many branches) ([#789](https://github.com/dasch-swiss/dsp-tools/issues/789)) ([e93b049](https://github.com/dasch-swiss/dsp-tools/commit/e93b049b7937757842045ec38b9da1c14faa6b43))
* **test_create_get_xmlupload:** fix one ruff PLR0912 ([#785](https://github.com/dasch-swiss/dsp-tools/issues/785)) ([c09c0c6](https://github.com/dasch-swiss/dsp-tools/commit/c09c0c6c2b7f5ceef1e35a65bb924ea1ded07911))
* use pytest's tmp_path fixture ([#786](https://github.com/dasch-swiss/dsp-tools/issues/786)) ([c01a08f](https://github.com/dasch-swiss/dsp-tools/commit/c01a08f0925d3813366d6bfe32d0e89bdee80d94))

## [5.7.0](https://github.com/dasch-swiss/dsp-tools/compare/v5.6.0...v5.7.0) (2024-01-31)


### Enhancements

* **excel2xml:** find_date_in_string(): allow time spans of 1 day (DEV-3154) ([#720](https://github.com/dasch-swiss/dsp-tools/issues/720)) ([59b5d16](https://github.com/dasch-swiss/dsp-tools/commit/59b5d16818fd599766b6c6eb2cd9d536d020d415))
* **excel2xml:** make_bitstream_prop(): make file existence check opt-in (DEV-3113) ([#709](https://github.com/dasch-swiss/dsp-tools/issues/709)) ([1f68943](https://github.com/dasch-swiss/dsp-tools/commit/1f68943bfce58a1ebafc4d1172139e6ac6fe46f3))
* **excel2xml:** support 2-digit-years in find_date_in_string() (DEV-2633) ([#711](https://github.com/dasch-swiss/dsp-tools/issues/711)) ([15d3493](https://github.com/dasch-swiss/dsp-tools/commit/15d3493c29a1ab9cf3a099bb471d4dde841a443f))
* **ingest-upload:** create new ingest xmlupload cli command (DEV-3019) ([#670](https://github.com/dasch-swiss/dsp-tools/issues/670)) ([5745190](https://github.com/dasch-swiss/dsp-tools/commit/5745190f2950f7aacdf4754b5d258f44c391c7fd))
* **ingest-xmlupload:** add support for dumping HTTP requests (DEV-3167) ([#729](https://github.com/dasch-swiss/dsp-tools/issues/729)) ([a02dda5](https://github.com/dasch-swiss/dsp-tools/commit/a02dda55d7259a921d3a6bef2edc6fc2acf03053))
* option for custom headers in HTTP requests (DEV-3145) ([#702](https://github.com/dasch-swiss/dsp-tools/issues/702)) ([0cbc78a](https://github.com/dasch-swiss/dsp-tools/commit/0cbc78a57cdb1ee4bdb78204413452f02f17625a))


### Bug Fixes

* add termcolor as main dependency (DEV-3149) ([#706](https://github.com/dasch-swiss/dsp-tools/issues/706)) ([4f6cd6d](https://github.com/dasch-swiss/dsp-tools/commit/4f6cd6d8cec0c31d8486022b1f6b9eed7cee7165))
* don't retry login when credentials are invalid (DEV-3224) ([#763](https://github.com/dasch-swiss/dsp-tools/issues/763)) ([41d8217](https://github.com/dasch-swiss/dsp-tools/commit/41d8217952d04221ab9f0b522a8910539dadc159))
* **excel2xml, xmlupload:** allow commas in URLs (DEV-3183) ([#742](https://github.com/dasch-swiss/dsp-tools/issues/742)) ([1ee6e36](https://github.com/dasch-swiss/dsp-tools/commit/1ee6e3693c69b9ae2801a9398a33f283b163f528))
* **excel2xml:** make_text_prop: allow &lt;, &gt;, & in rich texts (DEV-3131) ([#691](https://github.com/dasch-swiss/dsp-tools/issues/691)) ([228c79f](https://github.com/dasch-swiss/dsp-tools/commit/228c79f7113ea5719ed827f74b06a3f1e2264bf8))
* fix wrong resolution of merge conflict (DEV-3161) ([#726](https://github.com/dasch-swiss/dsp-tools/issues/726)) ([c81c94d](https://github.com/dasch-swiss/dsp-tools/commit/c81c94d624a64649682c3708f48ce5fb23e33d7b))
* fully mask passwords in logfile (DEV-3225) ([#761](https://github.com/dasch-swiss/dsp-tools/issues/761)) ([87c03d4](https://github.com/dasch-swiss/dsp-tools/commit/87c03d4ec3a090769f5494b8daf2d7361363128f))
* include stack trace in log file (DEV-3157) ([#723](https://github.com/dasch-swiss/dsp-tools/issues/723)) ([9046792](https://github.com/dasch-swiss/dsp-tools/commit/904679281d5aa32e7930b127e8f470f47ce37895))
* increase timeout to prevent doubled resources (DEV-3114) ([#698](https://github.com/dasch-swiss/dsp-tools/issues/698)) ([930df8f](https://github.com/dasch-swiss/dsp-tools/commit/930df8f2e6cdd66b6b8e01cf42c121207b20ba76))
* **ingest-xmlupload:** apply mapping.csv even if extension has wrong casing (DEV-3197) ([#749](https://github.com/dasch-swiss/dsp-tools/issues/749)) ([bac7c79](https://github.com/dasch-swiss/dsp-tools/commit/bac7c796db99e40ae37e22e4e7546d4dd6816cdb))
* **ingest-xmlupload:** file check: handle absolute vs. relative paths, save feedback file correctly (DEV-3162) ([#727](https://github.com/dasch-swiss/dsp-tools/issues/727)) ([c6d2169](https://github.com/dasch-swiss/dsp-tools/commit/c6d21697e030a1ae4346c32686f9b63ea02e1d50))
* prevent crash when venv isn't activated correctly (DEV-3233) ([#765](https://github.com/dasch-swiss/dsp-tools/issues/765)) ([6d339ed](https://github.com/dasch-swiss/dsp-tools/commit/6d339ed724f823b645e05c2d7a6607938ffecf89))
* properly log requests and their responses (DEV-3186) ([#745](https://github.com/dasch-swiss/dsp-tools/issues/745)) ([8296254](https://github.com/dasch-swiss/dsp-tools/commit/8296254cfeb54572da2e47788f389246176ecdba))
* restore authorization header after ConnectionError (DEV-3190) ([#744](https://github.com/dasch-swiss/dsp-tools/issues/744)) ([d03be2a](https://github.com/dasch-swiss/dsp-tools/commit/d03be2a6e69fde47fb4ad7661be14ef1fbec5901))
* retry mechanism again catches return codes in the 500 range (DEV-3177) ([#740](https://github.com/dasch-swiss/dsp-tools/issues/740)) ([c927c21](https://github.com/dasch-swiss/dsp-tools/commit/c927c21ebc6ea078417f4b7dc040779a1ba57ef1))
* **xmlupload:** retry on all non-OK response statuses (DEV-3214) ([#754](https://github.com/dasch-swiss/dsp-tools/issues/754)) ([b85e806](https://github.com/dasch-swiss/dsp-tools/commit/b85e80601b915f8fcf25dcaf9bd3059f72ee9c79))


### Maintenance

* add PermanentConnectionError to make BaseError slimmer (DEV-3192) ([#741](https://github.com/dasch-swiss/dsp-tools/issues/741)) ([ed60319](https://github.com/dasch-swiss/dsp-tools/commit/ed603194857fa714773a6ba83db65940e95d7769))
* add permission to test data ([#768](https://github.com/dasch-swiss/dsp-tools/issues/768)) ([a4d93fc](https://github.com/dasch-swiss/dsp-tools/commit/a4d93fcba57de55a801157f89ac248a4a6a42a95))
* add ruff rule to prevent TODO comments ([#738](https://github.com/dasch-swiss/dsp-tools/issues/738)) ([e897496](https://github.com/dasch-swiss/dsp-tools/commit/e89749639a02f96b6b2030a94c62b8f059c5a52b))
* add User-Agent header to HTTP requests ([#737](https://github.com/dasch-swiss/dsp-tools/issues/737)) ([85e363b](https://github.com/dasch-swiss/dsp-tools/commit/85e363ba2ec86cc11f7dce60dba092504e398baa))
* avoid mutable default values in class attributes (DEV-3234) ([#764](https://github.com/dasch-swiss/dsp-tools/issues/764)) ([1d9e5de](https://github.com/dasch-swiss/dsp-tools/commit/1d9e5de73499b4c9cefa118876c326445869fdf4))
* bump all dependencies ([#734](https://github.com/dasch-swiss/dsp-tools/issues/734)) ([d3e238b](https://github.com/dasch-swiss/dsp-tools/commit/d3e238beb2a115f025ce99b7a0cc4861b26feaaf))
* bump GitHub actions that use a deprecated NodeJS version ([#766](https://github.com/dasch-swiss/dsp-tools/issues/766)) ([84e8ec0](https://github.com/dasch-swiss/dsp-tools/commit/84e8ec04557d1a28200b9f1cbb96a647e465b63f))
* bump start-stack to 2024.01.01 ([#771](https://github.com/dasch-swiss/dsp-tools/issues/771)) ([2997c05](https://github.com/dasch-swiss/dsp-tools/commit/2997c05b2ae988f924970bac7b50c9a931fc6fcb))
* **ci:** move setup into reusable workflow ([#715](https://github.com/dasch-swiss/dsp-tools/issues/715)) ([a3799ce](https://github.com/dasch-swiss/dsp-tools/commit/a3799ce88264806e4ef52ceef46714803bafe012))
* **ci:** revert changes related to merge queue ([#719](https://github.com/dasch-swiss/dsp-tools/issues/719)) ([ff0e4fe](https://github.com/dasch-swiss/dsp-tools/commit/ff0e4fe2cf0171d08b0d513d5fc0df7feeca3d08))
* **ci:** set up merge queue ([#717](https://github.com/dasch-swiss/dsp-tools/issues/717)) ([1c13f5f](https://github.com/dasch-swiss/dsp-tools/commit/1c13f5fd6af6b2b49721a4a1ee27e1d26e1c0787))
* **connection:** content type doesn't have to be parametrized ([#752](https://github.com/dasch-swiss/dsp-tools/issues/752)) ([2c0febb](https://github.com/dasch-swiss/dsp-tools/commit/2c0febb8eb7ce1fadfe651842ee31c0fe7f4634f))
* **create:** in normal workflow, don't rely on failing request (DEV-3220) ([#757](https://github.com/dasch-swiss/dsp-tools/issues/757)) ([f9b9677](https://github.com/dasch-swiss/dsp-tools/commit/f9b967742fe19c1993e9a88cd5fa5e40a13163a8))
* define poetry exec targets for all tools ([#695](https://github.com/dasch-swiss/dsp-tools/issues/695)) ([c04356b](https://github.com/dasch-swiss/dsp-tools/commit/c04356bcc75866f3251ec9ad279108687426f065))
* delete dead code in project context ([#770](https://github.com/dasch-swiss/dsp-tools/issues/770)) ([5159b8d](https://github.com/dasch-swiss/dsp-tools/commit/5159b8d6bad97da909078d198106ae360386b8da))
* don't log errors multiple times (DEV-3195) ([#769](https://github.com/dasch-swiss/dsp-tools/issues/769)) ([0025784](https://github.com/dasch-swiss/dsp-tools/commit/002578404025dc7e791310df5f8281b28ddab919))
* don't send chat notification on post releases / release only on "feat" or "fix" (DEV-3148) ([#707](https://github.com/dasch-swiss/dsp-tools/issues/707)) ([fd9b148](https://github.com/dasch-swiss/dsp-tools/commit/fd9b148b6df7f7ad29ab11e51c7ab7d8fab545be))
* **excel2json-properties:** reorganise file ([#776](https://github.com/dasch-swiss/dsp-tools/issues/776)) ([4b8c060](https://github.com/dasch-swiss/dsp-tools/commit/4b8c060cec4c2bcac79475a51d5889ce430a895e))
* fix pypi.org publishing ([#708](https://github.com/dasch-swiss/dsp-tools/issues/708)) ([ea56066](https://github.com/dasch-swiss/dsp-tools/commit/ea560669759a4e57c14b0888eb983ad25c2d6848))
* fix ruff PLR5501 ([#774](https://github.com/dasch-swiss/dsp-tools/issues/774)) ([1f88112](https://github.com/dasch-swiss/dsp-tools/commit/1f881126a391569cf378aecab84bc84c29ffa54f))
* get rid of dead code ([#751](https://github.com/dasch-swiss/dsp-tools/issues/751)) ([f67eac2](https://github.com/dasch-swiss/dsp-tools/commit/f67eac204791e9af18dcc4dcd22aa4428f5aa1b1))
* get rid of http_call_with_retry ([#694](https://github.com/dasch-swiss/dsp-tools/issues/694)) ([70f6808](https://github.com/dasch-swiss/dsp-tools/commit/70f680843efd9c9398d869b83f46d0e0eea0fb83))
* get rid of shared.login() function ([#714](https://github.com/dasch-swiss/dsp-tools/issues/714)) ([28806a0](https://github.com/dasch-swiss/dsp-tools/commit/28806a06ff9a370504e124c647531dd105fec6cc))
* hide stack trace from user (DEV-3158) ([#724](https://github.com/dasch-swiss/dsp-tools/issues/724)) ([808c01c](https://github.com/dasch-swiss/dsp-tools/commit/808c01ca5cfd417a7228a2220140d4e560cdf1b6))
* improve package structure of unittests/cli ([#713](https://github.com/dasch-swiss/dsp-tools/issues/713)) ([111c6df](https://github.com/dasch-swiss/dsp-tools/commit/111c6df426824781fd316e5a3dbd28fb48e570d1))
* improve performance with requests.Session object (DEV-3174) ([#739](https://github.com/dasch-swiss/dsp-tools/issues/739)) ([43caaf9](https://github.com/dasch-swiss/dsp-tools/commit/43caaf9db3a8d445f1b0b741540d51e8dffb4b09))
* log all HTTP requests, get rid of --dump flag (DEV-3171) ([#731](https://github.com/dasch-swiss/dsp-tools/issues/731)) ([e2b0598](https://github.com/dasch-swiss/dsp-tools/commit/e2b0598386868500c12bcb8a42a054494522e45b))
* log all requests, also during retry (DEV-3213) ([#759](https://github.com/dasch-swiss/dsp-tools/issues/759)) ([fd05080](https://github.com/dasch-swiss/dsp-tools/commit/fd05080eb0010f6e6612a605f5e78d75a552f0c1))
* make dev-release to pypi.org on every commit to main (DEV-3130) ([#699](https://github.com/dasch-swiss/dsp-tools/issues/699)) ([b05690b](https://github.com/dasch-swiss/dsp-tools/commit/b05690bce18e2b53edeef4e5170655065f876c27))
* make post releases instead of dev releases (DEV-3130) ([#705](https://github.com/dasch-swiss/dsp-tools/issues/705)) ([94b289d](https://github.com/dasch-swiss/dsp-tools/commit/94b289d25e994755390675196d1193ca8c4fe3e1))
* make XmlUploadError a subclass of BaseError ([#746](https://github.com/dasch-swiss/dsp-tools/issues/746)) ([12e406f](https://github.com/dasch-swiss/dsp-tools/commit/12e406f48af060df26525029f87d9952de6e231f))
* move session renewal into own method ([#755](https://github.com/dasch-swiss/dsp-tools/issues/755)) ([7adc837](https://github.com/dasch-swiss/dsp-tools/commit/7adc837cb18aa44379bd510b2f48bc26984e3095))
* move to Python 3.12 ([#696](https://github.com/dasch-swiss/dsp-tools/issues/696)) ([60f64a2](https://github.com/dasch-swiss/dsp-tools/commit/60f64a2c9c14fe9197bb083dc117234a07779f51))
* **project_validate:** fix one ruff PLR0912 ([#775](https://github.com/dasch-swiss/dsp-tools/issues/775)) ([d7060d6](https://github.com/dasch-swiss/dsp-tools/commit/d7060d6314df2fc9bac11a74e60b607ae2fe02b1))
* **project-create:** clean up one ruff PLR0912 and one PLR0913 ([#772](https://github.com/dasch-swiss/dsp-tools/issues/772)) ([7902840](https://github.com/dasch-swiss/dsp-tools/commit/790284053427dcb3b6689d0036c19a69fc4edcd5))
* **project-get:** fix ruff PLR0915 ([#773](https://github.com/dasch-swiss/dsp-tools/issues/773)) ([71b9b2a](https://github.com/dasch-swiss/dsp-tools/commit/71b9b2acb1feb8e94aa80203627d3b8db6e0cf75))
* PyPI authentication via API token (DEV-3143) ([#703](https://github.com/dasch-swiss/dsp-tools/issues/703)) ([dd16ef4](https://github.com/dasch-swiss/dsp-tools/commit/dd16ef4909849bd056f82bd39c14091927928040))
* refactor test_find_date_in_string ([#710](https://github.com/dasch-swiss/dsp-tools/issues/710)) ([630df2c](https://github.com/dasch-swiss/dsp-tools/commit/630df2c36a7e482268c5d12e5cbb470a96d97a9b))
* remove duplicated & outdated docstrings from Connection protocol ([#758](https://github.com/dasch-swiss/dsp-tools/issues/758)) ([2a04f5a](https://github.com/dasch-swiss/dsp-tools/commit/2a04f5a1b48d58c37d72777717a23c632e1e3d96))
* remove unused code (DEV-3152) ([#712](https://github.com/dasch-swiss/dsp-tools/issues/712)) ([43cba62](https://github.com/dasch-swiss/dsp-tools/commit/43cba62cb42623aaea6a86d93c19d5264ce2770b))
* replace bandit action by ruff's bandit ruleset (DEV-3026) ([#722](https://github.com/dasch-swiss/dsp-tools/issues/722)) ([76203cf](https://github.com/dasch-swiss/dsp-tools/commit/76203cf9d3da1fcd193c9203de5cec9bc13c6671))
* resolve PLR0911 in call_requested_action() ([#701](https://github.com/dasch-swiss/dsp-tools/issues/701)) ([855231e](https://github.com/dasch-swiss/dsp-tools/commit/855231e43a5b091dd1c4e0785343e7ec2330f242))
* split up models/helpers.py ([#760](https://github.com/dasch-swiss/dsp-tools/issues/760)) ([f97cce8](https://github.com/dasch-swiss/dsp-tools/commit/f97cce80be17f23df15fd9dca220b3c52f2d58cc))
* tidy up connection class ([#747](https://github.com/dasch-swiss/dsp-tools/issues/747)) ([eaa1158](https://github.com/dasch-swiss/dsp-tools/commit/eaa115802355052c046b99547baeb627aa76c3b0))
* tidy up Connection class (DEV-3191) ([#748](https://github.com/dasch-swiss/dsp-tools/issues/748)) ([bd915ef](https://github.com/dasch-swiss/dsp-tools/commit/bd915ef2691ff383e4255df580b5580da89729ac))
* tidy up exceptions ([#762](https://github.com/dasch-swiss/dsp-tools/issues/762)) ([03213ed](https://github.com/dasch-swiss/dsp-tools/commit/03213ed11ce0aa9e3d5c8f4662407de1974cdf5d))

## [5.6.0](https://github.com/dasch-swiss/dsp-tools/compare/v5.5.0...v5.6.0) (2023-12-19)


### Enhancements

* **excel2xml:** support French BC dates in find_date_in_string() (DEV-3099) ([#680](https://github.com/dasch-swiss/dsp-tools/issues/680)) ([610f064](https://github.com/dasch-swiss/dsp-tools/commit/610f064392f54aa239b0881383547db0540c2e31))


### Bug Fixes

* **excel2json:** support uppercase classes sheet in resources.xlsx (DEV-3109) ([#683](https://github.com/dasch-swiss/dsp-tools/issues/683)) ([71205f8](https://github.com/dasch-swiss/dsp-tools/commit/71205f816539dd0e19f7375924e8488f1d6a9891))
* **excel2xml:** find_date_in_string() must not return invalid date (DEV-3116) ([#688](https://github.com/dasch-swiss/dsp-tools/issues/688)) ([71b754d](https://github.com/dasch-swiss/dsp-tools/commit/71b754d506e2025544552497733a91fbde36129d))
* **xmlupload:** saving the csv file if there are more than 50 problems with the ontology names (DEV-3112) ([#685](https://github.com/dasch-swiss/dsp-tools/issues/685)) ([a7d2e59](https://github.com/dasch-swiss/dsp-tools/commit/a7d2e594d25d6cf178afbc203ed5da65ba83e4ed))


### Maintenance

* add pytest-sugar ([#692](https://github.com/dasch-swiss/dsp-tools/issues/692)) ([1d22716](https://github.com/dasch-swiss/dsp-tools/commit/1d22716346d7f47cbf81bc7a565e755aa5d9201a))
* downgrade start-stack to 2023.11.02 ([#693](https://github.com/dasch-swiss/dsp-tools/issues/693)) ([09f50ff](https://github.com/dasch-swiss/dsp-tools/commit/09f50ffa7e0f499a4ba22f8721e3df025e2748a2))
* move retry logic into the connection implementation (DEV-3110) ([#686](https://github.com/dasch-swiss/dsp-tools/issues/686)) ([f1a7051](https://github.com/dasch-swiss/dsp-tools/commit/f1a7051070006a3fa9bf156748fb5a1e993af4ad))
* replace pylint, isort, black with ruff (DEV-2972) ([#653](https://github.com/dasch-swiss/dsp-tools/issues/653)) ([2594d36](https://github.com/dasch-swiss/dsp-tools/commit/2594d369c1fee841adf44db5b71f41ea08a4a631))
* resolve Ruff warnings A003, B023, D103 and PLR0911 ([#684](https://github.com/dasch-swiss/dsp-tools/issues/684)) ([b0f598c](https://github.com/dasch-swiss/dsp-tools/commit/b0f598c72aaf3734981e0708051b4ad9ebfa3965))
* **start-stack:** adapt docs of --max_file_size flag (DEV_3093) ([#689](https://github.com/dasch-swiss/dsp-tools/issues/689)) ([af46da8](https://github.com/dasch-swiss/dsp-tools/commit/af46da8e83e6355b2e882722a4bac1d9f63deb1c))

## [5.5.0](https://github.com/dasch-swiss/dsp-tools/compare/v5.4.0...v5.5.0) (2023-12-13)


### Enhancements

* **cli:** change user output when handling errors (DEV-3067) ([#672](https://github.com/dasch-swiss/dsp-tools/issues/672)) ([71a1737](https://github.com/dasch-swiss/dsp-tools/commit/71a1737a22d74aa5d856292afd992eaa4b110fd5))
* **excel2json:** new error implementation for json validation (DEV-3047) ([#664](https://github.com/dasch-swiss/dsp-tools/issues/664)) ([fdbc545](https://github.com/dasch-swiss/dsp-tools/commit/fdbc5450dc08b99006c5add09bfde186d5f26de1))
* **excel2json:** new user error (InputError) implementation in properties section (DEV-3037) ([#654](https://github.com/dasch-swiss/dsp-tools/issues/654)) ([b1703e1](https://github.com/dasch-swiss/dsp-tools/commit/b1703e12f4cf9919b9f8ce2efa53db86dae6c83f))
* **xmlupload:** improve error message if ontology is unknown (DEV-3024) ([#674](https://github.com/dasch-swiss/dsp-tools/issues/674)) ([5319ff3](https://github.com/dasch-swiss/dsp-tools/commit/5319ff3217969e86ac78ce3924b31fdf119e9f23))


### Bug Fixes

* date validation forbids legal values (DEV-3059) ([#668](https://github.com/dasch-swiss/dsp-tools/issues/668)) ([13131ff](https://github.com/dasch-swiss/dsp-tools/commit/13131ffebf8a99d4d10d5e0aeb5526f0547afd5f))
* **excel2json:** find hidden worksheets in excel (DEV-1483) ([#679](https://github.com/dasch-swiss/dsp-tools/issues/679)) ([ffbf0c0](https://github.com/dasch-swiss/dsp-tools/commit/ffbf0c079909b0c150f0e1a39efb256f6781a314))
* **xmlupload:** allow dots in filenames (DEV-3058) ([#676](https://github.com/dasch-swiss/dsp-tools/issues/676)) ([ad0c37c](https://github.com/dasch-swiss/dsp-tools/commit/ad0c37cc5feb030f538db3787d0b532be2694577))
* **xmlupload:** allow external link in text value (DEV-3054) ([#666](https://github.com/dasch-swiss/dsp-tools/issues/666)) ([08f7b93](https://github.com/dasch-swiss/dsp-tools/commit/08f7b9309c6b116d490ed18c81c0bbfc7f94aa5a))
* **xmlupload:** support uppercase file extensions (DEV-3095) ([#678](https://github.com/dasch-swiss/dsp-tools/issues/678)) ([24cb320](https://github.com/dasch-swiss/dsp-tools/commit/24cb320125016ecaff85387a11f7ca0dd53c5a85))


### Maintenance

* bump start-stack to 2023.12.01 (DEV-3105) ([#681](https://github.com/dasch-swiss/dsp-tools/issues/681)) ([ddd0078](https://github.com/dasch-swiss/dsp-tools/commit/ddd00782656cf2edac70204d69938423b1c644bf))
* **cli:** modularise cli.py (DEV-3068) ([#673](https://github.com/dasch-swiss/dsp-tools/issues/673)) ([f0da1ca](https://github.com/dasch-swiss/dsp-tools/commit/f0da1cad5d26ebf747e185542b4ada108f9bd54f))
* **deps:** bump the all-dependencies group with 8 updates ([#662](https://github.com/dasch-swiss/dsp-tools/issues/662)) ([6e307c2](https://github.com/dasch-swiss/dsp-tools/commit/6e307c2465f7ff8a82febf737ea92f3bab0b2549))
* **docs:** fix outdated link ([#669](https://github.com/dasch-swiss/dsp-tools/issues/669)) ([5b333c2](https://github.com/dasch-swiss/dsp-tools/commit/5b333c274267a9e1abbd6b11de5c20898e931024))
* **excel2json:** modularise unittests (DEV-3040) ([#659](https://github.com/dasch-swiss/dsp-tools/issues/659)) ([107b1b0](https://github.com/dasch-swiss/dsp-tools/commit/107b1b0bcbbe94dfa61a74ff6c17ec3888f0b4d2))
* **excel2json:** new excel reader (DEV-3049) ([#665](https://github.com/dasch-swiss/dsp-tools/issues/665)) ([a0d5776](https://github.com/dasch-swiss/dsp-tools/commit/a0d57769be9d8b0073536d5db29deb5cea05ce61))
* pandas future warning in unittest (DEV-3060) ([#671](https://github.com/dasch-swiss/dsp-tools/issues/671)) ([b3f75f4](https://github.com/dasch-swiss/dsp-tools/commit/b3f75f410afe1c2df5dd868a112736cb2ee40213))
* **process-files:** diverse improvements ([#656](https://github.com/dasch-swiss/dsp-tools/issues/656)) ([692ad40](https://github.com/dasch-swiss/dsp-tools/commit/692ad4092fe459d47ea015ad529de7e13f5a7066))
* remove tabs (DEV-3043) ([#661](https://github.com/dasch-swiss/dsp-tools/issues/661)) ([286abf8](https://github.com/dasch-swiss/dsp-tools/commit/286abf8c21aca9901dde2ac858f00e3c45be881a))
* update poetry.lock (DEV-3081) ([#675](https://github.com/dasch-swiss/dsp-tools/issues/675)) ([cd85836](https://github.com/dasch-swiss/dsp-tools/commit/cd85836d20479a5dc82d355434a076ec087e4010))
* **xmlupload:** clean up handle media information (DEV-3086) ([#677](https://github.com/dasch-swiss/dsp-tools/issues/677)) ([93fb71f](https://github.com/dasch-swiss/dsp-tools/commit/93fb71f7e31fcfe930ddbc0b47a924015af4a719))

## [5.4.0](https://github.com/dasch-swiss/dsp-tools/compare/v5.3.0...v5.4.0) (2023-11-29)


### Enhancements

* **xmlupload:** check consistency with ontology on server (DEV-2921) ([#630](https://github.com/dasch-swiss/dsp-tools/issues/630)) ([a563c07](https://github.com/dasch-swiss/dsp-tools/commit/a563c07a8350dba611f92ab22f894fca67c10a72))

## [5.3.0](https://github.com/dasch-swiss/dsp-tools/compare/v5.2.0...v5.3.0) (2023-11-29)


### Enhancements

* **excel2xml:** add support for 3-digit-years in find_date_in_string() (DEV-3005) ([#652](https://github.com/dasch-swiss/dsp-tools/issues/652)) ([1afee03](https://github.com/dasch-swiss/dsp-tools/commit/1afee03abc2a979eed26fb5adf2fa84387994d40))


### Bug Fixes

* **process-files:** fix resource leak, try omitting restart of python (DEV-2986) ([#651](https://github.com/dasch-swiss/dsp-tools/issues/651)) ([7347be7](https://github.com/dasch-swiss/dsp-tools/commit/7347be7a27f72d325424a57d6bfb8fdd8508eccc))
* **upload-files:** use a new ThreadPoolExecutor for every batch (DEV-2973) ([#650](https://github.com/dasch-swiss/dsp-tools/issues/650)) ([431a755](https://github.com/dasch-swiss/dsp-tools/commit/431a755870bb4e347a30f234d4461ad0b319aed3))


### Maintenance

* add sourcery workflow to CI checks ([#646](https://github.com/dasch-swiss/dsp-tools/issues/646)) ([8b445f2](https://github.com/dasch-swiss/dsp-tools/commit/8b445f257870f3b406a13111fcb9bc920b5933e2))
* apply sourcery suggestions ([#644](https://github.com/dasch-swiss/dsp-tools/issues/644)) ([96110a0](https://github.com/dasch-swiss/dsp-tools/commit/96110a0ad3c94c4bce30e261ac3b544492c43f87))
* bump start-stack to 2023.11.02 ([#657](https://github.com/dasch-swiss/dsp-tools/issues/657)) ([c399dee](https://github.com/dasch-swiss/dsp-tools/commit/c399deef52ff00f344c6f67f93b59cf9f3b171da))
* **excel2json:** modularise functions (DEV-3025) ([#655](https://github.com/dasch-swiss/dsp-tools/issues/655)) ([5486b15](https://github.com/dasch-swiss/dsp-tools/commit/5486b15f810a15d1bfd825f3c6798da7cec23466))
* more sourcery refactorings ([#647](https://github.com/dasch-swiss/dsp-tools/issues/647)) ([300bfa0](https://github.com/dasch-swiss/dsp-tools/commit/300bfa04e6a969791c4b59d89c4398f459630adc))
* refactor import-scripts ([#649](https://github.com/dasch-swiss/dsp-tools/issues/649)) ([9272898](https://github.com/dasch-swiss/dsp-tools/commit/9272898613b15665b4ebb7863fe64821de719618))
* remove unnecessary pylint ignore comments ([#645](https://github.com/dasch-swiss/dsp-tools/issues/645)) ([d314121](https://github.com/dasch-swiss/dsp-tools/commit/d314121f708ce77b0f2d2e20a19b3bbd5d9e3111))
* replace os.path and os.scandir with pathlib.Path ([#648](https://github.com/dasch-swiss/dsp-tools/issues/648)) ([e325237](https://github.com/dasch-swiss/dsp-tools/commit/e32523710269de13b591a0243cee811eee2523d3))
* use iri util consistently (DEV-2951) ([#642](https://github.com/dasch-swiss/dsp-tools/issues/642)) ([911cfa5](https://github.com/dasch-swiss/dsp-tools/commit/911cfa5ef55b114c41809f3640190b5270961fa3))

## [5.2.0](https://github.com/dasch-swiss/dsp-tools/compare/v5.1.0...v5.2.0) (2023-11-15)


### Enhancements

* **xmlupload:** add check if links point to valid resource ID (DEV-2902) ([#639](https://github.com/dasch-swiss/dsp-tools/issues/639)) ([803c9f6](https://github.com/dasch-swiss/dsp-tools/commit/803c9f68a27cac686f935d2ff2993144bfca905b))
* **xmlupload:** id2iri mapping contains servername (DEV-1889) ([#628](https://github.com/dasch-swiss/dsp-tools/issues/628)) ([19a3f29](https://github.com/dasch-swiss/dsp-tools/commit/19a3f29b91c5491843b309bfa9a9e7f50031b8f2))


### Bug Fixes

* retain value permissions if a link gets stashed because of circular dependencies (DEV-1489) ([#623](https://github.com/dasch-swiss/dsp-tools/issues/623)) ([3ccb75b](https://github.com/dasch-swiss/dsp-tools/commit/3ccb75b06cef51ba930d8159ad763fc1bc0769c9))
* **upload-files:** handle JSONDecodeError (DEV-2907) ([#621](https://github.com/dasch-swiss/dsp-tools/issues/621)) ([40000a8](https://github.com/dasch-swiss/dsp-tools/commit/40000a85e97d321928a3da1793b2e68d386000fd))
* **upload-files:** prevent crash (DEV-2918) ([#626](https://github.com/dasch-swiss/dsp-tools/issues/626)) ([19d179e](https://github.com/dasch-swiss/dsp-tools/commit/19d179ea0781ca00d96ec8ebea6d3c666bee301a))
* **xmlupload:** fix non-initialized variable (DEV-2922) ([#629](https://github.com/dasch-swiss/dsp-tools/issues/629)) ([afb16b1](https://github.com/dasch-swiss/dsp-tools/commit/afb16b1a4208398dd734f93098f8d47f0be32b76))
* **xmlupload:** print reason of failure if resource cannot be created (DEV-2925) ([#637](https://github.com/dasch-swiss/dsp-tools/issues/637)) ([e3a194a](https://github.com/dasch-swiss/dsp-tools/commit/e3a194a0c2849fcedb9b893dcd47ca2b31ce61ac))


### Maintenance

* add clean script to remove unnecessary files ([#631](https://github.com/dasch-swiss/dsp-tools/issues/631)) ([7f98045](https://github.com/dasch-swiss/dsp-tools/commit/7f9804543781287d9c2fe1e5b68318df341ca6e7))
* add more logs and timestamps ([#627](https://github.com/dasch-swiss/dsp-tools/issues/627)) ([21ed1d8](https://github.com/dasch-swiss/dsp-tools/commit/21ed1d8535e81f4dce12627f0f5d1b97724b9fd4))
* bump start-stack (apply DSP-APP fix) ([#641](https://github.com/dasch-swiss/dsp-tools/issues/641)) ([f901399](https://github.com/dasch-swiss/dsp-tools/commit/f901399ab6b19e52c1a9f141706951df0153351e))
* bump start-stack to 2023.11.01 ([#633](https://github.com/dasch-swiss/dsp-tools/issues/633)) ([81daf2a](https://github.com/dasch-swiss/dsp-tools/commit/81daf2afa11020d8c8f160eea174fb07585d089d))
* **excel2xml:** suppress irrelevant warnings, turn non-fatal errors into warnings (DEV-2917) ([#625](https://github.com/dasch-swiss/dsp-tools/issues/625)) ([b6943a2](https://github.com/dasch-swiss/dsp-tools/commit/b6943a2c426944850237a42b71e306d56692f105))
* remove unused code (DEV-2950) ([#638](https://github.com/dasch-swiss/dsp-tools/issues/638)) ([fbbafec](https://github.com/dasch-swiss/dsp-tools/commit/fbbafece69501c07f5e264456f03ac1c389e0f05))
* reorganize excel2xml ([#635](https://github.com/dasch-swiss/dsp-tools/issues/635)) ([6773513](https://github.com/dasch-swiss/dsp-tools/commit/67735134ef53ebacdee30684562543b2f2a046cf))
* reorganize excel2xml unit tests ([#636](https://github.com/dasch-swiss/dsp-tools/issues/636)) ([d015f9f](https://github.com/dasch-swiss/dsp-tools/commit/d015f9fbbce1a19b441afd496204015e732a55ea))
* replace resource instance factory (DEV-2876) ([#594](https://github.com/dasch-swiss/dsp-tools/issues/594)) ([906a211](https://github.com/dasch-swiss/dsp-tools/commit/906a2116cbe54759f9619e537994d418fc420b34))
* restructure repository ([#632](https://github.com/dasch-swiss/dsp-tools/issues/632)) ([8a05b2c](https://github.com/dasch-swiss/dsp-tools/commit/8a05b2ccd052260853a8f0344451e7175ddfab37))
* restructure stash-related files ([#640](https://github.com/dasch-swiss/dsp-tools/issues/640)) ([a49fa59](https://github.com/dasch-swiss/dsp-tools/commit/a49fa59cb1b8ab269b4be77cb74fc5986b8ed6be))
* **upload-files:** thread-safe logging of bullet point lists ([#619](https://github.com/dasch-swiss/dsp-tools/issues/619)) ([37040a6](https://github.com/dasch-swiss/dsp-tools/commit/37040a694ef65d113dbb4a1d62c0f18e6a174a27))


### Documentation

* replace admin.dasch.swiss by app.dasch.swiss ([#634](https://github.com/dasch-swiss/dsp-tools/issues/634)) ([ae06161](https://github.com/dasch-swiss/dsp-tools/commit/ae0616166fae7622477bd02bc5d47e8f927b7583))

## [5.1.0](https://github.com/dasch-swiss/dsp-tools/compare/v5.0.3...v5.1.0) (2023-11-01)


### Enhancements

* **xmlupload:** reduce stash size of circular references (DEV-2848) ([#599](https://github.com/dasch-swiss/dsp-tools/issues/599)) ([228b1f7](https://github.com/dasch-swiss/dsp-tools/commit/228b1f7488ee61307dc9e9c730f096c44508555e))


### Bug Fixes

* don't create logging handler multiple times (DEV-2891) ([#609](https://github.com/dasch-swiss/dsp-tools/issues/609)) ([e6aa47c](https://github.com/dasch-swiss/dsp-tools/commit/e6aa47cfeb70136a1e5107bf49490168a13d5b96))
* ignore IRIs in stashing algorithm (DEV-2885) ([#603](https://github.com/dasch-swiss/dsp-tools/issues/603)) ([635bc5c](https://github.com/dasch-swiss/dsp-tools/commit/635bc5cf3ce5651b5ee0a80734dfc9d33548cd81))
* IRI regex used in multiple places is incorrect (DEV-2888) ([#606](https://github.com/dasch-swiss/dsp-tools/issues/606)) ([096f47e](https://github.com/dasch-swiss/dsp-tools/commit/096f47e9c1e525be750a9d57c5c087c360cc0205))
* prevent endless waiting for response, without creating resources multiple times (DEV-2860) ([#586](https://github.com/dasch-swiss/dsp-tools/issues/586)) ([caa16b7](https://github.com/dasch-swiss/dsp-tools/commit/caa16b7126c63acc82d68932b6693a431042d986))


### Maintenance

* add a client for project related API requests (DEV-2890) ([#610](https://github.com/dasch-swiss/dsp-tools/issues/610)) ([e100b26](https://github.com/dasch-swiss/dsp-tools/commit/e100b26e74a6691b82b8f84bfbbef43ff5eee846))
* add logging to stashing algorithm (DEV-2881) ([#608](https://github.com/dasch-swiss/dsp-tools/issues/608)) ([736f02b](https://github.com/dasch-swiss/dsp-tools/commit/736f02bc6152f4e3aee73867a8d2c4e2d4e7dc48))
* add specific model for bitstream information (DEV-2893) ([#613](https://github.com/dasch-swiss/dsp-tools/issues/613)) ([8d0d61d](https://github.com/dasch-swiss/dsp-tools/commit/8d0d61da83ead342c49af3730341bb22df7a63d4))
* bump start-stack to 2023.10.03 ([#616](https://github.com/dasch-swiss/dsp-tools/issues/616)) ([213c301](https://github.com/dasch-swiss/dsp-tools/commit/213c3017c7ae4a9b25f68520a633814d342ae110))
* **deps:** bump the all-dependencies group with 8 updates ([#617](https://github.com/dasch-swiss/dsp-tools/issues/617)) ([1a2fdd6](https://github.com/dasch-swiss/dsp-tools/commit/1a2fdd60cc7baa4b9fe876d693b7aaaf2806acb4))
* fix analyse_circles_in_data() (remove namespaces) ([#598](https://github.com/dasch-swiss/dsp-tools/issues/598)) ([72f710c](https://github.com/dasch-swiss/dsp-tools/commit/72f710c01707c0373008dcfc89f53028da50c548))
* fix logging statements ([#611](https://github.com/dasch-swiss/dsp-tools/issues/611)) ([1f95f8d](https://github.com/dasch-swiss/dsp-tools/commit/1f95f8d1b79bd5170a652c0d04e7ada417d76734))
* further refactoring of graph analysing ([#590](https://github.com/dasch-swiss/dsp-tools/issues/590)) ([d0779ac](https://github.com/dasch-swiss/dsp-tools/commit/d0779aceaaee5e611d8cbe82dceab4f31bb91070))
* improve logging for upload-files ([#614](https://github.com/dasch-swiss/dsp-tools/issues/614)) ([f99e755](https://github.com/dasch-swiss/dsp-tools/commit/f99e75537cec73a14927b26350e24cfdf5bfcd44))
* log dsp-tools version ([#612](https://github.com/dasch-swiss/dsp-tools/issues/612)) ([ab9ffef](https://github.com/dasch-swiss/dsp-tools/commit/ab9ffeff41d39357b4258f8ab4489ea925a2fdd9))
* refactor graph analysing ([#589](https://github.com/dasch-swiss/dsp-tools/issues/589)) ([14a6e83](https://github.com/dasch-swiss/dsp-tools/commit/14a6e8395a583e644d589c69acec157e50ef5468))
* split up test_rosetta.py into smaller functions ([#601](https://github.com/dasch-swiss/dsp-tools/issues/601)) ([33c9fce](https://github.com/dasch-swiss/dsp-tools/commit/33c9fce4ffc20aae9ea6e53e10f1def24cefdf4e))
* **test_construct_and_analyze_graph:** remove namespace, add semantic line breaks ([#602](https://github.com/dasch-swiss/dsp-tools/issues/602)) ([b693a94](https://github.com/dasch-swiss/dsp-tools/commit/b693a9415d4e087fc8667a397de38370708c4f8b))
* tidy up graph analyzing ([#595](https://github.com/dasch-swiss/dsp-tools/issues/595)) ([f2d4488](https://github.com/dasch-swiss/dsp-tools/commit/f2d4488a147ed5b9109cf06b2dca7d8232a696f8))
* tidy up KnoraStandoffXml class ([#597](https://github.com/dasch-swiss/dsp-tools/issues/597)) ([c430b67](https://github.com/dasch-swiss/dsp-tools/commit/c430b67b103faf8808026988f52d365dde040d74))


### Documentation

* fix broken links ([#604](https://github.com/dasch-swiss/dsp-tools/issues/604)) ([7c19894](https://github.com/dasch-swiss/dsp-tools/commit/7c198940d1b9fce897f6f07f39c5e749937744a8))
* fix typos in docs ([#615](https://github.com/dasch-swiss/dsp-tools/issues/615)) ([a7ecd47](https://github.com/dasch-swiss/dsp-tools/commit/a7ecd47156b62edc07270c04574bcf105941e2d3))

## [5.0.3](https://github.com/dasch-swiss/dsp-tools/compare/v5.0.2...v5.0.3) (2023-10-20)


### Bug Fixes

* **xmlupload:** misleading warning when uploading stashed XML texts (DEV-2793) ([#559](https://github.com/dasch-swiss/dsp-tools/issues/559)) ([1e2c8f2](https://github.com/dasch-swiss/dsp-tools/commit/1e2c8f265ad1942d170ad43fb9c344361848a7f0))


### Maintenance

* bump dependencies ([#578](https://github.com/dasch-swiss/dsp-tools/issues/578)) ([6d9f082](https://github.com/dasch-swiss/dsp-tools/commit/6d9f082d281da529720fc6473e8b7c317915fe6f))
* bump start-stack to 2023.10.02 ([#584](https://github.com/dasch-swiss/dsp-tools/issues/584)) ([37ca185](https://github.com/dasch-swiss/dsp-tools/commit/37ca185b1e2c3943d9586c75466d8da402e324de))
* bump start-stack to 2023.10.02 (DEV-2823) ([#571](https://github.com/dasch-swiss/dsp-tools/issues/571)) ([863c631](https://github.com/dasch-swiss/dsp-tools/commit/863c63179f804eecedc1d3dba8c7b90c6ce4db8f))
* **CI:** split up test action into several jobs ([#553](https://github.com/dasch-swiss/dsp-tools/issues/553)) ([cfb5042](https://github.com/dasch-swiss/dsp-tools/commit/cfb5042ef0a4e96045ac5ce5c8b63542b876732c))
* clarify isort and pre-commit in readme (DEV-2781) ([#549](https://github.com/dasch-swiss/dsp-tools/issues/549)) ([e58fec1](https://github.com/dasch-swiss/dsp-tools/commit/e58fec136b0c63ea084cfca386ed01c7337f280c))
* create composite setup action and allow more PR titles ([#550](https://github.com/dasch-swiss/dsp-tools/issues/550)) ([2084999](https://github.com/dasch-swiss/dsp-tools/commit/2084999c68a4d230cbd09fcac303715f165aebba))
* create JSON-LD context without API request (DEV-2845) ([#581](https://github.com/dasch-swiss/dsp-tools/issues/581)) ([dcc655d](https://github.com/dasch-swiss/dsp-tools/commit/dcc655df92033449e415f077c98b5f20f6e2230c))
* create specific objects for stash information (DEV-2787) ([#557](https://github.com/dasch-swiss/dsp-tools/issues/557)) ([b38c2d3](https://github.com/dasch-swiss/dsp-tools/commit/b38c2d3320b699b8372d488a58149a90a62bde11))
* **deps:** bump urllib3 from 2.0.6 to 2.0.7 ([#575](https://github.com/dasch-swiss/dsp-tools/issues/575)) ([a41b174](https://github.com/dasch-swiss/dsp-tools/commit/a41b174fac879058c4af4715f551f645cf4384bb))
* identify temporary text values with UUID instead of text hash (DEV-2790) ([#558](https://github.com/dasch-swiss/dsp-tools/issues/558)) ([08624b2](https://github.com/dasch-swiss/dsp-tools/commit/08624b2bdf0acd4f1cd2f126e2f5511f4b633d15))
* integrate DSP-INGEST in start-stack ([#566](https://github.com/dasch-swiss/dsp-tools/issues/566)) ([e8fb38b](https://github.com/dasch-swiss/dsp-tools/commit/e8fb38bc50284317d6561aef35212aec923f1368))
* introduce abstraction layer for connection (DEV-2820) ([#570](https://github.com/dasch-swiss/dsp-tools/issues/570)) ([87c1e18](https://github.com/dasch-swiss/dsp-tools/commit/87c1e18a9a9e838dc21aaa5ed0d91af5cbcb33df))
* modularize xmlupload (DEV-2813) ([#568](https://github.com/dasch-swiss/dsp-tools/issues/568)) ([8026fcb](https://github.com/dasch-swiss/dsp-tools/commit/8026fcbe7b28335beb562564c30e4e7184d8678f))
* modularize xmlupload method (DEV-2836) ([#574](https://github.com/dasch-swiss/dsp-tools/issues/574)) ([b9588c3](https://github.com/dasch-swiss/dsp-tools/commit/b9588c3436514cc2490c7cfde4ee06f83b64f9b4))
* remove leftovers of old --metrics flag ([#583](https://github.com/dasch-swiss/dsp-tools/issues/583)) ([3234318](https://github.com/dasch-swiss/dsp-tools/commit/3234318869780cb385e4d14a9eb71306ab7c7cb2))
* remove use of XMLResource in stash models (DEV-2843) ([#577](https://github.com/dasch-swiss/dsp-tools/issues/577)) ([05dc486](https://github.com/dasch-swiss/dsp-tools/commit/05dc48695039c4f460c4a236efde9ed5c87905a1))
* **start-stack:** downgrade DSP-APP ([#576](https://github.com/dasch-swiss/dsp-tools/issues/576)) ([8c109e4](https://github.com/dasch-swiss/dsp-tools/commit/8c109e4a65b7bb85c8b1c692c5d6bac5e024b109))
* use sets instead of lists for stashing circular references (DEV-2771) ([#548](https://github.com/dasch-swiss/dsp-tools/issues/548)) ([68605bd](https://github.com/dasch-swiss/dsp-tools/commit/68605bd8859e73732c41742f15ab620ad73efa7b))
* **xmlupload:** optimize stash links (DEV-2847) ([#573](https://github.com/dasch-swiss/dsp-tools/issues/573)) ([1d20fad](https://github.com/dasch-swiss/dsp-tools/commit/1d20fad9acbe918c46656e99c5309633a64359a3))
* **xmlupload:** split up get resources and permissions function (DEV-2796) ([#560](https://github.com/dasch-swiss/dsp-tools/issues/560)) ([02eff6b](https://github.com/dasch-swiss/dsp-tools/commit/02eff6bf69378e587ddb497635b77bd9a58cc64e))


### Documentation

* **xmlupload:** day-precision dates should be written with end date (DEV-2802) ([#564](https://github.com/dasch-swiss/dsp-tools/issues/564)) ([c69af60](https://github.com/dasch-swiss/dsp-tools/commit/c69af6007c4f5edfe184ae544b4c2c39ff63f8d3))

## [5.0.2](https://github.com/dasch-swiss/dsp-tools/compare/v5.0.1...v5.0.2) (2023-10-05)


### Bug Fixes

* **fast-xmlupload:** CLI-command in documentation has outdated information (DEV-2779) ([#545](https://github.com/dasch-swiss/dsp-tools/issues/545)) ([334ea49](https://github.com/dasch-swiss/dsp-tools/commit/334ea4959c31188c9035892330147ebd3184ac41))
* ModuleNotFoundError when importing logging due to identical file name (DEV-2708) ([#530](https://github.com/dasch-swiss/dsp-tools/issues/530)) ([d2c6ec8](https://github.com/dasch-swiss/dsp-tools/commit/d2c6ec830e93cbdf6bc162112fabe2b027701797))
* **xmlupload:** fix performance slowdown during stash applying (DEV-2717) ([#533](https://github.com/dasch-swiss/dsp-tools/issues/533)) ([add40b2](https://github.com/dasch-swiss/dsp-tools/commit/add40b231eb9ded285cd19ef3c74e55a25949219))


### Maintenance

* add isort check in pre-commit and GitHub CI (DEV-2707) ([#529](https://github.com/dasch-swiss/dsp-tools/issues/529)) ([89ef086](https://github.com/dasch-swiss/dsp-tools/commit/89ef086ddc83943a9058ff8611d42f7a742f7d2e))
* add logging statements to "create" command (DEV-2776) ([#544](https://github.com/dasch-swiss/dsp-tools/issues/544)) ([73183c4](https://github.com/dasch-swiss/dsp-tools/commit/73183c46a2e17a9e728ca68563db3e27d827ac10))
* bump start-stack to 2023.10.01 (DEV-2748) ([#546](https://github.com/dasch-swiss/dsp-tools/issues/546)) ([3240d5d](https://github.com/dasch-swiss/dsp-tools/commit/3240d5dc289d62b31a15170d925650771cff6798))
* **deps:** bump dependencies ([#535](https://github.com/dasch-swiss/dsp-tools/issues/535)) ([bf93bc8](https://github.com/dasch-swiss/dsp-tools/commit/bf93bc884926983781ee6633d72b27466ac7bb0c))
* **deps:** bump dependencies ([#537](https://github.com/dasch-swiss/dsp-tools/issues/537)) ([cbcd2f3](https://github.com/dasch-swiss/dsp-tools/commit/cbcd2f3503aae7b23ec4fa05f54745fa93627cc4))
* harmonize timestamps between terminal output and log file (DEV-2716) ([#534](https://github.com/dasch-swiss/dsp-tools/issues/534)) ([9160eea](https://github.com/dasch-swiss/dsp-tools/commit/9160eea87f241d485cd0aee1fa92a8bce548d117))
* remove unnecessary PR template (DEV-2691) ([#525](https://github.com/dasch-swiss/dsp-tools/issues/525)) ([e2c41ec](https://github.com/dasch-swiss/dsp-tools/commit/e2c41ec3bbf9485368931156e372dfd4b5a0214b))
* use faster black in pre-commit hook (DEV-2736) ([#536](https://github.com/dasch-swiss/dsp-tools/issues/536)) ([ad00e4b](https://github.com/dasch-swiss/dsp-tools/commit/ad00e4bf6c51880ed0f18a34384988f2540022f2))
* **xmlupload:** _upload_stashed_xml_texts (DEV-2710) ([#532](https://github.com/dasch-swiss/dsp-tools/issues/532)) ([9d2dd35](https://github.com/dasch-swiss/dsp-tools/commit/9d2dd35cd3d7af562da3bd7190a65bcb037f836c))
* **xmlupload:** create new directory and move scripts (DEV-2715) ([#538](https://github.com/dasch-swiss/dsp-tools/issues/538)) ([6bad8d0](https://github.com/dasch-swiss/dsp-tools/commit/6bad8d0ab937096817e01fe12f96c3b9eee79d0e))
* **xmlupload:** file upload_stashed_resptr_props.py (DEV-2774) ([#542](https://github.com/dasch-swiss/dsp-tools/issues/542)) ([422bbb3](https://github.com/dasch-swiss/dsp-tools/commit/422bbb39da9e5200994eba4567ec0d830a0a802b))
* **xmlupload:** file xmlupload.py (DEV-2775) ([#543](https://github.com/dasch-swiss/dsp-tools/issues/543)) ([16fefae](https://github.com/dasch-swiss/dsp-tools/commit/16fefae3e20231dbe2484e908e084688b195c893))
* **xmlupload:** modularise individual functions in file read_validate_xml_file.py (DEV-2767) ([#541](https://github.com/dasch-swiss/dsp-tools/issues/541)) ([dc5c5a7](https://github.com/dasch-swiss/dsp-tools/commit/dc5c5a721f3ea713b661170b08207be238ff24d8))


### Documentation

* **xmlupload:** invalid example: properties must be unique (DEV-2711) ([#531](https://github.com/dasch-swiss/dsp-tools/issues/531)) ([5f9060f](https://github.com/dasch-swiss/dsp-tools/commit/5f9060f612182eff42879adbd881d015dd74444c))

## [5.0.1](https://github.com/dasch-swiss/dsp-tools/compare/v5.0.0...v5.0.1) (2023-09-20)


### Bug Fixes

* **excel2json:** correct row number in error message (DEV-2650) ([#513](https://github.com/dasch-swiss/dsp-tools/issues/513)) ([03a59ee](https://github.com/dasch-swiss/dsp-tools/commit/03a59ee23e7dc66cdb7419bd8e05438a4ac2deb7))
* **excel2json:** don't crash if optional columns are deleted in "properties" Excel file (DEV-2652) ([#518](https://github.com/dasch-swiss/dsp-tools/issues/518)) ([09c3940](https://github.com/dasch-swiss/dsp-tools/commit/09c39402bc02e4959852e318bb01fd6a2d3458a9))
* id2iri mapping is written with a question mark after the file extension (DEV-2670) [#522](https://github.com/dasch-swiss/dsp-tools/issues/522) ([3fc1bb9](https://github.com/dasch-swiss/dsp-tools/commit/3fc1bb942adccc08374e24fc90ef50601f237f66))
* no-op test that doesn't test anything (DEV-2655) ([#517](https://github.com/dasch-swiss/dsp-tools/issues/517)) ([76f1db2](https://github.com/dasch-swiss/dsp-tools/commit/76f1db263fe6121e5e76b8a40ef978163224b266))
* **upload-files:** close file handle before handling error (DEV-2666) [#519](https://github.com/dasch-swiss/dsp-tools/issues/519) ([439a139](https://github.com/dasch-swiss/dsp-tools/commit/439a1399fa2eff0c403b055f674a30cac9bbc157))


### Maintenance

* bump start-stack to 2023.09.02 (DEV-2690) ([#524](https://github.com/dasch-swiss/dsp-tools/issues/524)) ([6f5b935](https://github.com/dasch-swiss/dsp-tools/commit/6f5b935e70cd48a5ab3010ca7a553c9d8e7cf00b))
* documenation cleaning (DEV-2602) ([#503](https://github.com/dasch-swiss/dsp-tools/issues/503)) ([52485c0](https://github.com/dasch-swiss/dsp-tools/commit/52485c0a01e67eb9618554a8e52c41fd03c79a18))
* **excel2json:** replace BaseError with UserError (DEV-2671) ([#523](https://github.com/dasch-swiss/dsp-tools/issues/523)) ([eaf8dd6](https://github.com/dasch-swiss/dsp-tools/commit/eaf8dd6f967ac83db365001d9af13719f2cdd2d3))
* **excel2json:** replace excel reader in excel2resources (DEV-2668) ([#520](https://github.com/dasch-swiss/dsp-tools/issues/520)) ([f2f0d4e](https://github.com/dasch-swiss/dsp-tools/commit/f2f0d4e2b22eae4b9d3496f9bb0cd98dbe8a479f))
* fix gui_attributes notation (DEV-2651) ([#514](https://github.com/dasch-swiss/dsp-tools/issues/514)) ([8c97cc3](https://github.com/dasch-swiss/dsp-tools/commit/8c97cc34bf1a9285721e81d8709352187716dd79))
* improve PR title checking regex (DEV-2635) ([#509](https://github.com/dasch-swiss/dsp-tools/issues/509)) ([c25f3b7](https://github.com/dasch-swiss/dsp-tools/commit/c25f3b78c9fcdf7ad1de9f6f0efe8b6c2fcda2ce))
* pandas deprecated .applymap (DEV-2617) ([#510](https://github.com/dasch-swiss/dsp-tools/issues/510)) ([925b13d](https://github.com/dasch-swiss/dsp-tools/commit/925b13d4d07673220de9f657f2e7f758894ba26e))
* pandas deprecates inplace parameter (DEV-2618) ([#511](https://github.com/dasch-swiss/dsp-tools/issues/511)) ([8d6d3f7](https://github.com/dasch-swiss/dsp-tools/commit/8d6d3f7ce4cfcea51aa118794d73a5618683ed3a))
* small corrections (DEV-2653) [#515](https://github.com/dasch-swiss/dsp-tools/issues/515) ([99db5f1](https://github.com/dasch-swiss/dsp-tools/commit/99db5f1cd82e0fc1e39b73d39e5977016f84c4a1))
* **xmlupload:** split up _check_consistency_with_ontology() into smaller functions (DEV-2669) ([#521](https://github.com/dasch-swiss/dsp-tools/issues/521)) ([79a50cf](https://github.com/dasch-swiss/dsp-tools/commit/79a50cfebcd93940d512a6b1d6d3c5b7772f3046))

## [5.0.0](https://github.com/dasch-swiss/dsp-tools/compare/v4.0.0...v5.0.0) (2023-09-06)


### ⚠ BREAKING CHANGES

* **xmlupload:** allow both IDs and IRIs, remove --incremental flag (DEV-1339) ([#494](https://github.com/dasch-swiss/dsp-tools/issues/494))
* refactor id2iri: remove --outfile and --verbose flags (DEV-2576) ([#488](https://github.com/dasch-swiss/dsp-tools/issues/488))

### Enhancements

* add --dump flag to "xmlupload" and "get" commands (DEV-2534) ([#502](https://github.com/dasch-swiss/dsp-tools/issues/502)) ([d9aeba9](https://github.com/dasch-swiss/dsp-tools/commit/d9aeba9f0fabb5761aa524305ecddd2b673be3e6))
* get project without credentials (DEV-841) ([#504](https://github.com/dasch-swiss/dsp-tools/issues/504)) ([b5ea3e9](https://github.com/dasch-swiss/dsp-tools/commit/b5ea3e909971be215d8615bbb156947825ead581))
* **id2iri:** add flag to remove created resources from XML (DEV-2571) ([#491](https://github.com/dasch-swiss/dsp-tools/issues/491)) ([bf25cb7](https://github.com/dasch-swiss/dsp-tools/commit/bf25cb72c1af1e2623c8a70927c7f5d98f3e1dbb))
* **id2iri:** replace IDs also inside salsah-links, not only inside &lt;resptr&gt; tags (DEV-2578) ([#490](https://github.com/dasch-swiss/dsp-tools/issues/490)) ([047ba15](https://github.com/dasch-swiss/dsp-tools/commit/047ba155df8aa56e966468049b1c591c043b4cf7))
* **xmlupload:** allow both IDs and IRIs, remove --incremental flag (DEV-1339) ([#494](https://github.com/dasch-swiss/dsp-tools/issues/494)) ([df1cf13](https://github.com/dasch-swiss/dsp-tools/commit/df1cf13eecf30bb95adbf6a81dd2e4b7a5a0c20a))


### Bug Fixes

* **process-files:** default value of batchsize is too big (DEV-2573) [#486](https://github.com/dasch-swiss/dsp-tools/issues/486) ([b1775a9](https://github.com/dasch-swiss/dsp-tools/commit/b1775a9be86f3c0254d052ab93550b1ae7bc4f7b))
* **process-files:** remove docker container before starting / add user feedback (DEV-2601) ([#505](https://github.com/dasch-swiss/dsp-tools/issues/505)) ([8e1b77c](https://github.com/dasch-swiss/dsp-tools/commit/8e1b77c7f460b20c4aaf9e664b6a7450ddcf187a))
* **process-files:** the derivatives are created only at the end (DEV-2625) ([#507](https://github.com/dasch-swiss/dsp-tools/issues/507)) ([1934403](https://github.com/dasch-swiss/dsp-tools/commit/19344034645ebabbccfb826c7d4967b9d130175d))
* **xmlupload:** provide a helpful error message if default-ontology in XML file doesn't exist (DEV-2577) [#489](https://github.com/dasch-swiss/dsp-tools/issues/489) ([7b20ad8](https://github.com/dasch-swiss/dsp-tools/commit/7b20ad8bcfddc03892e3915f3a94fc324fc80c80))
* **xmlupload:** sanitize textvalues: remove whitespaces and newlines (DEV-2569) ([#484](https://github.com/dasch-swiss/dsp-tools/issues/484)) ([d6c8110](https://github.com/dasch-swiss/dsp-tools/commit/d6c811068be6e7f48173d0345ec47ebfd2c7d092))


### Maintenance

* bump start-stack to 2023.09.01 (DEV-2630) ([#508](https://github.com/dasch-swiss/dsp-tools/issues/508)) ([d28f2d8](https://github.com/dasch-swiss/dsp-tools/commit/d28f2d83fe6a029c1b579b10282b7a7354395ca2))
* **deps:** bump the all-dependencies group with 3 updates ([#501](https://github.com/dasch-swiss/dsp-tools/issues/501)) ([f4f6ff8](https://github.com/dasch-swiss/dsp-tools/commit/f4f6ff8cae535281ae1cb469477365bf1a6f643c))
* excel2json (DEV-2547) ([#487](https://github.com/dasch-swiss/dsp-tools/issues/487)) ([504a4ec](https://github.com/dasch-swiss/dsp-tools/commit/504a4ec0d52c1199d42db5fa7eba70f35c0f4ac6))
* improve release-please YAML file (DEV-2599) [#492](https://github.com/dasch-swiss/dsp-tools/issues/492) ([82b3b82](https://github.com/dasch-swiss/dsp-tools/commit/82b3b8269f21d9b2c6f1ee11fec7d043943baa82))
* mute warnings in tests / update gitignore (DEV-2609) [#498](https://github.com/dasch-swiss/dsp-tools/issues/498) ([03e19d7](https://github.com/dasch-swiss/dsp-tools/commit/03e19d792d947236198afec5de441f8fa3963b0f))
* refactor id2iri: remove --outfile and --verbose flags (DEV-2576) ([#488](https://github.com/dasch-swiss/dsp-tools/issues/488)) ([f814667](https://github.com/dasch-swiss/dsp-tools/commit/f814667751629471066ba95d43873027f1852ba5))
* refactor models/connection.py (DEV-2534) ([#495](https://github.com/dasch-swiss/dsp-tools/issues/495)) ([a9caf98](https://github.com/dasch-swiss/dsp-tools/commit/a9caf98c1882cedf465e70bbb5a334c59bcd99fd))
* refactor process-files (DEV-2623) ([#506](https://github.com/dasch-swiss/dsp-tools/issues/506)) ([7595846](https://github.com/dasch-swiss/dsp-tools/commit/75958461006b435ab5bdadb85ab44524138e5fb0))
* rename excel_to_json to excel2json (DEV-2604) [#496](https://github.com/dasch-swiss/dsp-tools/issues/496) ([5a31d5d](https://github.com/dasch-swiss/dsp-tools/commit/5a31d5d3273fc37e71d25367e35792f16699169f))
* run unit tests earlier in GitHub CI (DEV-2600) [#493](https://github.com/dasch-swiss/dsp-tools/issues/493) ([00d5ed6](https://github.com/dasch-swiss/dsp-tools/commit/00d5ed685783e67048043034f217c50233e80aea))
* some small bug fixes and improvements (DEV-2564) ([#483](https://github.com/dasch-swiss/dsp-tools/issues/483)) ([ecd09e9](https://github.com/dasch-swiss/dsp-tools/commit/ecd09e9d8c568e51f6a719145ceaa973d809ac78))
* use typing.TypeGuard for check_notna() (DEV-2608) [#497](https://github.com/dasch-swiss/dsp-tools/issues/497) ([2c4e2f8](https://github.com/dasch-swiss/dsp-tools/commit/2c4e2f8d025e28f918e08af7cde21bc2fde7fece))

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
