# 内置插件 {#builtin-plugins}

## 生成 IDE 工程文件 {#generate-ide-projects}

### 简介

XMake 跟 `cmake`、`premake` 等其他一些构建工具的区别在于：

::: tip 注意
`xmake` 默认是直接构建运行的，生成第三方 IDE 的工程文件仅仅作为 `插件` 来提供。
:::

这样做的一个好处是：插件更容易扩展，维护也更加独立和方便。

### 生成 Makefile {#generate-makefile}

```sh
$ xmake project -k makefile
```

### 生成 CMakelists.txt {#generate-cmakelists}

```sh
$ xmake project -k cmakelists
```

### 生成 build.ninja {#generate-build-ninja}

```sh
$ xmake project -k ninja
```

### 生成 compiler\_flags {#generate-compiler-flags}

```sh
$ xmake project -k compiler_flags
```

### 生成 compile\_commands {#generate-compile-commands}

导出每个源文件的编译信息，生成基于 clang 的编译数据库文件，json 格式，可用于与 IDE、编辑器、静态分析工具进行交互。

```sh
$ xmake project -k compile_commands
```

输出的内容格式如下：

```
[
  { "directory": "/home/user/llvm/build",
    "command": "/usr/bin/clang++ -Irelative -DSOMEDEF=\"With spaces, quotes and \\-es.\" -c -o file.o file.cc",
    "file": "file.cc" },
  ...
]

```

