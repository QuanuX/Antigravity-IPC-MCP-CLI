cmake_minimum_required(VERSION 3.30)

project(symphony_agent_plugin
  VERSION 0.2.0
  DESCRIPTION "Symphony C++26 MCP and local IPC bridge for Antigravity, Antigravity CLI, and agent hosts"
  LANGUAGES CXX)

set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
option(SYMPHONY_SANITIZERS "Enable AddressSanitizer and UndefinedBehaviorSanitizer" OFF)

find_package(Threads REQUIRED)
if(NOT APPLE)
  find_package(OpenSSL 3 REQUIRED COMPONENTS Crypto)
endif()

add_library(symphony_transport STATIC
  src/transport.cpp)

target_include_directories(symphony_transport
  PUBLIC
    "${CMAKE_CURRENT_SOURCE_DIR}/include"
    "${CMAKE_CURRENT_SOURCE_DIR}/third_party")

target_compile_options(symphony_transport
  PUBLIC
    -std=c++2c
    -Wall
    -Wextra
    -Wpedantic
    -Werror)

target_link_libraries(symphony_transport PUBLIC Threads::Threads)
if(NOT APPLE)
  target_link_libraries(symphony_transport PUBLIC OpenSSL::Crypto)
endif()

set(plugin_manifest "${CMAKE_CURRENT_SOURCE_DIR}/plugin.json")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${plugin_manifest}")
file(READ "${plugin_manifest}" plugin_metadata)
string(JSON plugin_version GET "${plugin_metadata}" version)
add_executable(symphony-mcp src/main.cpp)
target_compile_definitions(symphony-mcp PRIVATE SYMPHONY_MCP_VERSION="${plugin_version}")
target_link_libraries(symphony-mcp PRIVATE symphony_transport)
install(TARGETS symphony-mcp RUNTIME DESTINATION bin)

if(SYMPHONY_SANITIZERS)
  foreach(target symphony_transport symphony-mcp)
    target_compile_options(${target} PUBLIC -fsanitize=address,undefined -fno-omit-frame-pointer)
    target_link_options(${target} PUBLIC -fsanitize=address,undefined)
  endforeach()
endif()

include(CTest)
if(BUILD_TESTING)
  find_package(Python3 REQUIRED COMPONENTS Interpreter)

  add_executable(transport_test tests/transport_test.cpp)
  target_link_libraries(transport_test PRIVATE symphony_transport)
  add_test(NAME transport COMMAND transport_test)

  add_executable(hash_test tests/hash_test.cpp)
  target_link_libraries(hash_test PRIVATE symphony_transport)
  add_test(NAME bounded-hashing COMMAND hash_test)

  add_test(
    NAME mcp-integration
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_mcp.py" "$<TARGET_FILE:symphony-mcp>")

  add_test(
    NAME public-operation-tools
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_public_tools.py" "$<TARGET_FILE:symphony-mcp>")

  add_test(
    NAME client-adapters
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_adapters.py" "$<TARGET_FILE:symphony-mcp>")

  add_test(
    NAME qualification-report
    COMMAND "${Python3_EXECUTABLE}" -m unittest discover -s "${CMAKE_CURRENT_SOURCE_DIR}/tests" -p "test_qualification.py")

  add_test(
    NAME mcpb-packaging
    COMMAND "${Python3_EXECUTABLE}" -m unittest discover -s "${CMAKE_CURRENT_SOURCE_DIR}/tests" -p "test_mcpb.py")
endif()
