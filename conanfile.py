from conans import ConanFile, CMake, tools
import os


class wxWidgetsConan(ConanFile):
    name = "wxwidgets"
    version = "3.1.4"
    description = "wxWidgets."
    topics = ("conan", "wxwidgets", "gui", "ui")
    url = ""
    homepage = "https://www.wxwidgets.org"
    license = "wxWidgets"
    exports_sources = ["CMakeLists.txt"]
    generators = ["cmake", "cmake_find_package"]
    settings = "os", "arch", "compiler", "build_type"
    _cmake = None

    options = {"shared": [True, False],
               "fPIC": [True, False],
               "unicode": ['ON', 'OFF'],
               "compatibility": ["2.8", "3.0", "3.1"],
               "zlib": ['OFF', "sys", "builtin", "zlib"],
               "png": ['OFF', "sys", "builtin", "libpng"],
               "jpeg": ['OFF', "sys", "builtin", "libjpeg", "libjpeg-turbo", "mozjpeg"],
               "tiff": ['OFF', "sys", "builtin", "libtiff"],
               "expat": ['OFF', "sys", "builtin", "expat"],
               "secretstore": [True, False],
               "aui": [True, False],
               "opengl": [True, False],
               "html": [True, False],
               "mediactrl": [True, False],  
               "propgrid": [True, False],
               "debugreport": [True, False],
               "ribbon": [True, False],
               "richtext": [True, False],
               "sockets": [True, False],
               "stc": [True, False],
               "webview": [True, False],
               "xml": [True, False],
               "xrc": [True, False],
               "cairo": [True, False],
               "help": [True, False],
               "html_help": [True, False],
               "url": [True, False],
               "protocol": [True, False],
               "fs_inet": [True, False],
               "custom_enables": "ANY", # comma splitted list
               "custom_disables": "ANY"}
    default_options = {
               "shared": False,
               "fPIC": True,
               "unicode": 'ON',
               "compatibility": "3.0",
               "zlib": "sys",
               "png": "sys",
               "jpeg": "OFF", # should be sys 
               "tiff": 'OFF',
               "expat": "sys",
               "secretstore": True,
               "aui": True,
               "opengl": True,
               "html": True,
               "mediactrl": False,
               "propgrid": True,
               "debugreport": True,
               "ribbon": True,
               "richtext": True,
               "sockets": True,
               "stc": True,
               "webview": True,
               "xml": True,
               "xrc": True,
               "cairo": True,
               "help": True,
               "html_help": True,
               "url": True,
               "protocol": True,
               "fs_inet": True,
               "custom_enables": "",
               "custom_disables": ""
    }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        if self.settings.os != 'Linux':
            self.options.remove('cairo')

    #def build_requirements(self):
    #    self.build_requires("ninja/1.10.1")

    # i plan to use the below as well, but for now using the same as my system
    #def requirements(self):
