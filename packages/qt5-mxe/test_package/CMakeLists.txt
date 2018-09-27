cmake_minimum_required(VERSION 3.1 FATAL_ERROR)
project(TestQt)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_SKIP_RPATH OFF)

add_executable(test_qt main.cpp)
target_link_libraries(test_qt ${CONAN_LIBS})
set_target_properties(test_qt PROPERTIES CXX_STANDARD 11 CXX_STANDARD_REQUIRED ON)
