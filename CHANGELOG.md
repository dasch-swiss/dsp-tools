# Changelog

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
