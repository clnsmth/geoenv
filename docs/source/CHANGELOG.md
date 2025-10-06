
# CHANGELOG



## v0.4.0 (2025-10-06)


### Continuous integration

* ci: separate real request tests, add new triggers ([`a66003b`](https://github.com/clnsmth/geoenv/commit/a66003b5a9cb473c93377976360b494cc0a12c89)) 
* ci: fix release to PyPI step ([`5600685`](https://github.com/clnsmth/geoenv/commit/5600685c8723214207693da0593d8eae2084d836)) 

### Documentation

* docs: reorder top level documentation ([`404f489`](https://github.com/clnsmth/geoenv/commit/404f489d5780bd7e7603a4e4ed95341153306185)) 
* docs: improve quickstart clarity and reorder sections ([`a5aa115`](https://github.com/clnsmth/geoenv/commit/a5aa1158577deee0991a534797ce6346e798aeb4)) 
* docs: demo a common use case ([`ec2fa07`](https://github.com/clnsmth/geoenv/commit/ec2fa07884850fa922a71e220a5218d75aca353d)) 
* docs: edit documentation ([`570ceb4`](https://github.com/clnsmth/geoenv/commit/570ceb488950c5ae877b273db514e7a2f5e47031)) 

### Features

* feat: improve user agent string for HTTP requests (#43) ([`60163eb`](https://github.com/clnsmth/geoenv/commit/60163ebbdf22fe4ccd72d951e402a94030003774)) 

### Testing

* test: relax ECU response comparison to reduce test flakiness ([`09efa1c`](https://github.com/clnsmth/geoenv/commit/09efa1c6b404c4c2fb4eda188b196190715a2a7f)) 
* test: realign ECU mock with changed API response ([`42ec6ad`](https://github.com/clnsmth/geoenv/commit/42ec6ad0da53447d88b5f698db908ffd2ceabb7d)) 

## v0.3.0 (2025-09-05)


### Documentation

* docs: change PyPI badge to blue coloration ([`238d8c9`](https://github.com/clnsmth/geoenv/commit/238d8c979d8650f0c66185a01eda52202cf634fb)) 
* docs: remove stray sidebar and changelog files ([`0d8223c`](https://github.com/clnsmth/geoenv/commit/0d8223cc8c843bd8db987a4b48342dc30fd03f28)) 
* docs: more nuanced motivation section ([`696f0f8`](https://github.com/clnsmth/geoenv/commit/696f0f8cd49da7130788e05a396e10957b16b0d8)) 

### Features

* feat: implement concurrent data source resolution ([`de5a2a8`](https://github.com/clnsmth/geoenv/commit/de5a2a850f7c6c4f6dcfc34588755a1adf919133)) 

### Testing

* test: control real requests with environmental variable ([`af42d08`](https://github.com/clnsmth/geoenv/commit/af42d0823b5f381458cf9d616d08f7e5876a8d3c)) 

## v0.2.4 (2025-08-11)


### Bug fixes

* fix: don't template sidebars ([`b2f9b26`](https://github.com/clnsmth/geoenv/commit/b2f9b265d23af915f48d2d069a7e79bb3149d439)) 

## v0.2.3 (2025-08-11)


### Bug fixes

* fix: broken logo reference ([`6942561`](https://github.com/clnsmth/geoenv/commit/69425618f73cf3caea8ad81c6b1630501054c750)) 

## v0.2.2 (2025-08-11)


### Bug fixes

* fix: logo and quickstart reference ([`b9c1b81`](https://github.com/clnsmth/geoenv/commit/b9c1b816e4cf517e20b2a73b4eda1a0201c9a53b)) 

### Documentation

* docs: fix changelog auto build ([`da623c3`](https://github.com/clnsmth/geoenv/commit/da623c311aee1166c876fcd9d2edf80db91a5c3b)) 
* docs: align .toml project description ([`d866852`](https://github.com/clnsmth/geoenv/commit/d866852c34022fe5532eebfd1bac09ab5f5409f0)) 

## v0.2.1 (2025-08-11)


### Bug fixes

* fix: bump rebuild of the package to repost to PyPI ([`a2dc545`](https://github.com/clnsmth/geoenv/commit/a2dc54595f988da1086c7efbde3a6d27b1a9a4c3)) 

### Build system

* build: update environment.yml and requirements.txt ([`cf26e2b`](https://github.com/clnsmth/geoenv/commit/cf26e2b9c770073ba826a8b2ad117c0eb70548c3)) 
* build: lower python version requirement ([`92e44dd`](https://github.com/clnsmth/geoenv/commit/92e44dd465551a0b081e222624b135a6363e4d98)) 

### Continuous integration

* ci: remove redundant Poetry and package installation ([`5cfd4d9`](https://github.com/clnsmth/geoenv/commit/5cfd4d9216e16e6f0a0f43833d066d6e884cd8a9)) 
* ci: harmonize black formatting versions ([`377e2f1`](https://github.com/clnsmth/geoenv/commit/377e2f10ad939a8ef0af36fd8f4634ebc221963e)) 

### Documentation

* docs: add PyPI installation instructions and badge ([`fe1ae44`](https://github.com/clnsmth/geoenv/commit/fe1ae447cf3bf2e4eda1d1bc5197414863d8f227)) 
* docs: add a logo for branding ([`1702856`](https://github.com/clnsmth/geoenv/commit/1702856d1fc4e3701bc27e95a0ca32e76d32b8bf)) 
* docs: improve project website home page ([`0f06038`](https://github.com/clnsmth/geoenv/commit/0f0603881c540bad5495acced6f2031069ce834b)) 
* docs: refine documentation for upcoming release ([`d555621`](https://github.com/clnsmth/geoenv/commit/d5556211cad9b2a6d65cef3e31737e45b50f45c8)) 

### Testing

* test: stabilize tests by focusing on relevant HTTP response content ([`3ebf4e9`](https://github.com/clnsmth/geoenv/commit/3ebf4e9c264bc5be8cd48b22d13aa8ccd4abb834)) 

### Unknown

* Migrate code base from `geoenvo` to `geoenv` ([`25f2f9c`](https://github.com/clnsmth/geoenv/commit/25f2f9c5268afbbb03083b0fc48dc9434c74ba7b))


## v0.2.0 (2025-03-12)


### Features

* feat: release to production PyPI ([`544f6c8`](https://github.com/clnsmth/geoenv/commit/544f6c85125862edc02d1ed3a1455680fdbfddd8)) 

## v0.1.1 (2025-03-12)


### Bug fixes

* fix: trivial change for testing release to PyPI ([`8e5e3c0`](https://github.com/clnsmth/geoenv/commit/8e5e3c09123051b86b90d348feaf5347a48bf7a2)) 

## v0.1.0 (2025-03-12)


### Features

* feat: release to test PyPI ([`a8049cf`](https://github.com/clnsmth/geoenv/commit/a8049cfbed69c769f6fb8697dbf191af8264db98)) 

## v0.0.0 (2025-03-12)


### Unknown

* Set up basic project files and structure ([`683c9b9`](https://github.com/clnsmth/geoenv/commit/683c9b9a6b3bbbf7021ed63852536e8caed93703))
