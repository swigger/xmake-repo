package("utilwin")
    set_homepage("https://github.com/swigger/utilwin")
    set_description("A collection of POSIX/Unix utility functions for Windows")
    set_license("Apache-2.0")

    add_urls("https://github.com/swigger/utilwin/archive/refs/tags/v1.0.12.tar.gz")
    add_urls("https://github.com/swigger/utilwin.git")
    
    add_versions("1.0.12", "85f0d0f78bbcd9d5a1daada04358bd0cd8b91299f3b5803df094dee6af644b6b")

    add_syslinks("ntdll")

    on_install("windows", function (package)
        local configs = {}
        import("package.tools.xmake").install(package, configs)
    end)

    on_test(function (package)
        assert(package:check_cxxsnippets({test = [[
            #include <windows.h>
            #include <dirent.h>
            void test() {}
        ]]}, {configs = {languages = "c++11"}}))
    end)