#        if self.options.jpeg == 'libjpeg':
#            self.requires('libjpeg/9d')
#        if self.options.png == 'libpng':
#            self.requires('libpng/1.6.37')
#        if self.options.jpeg == 'libjpeg':
#            self.requires('libjpeg/9d')
#        elif self.options.jpeg == 'libjpeg-turbo':
#            self.requires('libjpeg-turbo/2.0.5')
#        elif self.options.jpeg == 'mozjpeg':
#            self.requires('mozjpeg/3.3.1')
#        if self.options.tiff == 'libtiff':
#            self.requires('libtiff/4.0.9')
#        if self.options.zlib == 'zlib':
#            self.requires('zlib/1.2.11')
#        if self.options.expat == 'expat':
#            self.requires('expat/2.2.7')

    def source(self):
        #tools.get(**self.conan_data["sources"][self.version])
        tools.get("https://github.com/wxWidgets/wxWidgets/archive/v3.1.4.tar.gz", sha256='f2698297b2d2c6d2372c23144c133e531248a64286c78ae17179155c94971d6f')
        extracted_dir = "wxWidgets-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def add_libraries_from_pc(self, library):
        pkg_config = tools.PkgConfig(library)
        libs = [lib[2:] for lib in pkg_config.libs_only_l]  # cut -l prefix
        lib_paths = [lib[2:] for lib in pkg_config.libs_only_L]  # cut -L prefix
        self.cpp_info.libs.extend(libs)
        self.cpp_info.libdirs.extend(lib_paths)
        self.cpp_info.sharedlinkflags.extend(pkg_config.libs_only_other)
        self.cpp_info.exelinkflags.extend(pkg_config.libs_only_other)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        cmake = CMake(self)

        # generic build options
        cmake.definitions['wxBUILD_SHARED'] = self.options.shared
        cmake.definitions['wxBUILD_SAMPLES'] = 'SOME' #'SOME' # should be OFF
        cmake.definitions['wxBUILD_TESTS'] = 'OFF'
        cmake.definitions['wxBUILD_DEMOS'] = 'OFF'
        cmake.definitions['wxBUILD_INSTALL'] = True
        cmake.definitions['wxBUILD_COMPATIBILITY'] = self.options.compatibility
        if self.settings.compiler == 'clang':
            cmake.definitions['wxBUILD_PRECOMP'] = 'OFF'

        # platform-specific options
        if self.settings.compiler == 'Visual Studio':
            cmake.definitions['wxBUILD_USE_STATIC_RUNTIME'] = 'MT' in str(self.settings.compiler.runtime)
            cmake.definitions['wxBUILD_MSVC_MULTIPROC'] = True
        if self.settings.os == 'Linux':
            # TODO : GTK3
            cmake.definitions['wxBUILD_TOOLKIT'] = 'gtk3'
            cmake.definitions['wxUSE_CAIRO'] = self.options.cairo
        # Disable some optional libraries that will otherwise lead to non-deterministic builds
        if self.settings.os != "Windows":
            cmake.definitions['wxUSE_LIBSDL'] = 'OFF'
            cmake.definitions['wxUSE_LIBICONV'] = 'OFF'
            cmake.definitions['wxUSE_LIBNOTIFY'] = 'OFF'
            cmake.definitions['wxUSE_LIBMSPACK'] = 'OFF'
            cmake.definitions['wxUSE_LIBGNOMEVFS'] = 'OFF'

        cmake.definitions['wxUSE_LIBPNG'] = 'sys' if self.options.png != 'OFF' else 'OFF'
        cmake.definitions['wxUSE_LIBJPEG'] = 'sys' if self.options.jpeg != 'OFF' else 'OFF'
        cmake.definitions['wxUSE_LIBTIFF'] = 'sys' if self.options.tiff != 'OFF' else 'OFF'
        cmake.definitions['wxUSE_ZLIB'] = 'sys' if self.options.zlib != 'OFF' else 'OFF'
        cmake.definitions['wxUSE_EXPAT'] = 'sys' if self.options.expat != 'OFF' else 'OFF'
        

        # wxWidgets features
        cmake.definitions['wxUSE_UNICODE'] = self.options.unicode
        cmake.definitions['wxUSE_SECRETSTORE'] = self.options.secretstore

        # wxWidgets libraries
        cmake.definitions['wxUSE_AUI'] = self.options.aui
        cmake.definitions['wxUSE_OPENGL'] = self.options.opengl
        cmake.definitions['wxUSE_HTML'] = self.options.html
        cmake.definitions['wxUSE_MEDIACTRL'] = self.options.mediactrl
        cmake.definitions['wxUSE_PROPGRID'] = self.options.propgrid
        cmake.definitions['wxUSE_DEBUGREPORT'] = self.options.debugreport
        cmake.definitions['wxUSE_RIBBON'] = self.options.ribbon
        cmake.definitions['wxUSE_REGEX'] = 'OFF' #'builtin'
        cmake.definitions['wxUSE_RICHTEXT'] = self.options.richtext
        cmake.definitions['wxUSE_SOCKETS'] = self.options.sockets
        cmake.definitions['wxUSE_STC'] = self.options.stc
        cmake.definitions['wxUSE_WEBVIEW'] = self.options.webview
        cmake.definitions['wxUSE_XML'] = self.options.xml
        cmake.definitions['wxUSE_XRC'] = self.options.xrc
        cmake.definitions['wxUSE_HELP'] = self.options.help
        cmake.definitions['wxUSE_WXHTML_HELP'] = self.options.html_help
        cmake.definitions['wxUSE_URL'] = self.options.protocol
        cmake.definitions['wxUSE_PROTOCOL'] = self.options.protocol
        cmake.definitions['wxUSE_FS_INET'] = self.options.fs_inet

        for item in str(self.options.custom_enables).split(","):
            if len(item) > 0:
                cmake.definitions[item] = True
        for item in str(self.options.custom_disables).split(","):
            if len(item) > 0:
                cmake.definitions[item] = False

        cmake.configure(build_folder=self._build_subfolder)

        self._cmake = cmake 
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # copy setup.h
        self.copy(pattern='*setup.h', dst=os.path.join('include', 'wx'), src=os.path.join(self._build_subfolder, 'lib'),
                  keep_path=False)

        if self.settings.os == 'Windows':
            # copy wxrc.exe
            self.copy(pattern='*', dst='bin', src=os.path.join(self._build_subfolder, 'bin'), keep_path=False)
        else:
            # make relative symlink
            bin_dir = os.path.join(self.package_folder, 'bin')
            for x in os.listdir(bin_dir):
                filename = os.path.join(bin_dir, x)
                if os.path.islink(filename):
                    target = os.readlink(filename)
                    if os.path.isabs(target):
                        rel = os.path.relpath(target, bin_dir)
                        os.remove(filename)
                        os.symlink(rel, filename)

    def package_info(self):
        version_tokens = self.version.split('.')
        version_major = version_tokens[0]
        version_minor = version_tokens[1]
        version_suffix_major_minor = '-%s.%s' % (version_major, version_minor)
        unicode = 'u' if self.options.unicode else ''
        
        # wx no longer uses a debug suffix for non-windows platforms from 3.1.3 onwards
        use_debug_suffix = False
        if self.settings.build_type == 'Debug':
            version_list = [int(part) for part in version_tokens]
            use_debug_suffix = (self.settings.os == 'Windows' or version_list < [3, 1, 3])
        
        debug = 'd' if use_debug_suffix else ''
        
        if self.settings.os == 'Linux':
            prefix = 'wx_'
            toolkit = 'gtk3'
            version = ''
            suffix = version_suffix_major_minor
        elif self.settings.os == 'Macos':
            prefix = 'wx_'
            toolkit = 'osx_cocoa'
            version = ''
            suffix = version_suffix_major_minor
        elif self.settings.os == 'Windows':
            prefix = 'wx'
            toolkit = 'msw'
            version = '%s%s' % (version_major, version_minor)
            suffix = ''

        def base_library_pattern(library):
            return '{prefix}base{version}{unicode}{debug}_%s{suffix}' % library

        def library_pattern(library):
            return '{prefix}{toolkit}{version}{unicode}{debug}_%s{suffix}' % library
            
        def external_library_pattern(library):
            return 'wx%s{unicode}{debug}{suffix}' % library 

        # pim: perhaps also no debug ...
        def external_library_pattern_no_unicode(library):
            return 'wx%s{debug}{suffix}' % library 
            
        libs = ['{prefix}base{version}{unicode}{debug}{suffix}',
                library_pattern('core'),
                library_pattern('adv')]
        
        #libs.append(external_library_pattern_no_unicode('scintilla'))
        if self.options.stc:
            if not self.options.shared:
                scintilla_suffix = '{debug}' if self.settings.os == "Windows" else '{suffix}'
                libs.append('wxscintilla' + scintilla_suffix)
            libs.append(library_pattern('stc'))
        if self.options.sockets:
            libs.append(base_library_pattern('net'))
        if self.options.xml:
            libs.append(base_library_pattern('xml'))
        if self.options.aui:
            libs.append(library_pattern('aui'))
        if self.options.opengl:
            libs.append(library_pattern('gl'))
        if self.options.html:
            libs.append(library_pattern('html'))
        if self.options.mediactrl:
            libs.append(library_pattern('media'))
        if self.options.propgrid:
            libs.append(library_pattern('propgrid'))
        if self.options.debugreport:
            libs.append(library_pattern('qa'))
        if self.options.ribbon:
            libs.append(library_pattern('ribbon'))
        if self.options.richtext:
            libs.append(library_pattern('richtext'))
        if self.options.webview:
            libs.append(library_pattern('webview'))
        if self.options.xrc:
            libs.append(library_pattern('xrc'))
        #pim:addded
#        libs.append(external_library_pattern('regex'))
        
        for lib in reversed(libs):
            self.cpp_info.libs.append(lib.format(prefix=prefix,
                                                 toolkit=toolkit,
                                                 version=version,
                                                 unicode=unicode,
                                                 debug=debug,
                                                 suffix=suffix))

        self.cpp_info.defines.append('wxUSE_GUI=1')
        if self.settings.build_type == 'Debug':
            self.cpp_info.defines.append('__WXDEBUG__')
        if self.settings.os == 'Linux':
            self.cpp_info.defines.append('__WXGTK__')
            self.cpp_info.defines.append('__WXGTK3__')
            self.add_libraries_from_pc('gtk+-3.0')
            self.add_libraries_from_pc('webkit2gtk-4.0')
            self.add_libraries_from_pc('x11')
            self.cpp_info.libs.extend(['dl', 'pthread', 'png'])
            #self.cpp_info.libs.extend(['dl', 'pthread', 'SM'])
        if self.settings.os != 'Windows':
            unix_include_path = os.path.join("include", "wx{}".format(version_suffix_major_minor))
            self.cpp_info.includedirs = [unix_include_path] + self.cpp_info.includedirs
