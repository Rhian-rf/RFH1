
[app]

title = RFH1

package.name = rfh1

package.domain = com.rfh

source.dir = .

source.include_exts = py,json,png,jpg,kv,atlas

version = 1.0.0

requirements = python3==3.14.2,kivy,charset-normalizer==3.4.9

orientation = portrait

fullscreen = 0

android.permissions =

android.api = 35

android.minapi = 24

android.archs = arm64-v8a

android.accept_sdk_license = True

p4a.bootstrap = sdl2

p4a.branch = develop
p4a.commit = HEAD

[buildozer]

log_level = 2

warn_on_root = 1