对于 `compile_commands` 的详细说明见：[JSONCompilationDatabase](https://clang.llvm.org/docs/JSONCompilationDatabase.html)

### 生成 Xcode 工程文件 {#generate-xcode-project}

目前历史版本是利用 CMake 来生成的 Xcode 工程，不过最新的 dev 版本，也就是后续即将发布的 3.0.1 版本，将会带来原生的 Xcode 生成器。

如果想要提前体验，可以更新到 xmake dev 版本试用，`xmake update -s dev`。

具体详情见：[issue #4810](https://github.com/xmake-io/xmake/issues/4810)。

```sh
$ xmake project -k xcode
```

### 生成 VisualStudio 工程 {#generate-vs-project}

#### 使用 xmake 集成编译 {#generate-vsxmake}

v2.2.8以上版本，提供了新版本的vs工程生成插件扩展，与之前的生成vs的插件处理模式有很大不同，之前生成的vs工程是把所有文件的编译展开后，转交给vs来处理编译。

但是这种模式，对xmake的rules是没法支持的。因为xmake的rules里面用了很多的`on_build`此类自定义脚本，无法展开，所以像qt， wdk此类的项目就没法支持导出到vs里面进行编译了。

因此，为了解决这个问题，新版本的vs生成插件通过在vs下直接调用xmake命令，去执行编译操作，并且对intellsence和定义跳转，还有断点调试也做了支持。

具体使用方式跟老版本类似：

```sh
$ xmake project -k [vsxmake2010|vsxmake2013|vsxmake2015|..] -m "debug;release"
```

如果没指明版本，那么xmake会自动探测当前已有的vs版本来生成：

```sh
$ xmake project -k vsxmake -m "debug,release"
```

![](/assets/img/manual/qt_vs.png)

另外，vsxmake插件还会额外生成一个自定义的配置属性页，用于在vs里面，方便灵活的修改和追加一些xmake编译配置，甚至可以在里面配置切换到其他交叉工具链，实现在vs中对android, linux等其他平台的交叉编译。

![](/assets/img/manual/property_page_vsxmake.png)

v2.5.1 版本提供了一个 `add_rules("plugin.vsxmake.autoupdate")` 规则，如果应用此规则，生成的vs工程在编译完成后，会检测 xmake.lua 和代码文件列表的改动，如果有变化，就会自动更新 vs 工程。

```lua
add_rules("plugin.vsxmake.autoupdate")
target("test")
    set_kind("binary")
    add_files("src/*.c")
```

另外，我们可以通过 `set_group` 接口对每个 target 设置分组，使得生成的 vs 工程可以按指定结构进行分组。更多详情见：[issue #1026](https://github.com/xmake-io/xmake/issues/1026)

#### 使用 vs 内置编译机制 {#generate-vs}

::: tip 注意
建议尽量使用上文提到的v2.2.8之后提供的新版的vs生成插件，支持更加完善，此处的生成方式不支持xmake的rules，以及对qt等工程的生成。
:::

```sh
$ xmake project -k [vs2008|vs2013|vs2015|..]
```

v2.1.2以上版本，增强了vs201x版本工程的生成，支持多模式+多架构生成，生成的时候只需要指定：

```sh
$ xmake project -k vs2017 -m "debug,release"
```

生成后的工程文件，同时支持`debug|x86`, `debug|x64`, `release|x86`, `release|x64`四种配置模式。

如果不想每次生成的时候，指定模式，可以把模式配置加到`xmake.lua`的中，例如：

```lua
-- 配置当前的工程，支持哪些编译模式
add_rules("mode.debug", "mode.release")
```

另外，我们可以通过 `set_group` 接口对每个 target 设置分组，使得生成的 vs 工程可以按指定结构进行分组。更多详情见：[issue #1026](https://github.com/xmake-io/xmake/issues/1026)

## 运行自定义 lua 脚本 {#run-lua-scripts}

这个跟宏脚本类似，只是省去了导入导出操作，直接指定lua脚本来加载运行，这对于想要快速测试一些接口模块，验证自己的某些思路，都是一个不错的方式。

### 运行指定的脚本文件

我们先写个简单的lua脚本：

```lua
function main()
    print("hello xmake!")
end
```

然后直接运行它就行了：

```sh
$ xmake lua /tmp/test.lua
```

::: tip 注意
当然，你也可以像宏脚本那样，使用`import`接口导入扩展模块，实现复杂的功能。
:::

### 从标准输入运行脚本

`xmake lua` 命令现在支持从标准输入 (stdin) 读取并运行脚本，允许你通过管道将脚本内容传递给 xmake。

```bash
$ echo 'print("hello xmake")' | xmake lua --stdin
hello xmake
```

或者：

```bash
$ cat script.lua | xmake lua --stdin
```

### 运行内置的脚本命令

你可以运行 `xmake lua -l` 来列举所有内置的脚本名，例如：

```sh
$ xmake lua -l
scripts:
    cat
    cp
    echo
    versioninfo
    ...
```

并且运行它们：

```sh
$ xmake lua cat ~/file.txt
$ xmake lua echo "hello xmake"
$ xmake lua cp /tmp/file /tmp/file2
$ xmake lua versioninfo
```

### 运行交互命令 (REPL)

有时候在交互模式下，运行命令更加方便测试和验证一些模块和 API，也更加灵活，不需要再去额外写一个脚本文件来加载。

我们先看下，如何进入交互模式：

```sh
# 不带任何参数执行，就可以进入
$ xmake lua
>

# 进行表达式计算
> 1 + 2
3

# 赋值和打印变量值
> a = 1
> a
1

# 多行输入和执行
> for _, v in pairs({1, 2, 3}) do
>> print(v)
>> end
1
2
3
```

我们也能够通过 `import` 来导入扩展模块：

```sh
> task = import("core.project.task")
> task.run("hello")
hello xmake!
```

如果要中途取消多行输入，只需要输入字符：`q` 就行了

```sh
> for _, v in ipairs({1, 2}) do
>> print(v)
>> q             <--  取消多行输入，清空先前的输入数据
> 1 + 2
3
```

## 显示指定信息和列表 {#xmake-show}

### 显示xmake自身和当前项目的基础信息

```sh
$ xmake show
The information of xmake:
    version: 2.3.3+202006011009
    host: macosx/x86_64
    programdir: /Users/ruki/.local/share/xmake
    programfile: /Users/ruki/.local/bin/xmake
    globaldir: /Users/ruki/.xmake
    tmpdir: /var/folders/32/w9cz0y_14hs19lkbs6v6_fm80000gn/T/.xmake501/200603
    workingdir: /Users/ruki/projects/personal/tbox
    packagedir: /Users/ruki/.xmake/packages
    packagedir(cache): /Users/ruki/.xmake/cache/packages/2006

The information of project: tbox
    version: 1.6.5
    plat: macosx
    arch: x86_64
    mode: release
    buildir: build
    configdir: /Users/ruki/projects/personal/tbox/.xmake/macosx/x86_64
    projectdir: /Users/ruki/projects/personal/tbox
    projectfile: /Users/ruki/projects/personal/tbox/xmake.lua
```

### 显示工具链列表

```sh
$ xmake show -l toolchains
xcode         Xcode IDE
vs            VisualStudio IDE
yasm          The Yasm Modular Assembler
clang         A C language family frontend for LLVM
go            Go Programming Language Compiler
dlang         D Programming Language Compiler
sdcc          Small Device C Compiler
cuda          CUDA Toolkit
ndk           Android NDK
rust          Rust Programming Language Compiler
llvm          A collection of modular and reusable compiler and toolchain technologies
cross         Common cross compilation toolchain
nasm          NASM Assembler
gcc           GNU Compiler Collection
mingw         Minimalist GNU for Windows
gnu-rm        GNU Arm Embedded Toolchain
envs          Environment variables toolchain
fasm          Flat Assembler
```

### 显示指定 target 配置信息

我们可以用它来快速追溯定位一些特定配置的位置。

```sh
$ xmake show -t tbox
The information of target(tbox):
    at: /Users/ruki/projects/personal/tbox/src/tbox/xmake.lua
    kind: static
    targetfile: build/macosx/x86_64/release/libtbox.a
    rules:
      -> mode.release -> ./xmake.lua:26
      -> mode.debug -> ./xmake.lua:26
      -> mode.profile -> ./xmake.lua:26
      -> mode.coverage -> ./xmake.lua:26
      -> utils.install.cmake_importfiles -> ./src/tbox/xmake.lua:15
      -> utils.install.pkgconfig_importfiles -> ./src/tbox/xmake.lua:16
    options:
      -> info -> ./src/tbox/xmake.lua:50
      -> float -> ./src/tbox/xmake.lua:50
      -> wchar -> ./src/tbox/xmake.lua:50
      -> exception -> ./src/tbox/xmake.lua:50
      -> force-utf8 -> ./src/tbox/xmake.lua:50
      -> deprecated -> ./src/tbox/xmake.lua:50
      -> xml -> ./src/tbox/xmake.lua:53
      -> zip -> ./src/tbox/xmake.lua:53
      -> hash -> ./src/tbox/xmake.lua:53
      -> regex -> ./src/tbox/xmake.lua:53
      -> coroutine -> ./src/tbox/xmake.lua:53
      -> object -> ./src/tbox/xmake.lua:53
      -> charset -> ./src/tbox/xmake.lua:53
      -> database -> ./src/tbox/xmake.lua:53
    packages:
      -> mbedtls -> ./src/tbox/xmake.lua:43
      -> polarssl -> ./src/tbox/xmake.lua:43
      -> openssl -> ./src/tbox/xmake.lua:43
      -> pcre2 -> ./src/tbox/xmake.lua:43
      -> pcre -> ./src/tbox/xmake.lua:43
      -> zlib -> ./src/tbox/xmake.lua:43
      -> mysql -> ./src/tbox/xmake.lua:43
      -> sqlite3 -> ./src/tbox/xmake.lua:43
    links:
      -> pthread -> option(__keyword_thread_local) -> @programdir/includes/check_csnippets.lua:100
    syslinks:
      -> pthread -> ./xmake.lua:71
      -> dl -> ./xmake.lua:71
      -> m -> ./xmake.lua:71
      -> c -> ./xmake.lua:71
    defines:
      -> __tb_small__ -> ./xmake.lua:42
      -> __tb_prefix__="tbox" -> ./src/tbox/xmake.lua:19
      -> _GNU_SOURCE=1 -> option(__systemv_semget) -> @programdir/includes/check_cfuncs.lua:104
    cxflags:
      -> -Wno-error=deprecated-declarations -> ./xmake.lua:22
      -> -fno-strict-aliasing -> ./xmake.lua:22
      -> -Wno-error=expansion-to-defined -> ./xmake.lua:22
      -> -fno-stack-protector -> ./xmake.lua:51
    frameworks:
      -> CoreFoundation -> ./src/tbox/xmake.lua:38
      -> CoreServices -> ./src/tbox/xmake.lua:38
    mxflags:
      -> -Wno-error=deprecated-declarations -> ./xmake.lua:23
      -> -fno-strict-aliasing -> ./xmake.lua:23
      -> -Wno-error=expansion-to-defined -> ./xmake.lua:23
    includedirs:
      -> src -> ./src/tbox/xmake.lua:26
      -> build/macosx/x86_64/release -> ./src/tbox/xmake.lua:27
    headerfiles:
      -> src/(tbox/**.h)|**/impl/**.h -> ./src/tbox/xmake.lua:30
      -> src/(tbox/prefix/**/prefix.S) -> ./src/tbox/xmake.lua:31
      -> src/(tbox/math/impl/*.h) -> ./src/tbox/xmake.lua:32
      -> src/(tbox/utils/impl/*.h) -> ./src/tbox/xmake.lua:33
      -> build/macosx/x86_64/release/tbox.config.h -> ./src/tbox/xmake.lua:34
    files:
      -> src/tbox/*.c -> ./src/tbox/xmake.lua:56
      -> src/tbox/hash/bkdr.c -> ./src/tbox/xmake.lua:57
      -> src/tbox/hash/fnv32.c -> ./src/tbox/xmake.lua:57
      -> src/tbox/hash/adler32.c -> ./src/tbox/xmake.lua:57
      -> src/tbox/math/**.c -> ./src/tbox/xmake.lua:58
      -> src/tbox/libc/**.c|string/impl/**.c -> ./src/tbox/xmake.lua:59
      -> src/tbox/utils/*.c|option.c -> ./src/tbox/xmake.lua:60
      -> src/tbox/prefix/**.c -> ./src/tbox/xmake.lua:61
      -> src/tbox/memory/**.c -> ./src/tbox/xmake.lua:62
      -> src/tbox/string/**.c -> ./src/tbox/xmake.lua:63
      -> src/tbox/stream/**.c|**/charset.c|**/zip.c -> ./src/tbox/xmake.lua:64
      -> src/tbox/network/**.c|impl/ssl/*.c -> ./src/tbox/xmake.lua:65
      -> src/tbox/algorithm/**.c -> ./src/tbox/xmake.lua:66
      -> src/tbox/container/**.c|element/obj.c -> ./src/tbox/xmake.lua:67
      -> src/tbox/libm/impl/libm.c -> ./src/tbox/xmake.lua:68
      -> src/tbox/libm/idivi8.c -> ./src/tbox/xmake.lua:73
      -> src/tbox/libm/ilog2i.c -> ./src/tbox/xmake.lua:70
      -> src/tbox/libm/isqrti.c -> ./src/tbox/xmake.lua:71
      -> src/tbox/libm/isqrti64.c -> ./src/tbox/xmake.lua:72
      -> src/tbox/platform/*.c|context.c|exception.c -> ./src/tbox/xmake.lua:74
      -> src/tbox/platform/impl/*.c|charset.c|poller_fwatcher.c -> ./src/tbox/xmake.lua:74
      -> src/tbox/libm/*.c -> ./src/tbox/xmake.lua:77
    compiler (cc): /usr/bin/xcrun -sdk macosx clang
      -> -Qunused-arguments -target x86_64-apple-macos12.6 -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX13.0.sdk
    linker (ar): /usr/bin/xcrun -sdk macosx ar
      -> -cr
    compflags (cc):
      -> -Qunused-arguments -target x86_64-apple-macos12.6 -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX13.0.sdk -Wall -Werror -Oz -std=c99 -Isrc -Ibuild/macosx/x86_64/release -D__tb_small__ -D__tb_prefix__=\"tbox\" -D_GNU_SOURCE=1 -framework CoreFoundation -framework CoreServices -Wno-error=deprecated-declarations -fno-strict-aliasing -Wno-error=expansion-to-defined -fno-stack-protector
    linkflags (ar):
      -> -cr
```

#### JSON 输出格式

从 v3.0.5 开始，`xmake show -t target` 支持 JSON 输出格式，使得以编程方式提取目标信息变得更加容易。这个特性实现了与 IDE、构建自动化工具和需要解析 xmake 项目元数据的自定义脚本的无缝集成。

您可以使用 `--json` 获得紧凑输出，或使用 `--pretty-json` 获得格式化输出：

```bash
$ xmake show -t target --json
{"targets":[{"name":"test","kind":"binary","files":["src/main.cpp"],"links":["pthread"],"defines":["DEBUG"]}]}

$ xmake show -t target --pretty-json
{
  "targets": [
    {
      "name": "test",
      "kind": "binary",
      "files": ["src/main.cpp"],
      "links": ["pthread"],
      "defines": ["DEBUG"],
      "includedirs": ["include"],
      "cxxflags": ["-std=c++17"],
      "deps": ["mylib"]
    }
  ]
}
```

您可以提取目标信息用于 IDE 集成或在脚本中使用：

```bash
# 提取目标信息用于 IDE 集成
xmake show -t target --pretty-json > project_info.json

# 在脚本中使用
TARGET_INFO=$(xmake show -t target --json)
TARGET_NAME=$(echo $TARGET_INFO | jq -r '.targets[0].name')
```

这对于以下场景特别有用：

* IDE 集成（VS Code、CLion 等）
* 自动化构建系统和 CI/CD 流水线
* 自定义项目分析工具
* 文档生成

### 显示内置编译模式列表

```sh
$ xmake show -l buildmodes
```

### 显示内置编译规则列表

```sh
$ xmake show -l rules
```

### 显示其他信息

还在完善中，详情见：https://github.com/xmake-io/xmake/issues/798

或者运行：

```sh
$ xmake show --help
```

## 监视文件更新 {#xmake-watch}

v2.7.1 版本新增了 `xmake watch` 插件命令，可以自动监视项目文件更新，然后触发自动构建，或者运行一些自定义命令。

这通常用于个人开发时候，实现快速的实时增量编译，而不需要每次手动执行编译命令，提高开发效率。

### 项目更新后自动构建

默认行为就是监视整个项目根目录，任何文件改动都会触发项目的增量编译。

```sh
$ xmake watch
watching /private/tmp/test/src/** ..
watching /private/tmp/test/* ..
/private/tmp/test/src/main.cpp modified
[ 25%]: cache compiling.release src/main.cpp
[ 50%]: linking.release test
[100%]: build ok!
```

### 监视指定目录

我们也可以监视指定的代码目录，缩小监视范围，提升监视性能。

```sh
$ xmake watch -d src
$ xmake watch -d "src;tests/*"
```

上面的命令，会去递归监视所有子目录，如果想要紧紧监视当前目录下的文件，不进行递归监视，可以使用下面的命令。

```sh
$ xmake watch -p src
$ xmake watch -p "src;tests/*"
```

### 监视并运行指定命令

如果想在自动构建后，还想自动运行构建的程序，我们可以使用自定义的命令集。

```sh
$ xmake watch -c "xmake; xmake run"
```

上面的命令列表是作为字符串传递，这对于复杂命令参数，需要转义比较繁琐不够灵活，那么我们可以使用下面的方式进行任意命令的设置。

```sh
$ xmake watch -- echo hello xmake!
$ xmake watch -- xmake run --help
```

### 监视并运行目标程序

尽管我们可以通过自定义命令来实现目标程序的自动运行，但是我们也提供了更加方便的参数来实现这个行为。

```sh
$ xmake watch -r
$ xmake watch --run
[100%]: build ok!
hello world!
```

### 监视并运行 lua 脚本

我们还可以监视文件更新后，运行指定的 lua 脚本，实现更加灵活复杂的命令定制。

```sh
$ xmake watch -s /tmp/test.lua
```

我们还可以再脚本中获取所有更新的文件路径列表和事件。

```lua
function main(events)
    -- TODO handle events
end
```

## 分析诊断工程配置和代码 {#xmake-check}

### 检测工程配置

#### 默认检测所有 API

```lua
set_lanuages("c91") -- typo
```

```sh
$ xmake check
./xmake.lua:15: warning: unknown language value 'c91', it may be 'c90'
0 notes, 1 warnings, 0 errors
```

默认也可以指定检测特定组：

```sh
$ xmake check api
$ xmake check api.target
```

#### 显示详细输出

这会额外提供 note 级别的检测信息。

```sh
$ xmake check -v
./xmake.lua:15: warning: unknown language value 'cxx91', it may be 'cxx98'
./src/tbox/xmake.lua:43: note: unknown package value 'mbedtls'
./src/tbox/xmake.lua:43: note: unknown package value 'polarssl'
./src/tbox/xmake.lua:43: note: unknown package value 'openssl'
./src/tbox/xmake.lua:43: note: unknown package value 'pcre2'
./src/tbox/xmake.lua:43: note: unknown package value 'pcre'
./src/tbox/xmake.lua:43: note: unknown package value 'zlib'
./src/tbox/xmake.lua:43: note: unknown package value 'mysql'
./src/tbox/xmake.lua:43: note: unknown package value 'sqlite3'
8 notes, 1 warnings, 0 errors
```

#### 检测指定的 API

```sh
$ xmake check api.target.languages
./xmake.lua:15: warning: unknown language value 'cxx91', it may be 'cxx98'
0 notes, 1 warnings, 0 errors
```

#### 检测编译 flags

```sh
$ xmake check
./xmake.lua:10: warning: clang: unknown c compiler flag '-Ox'
0 notes, 1 warnings, 0 errors
```

#### 检测 includedirs

除了 includedirs，还有 linkdirs 等路径都会去检测。

```sh
$ xmake check
./xmake.lua:11: warning: includedir 'xxx' not found
0 notes, 1 warnings, 0 errors
```

### 检测工程代码（clang-tidy）

#### 显示 clang-tidy 检测列表

```sh
$ xmake check clang.tidy --list
Enabled checks:
    clang-analyzer-apiModeling.StdCLibraryFunctions
    clang-analyzer-apiModeling.TrustNonnull
    clang-analyzer-apiModeling.google.GTest
    clang-analyzer-apiModeling.llvm.CastValue
    clang-analyzer-apiModeling.llvm.ReturnValue
    ...
```

#### 检测所有 targets 中的源码

```sh
$ xmake check clang.tidy
1 error generated.
Error while processing /private/tmp/test2/src/main.cpp.
/tmp/test2/src/main.cpp:1:10: error: 'iostr' file not found [clang-diagnostic-error]
#include <iostr>
         ^~~~~~~
Found compiler error(s).
error: execv(/usr/local/opt/llvm/bin/clang-tidy -p compile_commands.json /private/tmp/test2/src
/main.cpp) failed(1)
```

#### 指定检测类型

我们可以在 `--check=` 中指定需要检测的类型，具体用法可以参考 `clang-tidy` 的 `--check=` 参数，完全一致的。

```sh
$ xmake check clang.tidy --checks="*"
6 warnings and 1 error generated.
Error while processing /private/tmp/test2/src/main.cpp.
/tmp/test2/src/main.cpp:1:10: error: 'iostr' file not found [clang-diagnostic-error]
#include <iostr>
         ^~~~~~~
/tmp/test2/src/main.cpp:3:1: warning: do not use namespace using-directives; use using-declarat
ions instead [google-build-using-namespace]
using namespace std;
^
/tmp/test2/src/main.cpp:3:17: warning: declaration must be declared within the '__llvm_libc' na
mespace [llvmlibc-implementation-in-namespace]
using namespace std;
                ^
/tmp/test2/src/main.cpp:5:5: warning: declaration must be declared within the '__llvm_libc' nam
espace [llvmlibc-implementation-in-namespace]
int main(int argc, char **argv) {
    ^
/tmp/test2/src/main.cpp:5:5: warning: use a trailing return type for this function [modernize-u
se-trailing-return-type]
int main(int argc, char **argv) {
~~~ ^
auto                            -> int
/tmp/test2/src/main.cpp:5:14: warning: parameter 'argc' is unused [misc-unused-parameters]
int main(int argc, char **argv) {
             ^~~~
              /*argc*/
/tmp/test2/src/main.cpp:5:27: warning: parameter 'argv' is unused [misc-unused-parameters]
int main(int argc, char **argv) {
                          ^~~~
                           /*argv*/
Found compiler error(s).
error: execv(/usr/local/opt/llvm/bin/clang-tidy --checks=* -p compile_commands.json /private/tm
p/test2/src/main.cpp) failed(1)
```

#### 检测指定 target 的代码

```sh
$ xmake check clang.tidy [targetname]
```

#### 检测给定的源文件列表

```sh
$ xmake check clang.tidy -f src/main.c
$ xmake check clang.tidy -f 'src/*.c:src/**.cpp'
```

#### 设置 .clang-tidy 配置文件

```sh
$ xmake check clang.tidy --configfile=/tmp/.clang-tidy
```

#### 创建 .clang-tidy 配置文件

```sh
$ xmake check clang.tidy --checks="*" --create
$ cat .clang-tidy
