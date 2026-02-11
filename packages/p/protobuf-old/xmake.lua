package("protobuf-old")
    set_homepage("https://github.com/protocolbuffers/protobuf")
    set_description("Protocol Buffers - Google's data interchange format")
    -- 指定固定版本
    add_versions("2.5.0", "25abfc115e9044e9b3f57559ecef7da2b5bc9fa06c22e1a4ab2cf79affe29345")

    -- 下载源码
    add_urls("https://github.com/protocolbuffers/protobuf/releases/download/v$(version)/protobuf-$(version).zip",
             "https://github.com/protocolbuffers/protobuf.git")

    -- 默认 fetch 时不需要子模块
    add_deps("autotools", { kind = "binary" })
    add_deps("openssl", { optional = true })

    on_load(function (package)
        -- public headers 和库
        package:add("links", "protobuf-lite")
    end)

    on_install(function (package)
		import("core.base.cpu")
        local configs = {}
        table.insert(configs, "--disable-dependency-tracking")
        table.insert(configs, "--disable-silent-rules")
        table.insert(configs, "--prefix=" .. package:installdir())

        if package:config("shared") then
            table.insert(configs, "--enable-shared")
            table.insert(configs, "--disable-static")
        else
            table.insert(configs, "--disable-shared")
            table.insert(configs, "--enable-static")
        end

        local cc = package:build_getenv("cc") or "cc"
        local cxx = package:build_getenv("cxx") or "c++"
		local cxflags = table.concat(package:build_getenv("cxflags") or "", " ")
		local ldflags = table.concat(package:build_getenv("ldflags") or "", " ")
        local envprefix = string.format("env CC=%s CXX=%s CFLAGS=\"%s\" CXXFLAGS=\"%s\" LDFLAGS=\"%s\"", cc, cxx, cxflags, cxflags, ldflags)

        os.vrun("./autogen.sh")
        os.vrun(envprefix .. " ./configure " .. table.concat(configs, " "))
        os.vrun("make -j" .. (cpu.number() or 1))
        os.vrun("make install")
    end)

    on_test(function (package)
        assert(package:check_cxxsnippets({test=[[
            #include <google/protobuf/stubs/common.h>
            int main() {
                GOOGLE_PROTOBUF_VERIFY_VERSION;
                return 0;
            }
        ]]}, { configs = { languages="c++17", links="protobuf-lite" }}))
    end)

