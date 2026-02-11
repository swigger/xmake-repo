---
name: xmake-skill
description: 使用 xmake 来编译工程
---

# 综述

Xmake 是一个基于 Lua 的轻量级跨平台构建工具。它使用 `xmake.lua` 作为工程描述文件，语法简洁直观。Xmake 既能像 Make/Ninja 那样直接编译项目，也能像 CMake 那样生成工程文件，还内置了包管理系统来解决 C/C++ 依赖库的集成问题。

核心工作流：
1. `xmake create <project>` — 创建工程
2. `xmake f -p <platform> -m <mode>` — 配置平台和编译模式（可省略，自动检测）
3. `xmake` — 构建（等价于 `xmake build`）
4. `xmake run` — 运行目标程序
5. `xmake install` — 安装
6. `xmake clean` — 清理构建产物
7. `xmake test` — 运行测试

最小 xmake.lua 只需三行：

```lua
target("hello")
    set_kind("binary")
    add_files("src/*.cpp")
```

xmake.lua 分为描述域和脚本域。描述域用 `set_xxx`/`add_xxx` 做声明式配置（占 80% 场景），脚本域通过 `on_xxx`/`before_xxx`/`after_xxx` 的 `function() end` 回调实现复杂逻辑（占 20% 场景）。描述域会被多次解析，不要在其中写复杂脚本或 print。

配置作用域按树状结构继承：根作用域的配置影响所有 target（包括 `includes()` 引入的子目录），target 作用域仅影响当前 target。

# 典型例子

## 1. 可执行程序 + 静态库依赖

```lua
add_rules("mode.debug", "mode.release")

target("mylib")
    set_kind("static")
    add_files("src/lib/*.cpp")
    add_headerfiles("include/*.h")

target("app")
    set_kind("binary")
    add_deps("mylib")           -- 自动链接 mylib，无需额外 add_links
    add_files("src/main.cpp")
    add_includedirs("include")
```

构建和运行：

```sh
xmake
xmake run app
```

## 2. 使用第三方依赖包

```lua
add_rules("mode.debug", "mode.release")
add_requires("zlib", "fmt ~10.0", "spdlog", {configs = {header_only = true}})

target("app")
    set_kind("binary")
    add_files("src/*.cpp")
    add_packages("zlib", "fmt", "spdlog")
```

`add_requires` 声明依赖（支持语义版本），`add_packages` 绑定到 target，自动处理 links/includedirs。

## 3. 多平台条件编译

```lua
add_rules("mode.debug", "mode.release")

target("app")
    set_kind("binary")
    add_files("src/common/*.cpp")
    if is_plat("windows") then
        add_files("src/win/*.cpp")
        add_syslinks("user32", "ws2_32")
    elseif is_plat("linux") then
        add_files("src/linux/*.cpp")
        add_syslinks("pthread", "dl")
    elseif is_plat("macosx") then
        add_files("src/mac/*.cpp")
        add_frameworks("Foundation", "CoreFoundation")
    end
```

## 4. 动态库

```lua
target("myshared")
    set_kind("shared")
    add_files("src/*.cpp")

target("app")
    set_kind("binary")
    add_deps("myshared")
    add_files("src/main.cpp")
```

## 5. 多级目录结构

```lua
-- 根 xmake.lua
add_rules("mode.debug", "mode.release")
add_defines("ROOT_FLAG")
includes("lib", "app")
```

```lua
-- lib/xmake.lua
target("mylib")
    set_kind("static")
    add_files("*.cpp")
```

```lua
-- app/xmake.lua
target("myapp")
    set_kind("binary")
    add_deps("mylib")
    add_files("*.cpp")
```

根作用域的 `add_defines("ROOT_FLAG")` 会继承到所有子目录的 target。

## 6. 交叉编译

```sh
# Android
xmake f -p android --ndk=~/android-ndk-r25 -a arm64-v8a
xmake

# 通用交叉编译
xmake f -p cross --sdk=/path/to/toolchain
xmake

# WebAssembly
xmake f -p wasm
xmake

# iOS
xmake f -p iphoneos -a arm64
xmake

# MinGW
xmake f -p mingw
xmake
```

## 7. 自定义选项

```lua
option("with_tests", {default = false, description = "Enable tests"})

target("app")
    set_kind("binary")
    add_files("src/*.cpp")

if has_config("with_tests") then
    target("test")
        set_kind("binary")
        add_files("tests/*.cpp")
        add_tests("default")
end
```

```sh
xmake f --with_tests=y
xmake
xmake test
```

## 8. 自定义规则

