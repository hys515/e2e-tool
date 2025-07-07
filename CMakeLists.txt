cmake_minimum_required(VERSION 3.10)
project(e2e-tool C)

# 设置 C 标准
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# 设置输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# 查找 GmSSL
find_path(GMSSL_INCLUDE_DIR gmssl/sm2.h
    PATHS
    /usr/local/include
    /usr/include
    "C:/Program Files/GmSSL/include"
    "C:/GmSSL/include"
)

find_library(GMSSL_LIBRARY
    NAMES gmssl libgmssl
    PATHS
    /usr/local/lib
    /usr/lib
    "C:/Program Files/GmSSL/lib"
    "C:/GmSSL/lib"
)

if(NOT GMSSL_INCLUDE_DIR)
    message(FATAL_ERROR "GmSSL include directory not found. Please install GmSSL first.")
endif()

if(NOT GMSSL_LIBRARY)
    message(FATAL_ERROR "GmSSL library not found. Please install GmSSL first.")
endif()

message(STATUS "Found GmSSL include: ${GMSSL_INCLUDE_DIR}")
message(STATUS "Found GmSSL library: ${GMSSL_LIBRARY}")

# 包含目录
include_directories(${CMAKE_SOURCE_DIR}/include ${GMSSL_INCLUDE_DIR})

# 源文件
set(MAIN_SOURCES
    cli/main.c
    src/sm2_ecdh.c
)

set(TEST_SOURCES
    test/test_sm2_ecdh.c
    src/sm2_ecdh.c
)

# 主程序
add_executable(e2e-tool ${MAIN_SOURCES})
target_link_libraries(e2e-tool ${GMSSL_LIBRARY})

# 测试程序
add_executable(test_sm2_ecdh ${TEST_SOURCES})
target_link_libraries(test_sm2_ecdh ${GMSSL_LIBRARY})

# 平台特定设置
if(WIN32)
    # Windows 特定设置
    target_link_libraries(e2e-tool ws2_32)
    target_link_libraries(test_sm2_ecdh ws2_32)
    
    # MSVC 特定设置
    if(MSVC)
        target_compile_options(e2e-tool PRIVATE /utf-8)
        target_compile_options(test_sm2_ecdh PRIVATE /utf-8)
        add_definitions(-D_CRT_SECURE_NO_WARNINGS)
    endif()
elseif(APPLE)
    # macOS 特定设置
    target_link_libraries(e2e-tool "-framework Security")
    target_link_libraries(test_sm2_ecdh "-framework Security")
endif()

# 安装规则
install(TARGETS e2e-tool
    RUNTIME DESTINATION bin
)

# 测试
enable_testing()
add_test(NAME test_sm2_ecdh COMMAND test_sm2_ecdh) 