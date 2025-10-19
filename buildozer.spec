[app]

# (str) Title of your application
title = Leitor de Cupons Fiscais

# (str) Package name
package.name = qrreader

# (str) Package domain (needed for android/ios packaging)
package.domain = com.business.qrreader

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,txt,csv

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,*.py

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,kivymd,pillow,opencv-python,pyzbar,numpy,plyer,requests

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 30

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 23b

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (list) Pattern to whitelist for the whole project
android.whitelist = 

# (str) Path to a custom whitelist file
android.whitelist_src = 

# (str) Path to a custom blacklist file
android.blacklist_src = 

# (list) Java classes to add as java src in the apk
android.add_src = 

# (list) Java files to add to the libs so they can be loaded by the APK
android.add_jars = 

# (list) List of Java .jar files to add to the libs so they can be loaded by the APK
android.add_java_src = 

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled
android.ouya.category = APP

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file to include as an intent filters in <activity> tag
android.manifest.intent_filters = 

# (str) launchMode to set for the main activity
android.manifest.launch_mode = standard

# (list) Android additionnal libraries to copy into libs/armeabi
android.add_libs_armeabi = 

# (list) Android additionnal libraries to copy into libs/armeabi-v7a
android.add_libs_armeabi_v7a = 

# (list) Android additionnal libraries to copy into libs/arm64-v8a
android.add_libs_arm64_v8a = 

# (list) Android additionnal libraries to copy into libs/x86
android.add_libs_x86 = 

# (list) Android additionnal libraries to copy into libs/mips
android.add_libs_mips = 

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# You can also specify multiple archs separated by comma: armeabi-v7a,arm64-v8a
android.archs = arm64-v8a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
bin_dir = ./bin