```lua
rule("protobuf")
    set_extensions(".proto")
    on_build_file(function (target, sourcefile, opt)
        import("core.project.depend")
        local targetfile = path.join(target:autogendir(), path.basename(sourcefile) .. ".pb.cc")
        depend.on_changed(function ()
            os.vrunv("protoc", {"--cpp_out=" .. target:autogendir(), sourcefile})
        end, {files = sourcefile})
        target:add("files", targetfile)
    end)

target("app")
    set_kind("binary")
    add_rules("protobuf")
    add_files("src/*.cpp", "proto/*.proto")
```

## 9. 远程拉取工具链

```lua
add_requires("llvm 15.x", {alias = "llvm-15"})

target("app")
    set_kind("binary")
    add_files("src/*.c")
    set_toolchains("llvm@llvm-15")
```

## 10. 测试用例

```lua
add_rules("mode.debug", "mode.release")
add_requires("doctest")

target("myapp")
    set_kind("binary")
    add_files("src/*.cpp")
    for _, testfile in ipairs(os.files("tests/*.cpp")) do
        add_tests(path.basename(testfile), {
            files = testfile,
            remove_files = "src/main.cpp",
            packages = "doctest",
            defines = "DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN"
        })
    end
```

```sh
xmake test
xmake test -vD          -- 查看详细失败信息
xmake test myapp/foo*   -- 运行匹配的测试
```

# 分类指引

以下按主题分类列出文档路径，供深入查阅。所有路径相对于 `zh/` 目录。

## 入门与安装
- `guide/introduction.md` — Xmake 简介
- `guide/quick-start.md` — 快速上手（安装、创建、构建、运行）

## 基础命令
- `guide/basic-commands/create-project.md` — `xmake create` 创建工程（支持 `-l` 指定语言、`-t` 指定模板如 console/static/shared）
- `guide/basic-commands/build-configuration.md` — `xmake f/config` 编译配置（切换平台 `-p`、架构 `-a`、模式 `-m`、全局配置 `xmake g`、清除配置 `-c`、导入导出配置）
- `guide/basic-commands/build-targets.md` — `xmake build` 构建（`-r` 重建、`-a` 构建全部、`-v` 查看编译命令、`-vD` 查看错误堆栈）
- `guide/basic-commands/run-targets.md` — `xmake run` 运行（`-d` 调试、`-w` 工作目录、传递运行参数）
- `guide/basic-commands/run-tests.md` — `xmake test` 测试（`add_tests` 配置、doctest/gtest 集成、模式匹配、超时、预期输出）
- `guide/basic-commands/clean-targets.md` — `xmake clean` 清理（`-a` 清理所有模式和架构）
- `guide/basic-commands/install-and-uninstall.md` — `xmake install/uninstall` 安装卸载（`-o` 指定目录）
- `guide/basic-commands/pack-programs.md` — `xmake package/pack` 打包（本地包、远程包、XPack 安装包如 NSIS/DEB/RPM）
- `guide/basic-commands/switch-toolchains.md` — 命令行切换工具链（gcc/clang/llvm/mingw/tinyc/armcc/zig/emcc/cuda/ndk 等）
- `guide/basic-commands/cross-compilation.md` — 交叉编译（`--sdk`/`--bin`/`--cross` 参数、自定义平台、MingW/LLVM/GNU-RM 等工具链）

## 工程配置（xmake.lua 编写）
- `guide/project-configuration/syntax-description.md` — 语法说明（描述域 vs 脚本域、配置域与作用域、缩进规范、简化语法、可选域语法）
- `guide/project-configuration/configure-targets.md` — 配置目标（target 类型 binary/static/shared/object/headeronly/phony、宏定义、优化、头文件目录、链接库、编译选项、依赖、源文件、语言标准、平台条件、规则、运行时、分组等）
- `guide/project-configuration/add-packages.md` — 添加依赖包（`add_requires` + `add_packages`、版本约束、可选包、别名、平台限定、包配置参数）
- `guide/project-configuration/define-options.md` — 定义选项（`option()` 自定义命令行选项、绑定到 target、布尔/字符串/多值类型）
- `guide/project-configuration/custom-rule.md` — 自定义规则（`rule()` 定义、文件扩展名关联、生命周期回调、单文件/批量处理、批处理命令模式）
- `guide/project-configuration/toolchain-configuration.md` — 工具链配置（`set_toolchains` 按 target 切换、自定义工具链 `toolchain()`、远程拉取工具链、简化语法）
- `guide/project-configuration/multi-level-directories.md` — 多级目录（`includes()` 引入子目录、树状配置继承）
- `guide/project-configuration/namespace-isolation.md` — 命名空间隔离
- `guide/project-configuration/plugin-and-task.md` — 插件和任务（`task()` 自定义命令行任务、菜单参数、在构建流程中调用）

## 包管理
- `guide/package-management/using-official-packages.md` — 使用官方包
- `guide/package-management/using-third-party-packages.md` — 使用第三方包（vcpkg/conan/conda/homebrew/apt/pacman 等）
- `guide/package-management/using-system-packages.md` — 使用系统包
- `guide/package-management/using-local-packages.md` — 使用本地包
- `guide/package-management/using-source-code-packages.md` — 使用源码包
- `guide/package-management/using-packages-in-cmake.md` — 在 CMake 中使用 xmake 包
- `guide/package-management/package-distribution.md` — 包分发
- `guide/package-management/distribute-private-libraries.md` — 分发私有库
- `guide/package-management/repository-management.md` — 仓库管理
- `guide/package-management/package-management-in-project.md` — 工程内包管理
- `guide/package-management/network-optimization.md` — 网络优化
- `guide/package-management/xrepo-cli.md` — xrepo 命令行工具

## 高级特性
- `guide/extras/build-cache.md` — 构建缓存
- `guide/extras/distributed-compilation.md` — 分布式编译
- `guide/extras/remote-compilation.md` — 远程编译
- `guide/extras/unity-build.md` — Unity Build
- `guide/extras/autoscan-sourcecode.md` — 自动扫描源码（从 CMake/Makefile 等迁移）
- `guide/extras/trybuild-3rd-sourcecode.md` — 尝试构建第三方源码
- `guide/extras/environment-variables.md` — 环境变量

## 扩展与插件
- `guide/extensions/builtin-plugins.md` — 内置插件（宏脚本、生成工程文件、doxygen 等）
- `guide/extensions/ide-integration-plugins.md` — IDE 集成（VSCode/VS/Sublime/CMake/Makefile 生成等）
- `guide/extensions/plugin-development.md` — 插件开发
- `guide/extensions/theme-style.md` — 主题样式

## 最佳实践
- `guide/best-practices/faq.md` — 常见问题（静默构建 `-q`、查看警告 `-w`、证书问题、调试源码、git bisect 定位问题）
- `guide/best-practices/performance.md` — 性能优化
- `guide/best-practices/configuration-optimization.md` — 配置优化
- `guide/best-practices/ai-qa-optimization.md` — AI 问答优化

## API 参考
- `api/description/specification.md` — 接口规范
- `api/description/global-interfaces.md` — 全局接口（`includes`、`add_requires`、`add_repositories`、`set_project` 等）
- `api/description/project-target.md` — 工程目标 API（`target()`、`set_kind`、`add_files`、`add_deps`、`add_packages`、`set_toolchains`、`add_tests` 等，最完整的 API 参考）
- `api/description/configuration-option.md` — 配置选项 API
- `api/description/custom-rule.md` — 自定义规则 API
- `api/description/custom-toolchain.md` — 自定义工具链 API
- `api/description/package-dependencies.md` — 包依赖 API
- `api/description/builtin-rules.md` — 内置规则（mode.debug/release、Qt、WDK、C++ Modules 等）
- `api/description/builtin-policies.md` — 内置策略
- `api/description/builtin-variables.md` — 内置变量（`$(projectdir)`、`$(buildir)` 等）
- `api/description/conditions.md` — 条件判断（`is_plat`、`is_arch`、`is_mode`、`is_host`、`has_config` 等）
- `api/description/helper-interfaces.md` — 辅助接口
- `api/description/plugin-and-task.md` — 插件任务 API
- `api/description/xpack-interfaces.md` — XPack 打包接口
- `api/scripts/target-instance.md` — target 实例接口（脚本域中操作 target 对象）
- `api/scripts/package-instance.md` — package 实例接口
- `api/scripts/option-instance.md` — option 实例接口
- `api/scripts/native-modules.md` — 原生模块
- `api/scripts/builtin-modules/` — 内置脚本模块（import、os、io、path 等）
- `api/scripts/extension-modules/` — 扩展脚本模块

## 示例
- `examples/cpp/basic.md` — C/C++ 基础示例（可执行程序、静态库、动态库）
- `examples/cpp/cxx-modules.md` — C++20 Modules
- `examples/cpp/packages.md` — 包管理示例
- `examples/cpp/protobuf.md` — Protobuf 集成
- `examples/cpp/wasm.md` — WebAssembly 编译
- `examples/cpp/wdk.md` — Windows 驱动开发
- `examples/cpp/linux-driver-module.md` — Linux 内核模块
- `examples/other-languages/` — 其他语言（Rust、Go、Zig、Fortran、Cuda、Swift、Nim、D、Pascal、Vala、Objective-C）
- `examples/embed/` — 嵌入式（Keil MDK、Verilog）
- `examples/configuration/` — 配置示例（自动生成、自定义工具链、远程工具链等）
