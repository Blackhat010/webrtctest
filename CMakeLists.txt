cmake_minimum_required(VERSION 3.18)
project(pi-webrtc)

set(CMAKE_CXX_STANDARD 20)
set(BUILD_TEST "" CACHE STRING "test")

string(TOLOWER "${CMAKE_BUILD_TYPE}" BUILD_TYPE_LOWER)
if(NOT BUILD_TYPE_LOWER OR BUILD_TYPE_LOWER STREQUAL "debug")
    set(CMAKE_BUILD_TYPE Debug CACHE STRING "Choose the type of build (Debug or Release)" FORCE)
    add_compile_options(-g)
    add_definitions(-DDEBUG_MODE)
    find_library(PROFILER_LIB profiler)
    if(PROFILER_LIB)
        message(STATUS "Profiler library found: ${PROFILER_LIB}")
        add_link_options(-lprofiler)
    else()
        message(STATUS "Profiler library not found")
    endif()
else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2")
endif()

set(WEBRTC_INCLUDE_DIR /usr/local/include/webrtc)
set(WEBRTC_LIBRARY
    /usr/local/lib/libwebrtc.a
    avcodec
)

set(THREADS_PREFER_PTHREAD_FLAG ON)

message(STATUS "BUILD_TEST: ${BUILD_TEST}")
message(STATUS "WEBRTC_INCLUDE_DIR: ${WEBRTC_INCLUDE_DIR}")
message(STATUS "WEBRTC_LIBRARY: ${WEBRTC_LIBRARY}")

add_compile_definitions(
    NDEBUG
    WEBRTC_POSIX
    WEBRTC_LINUX
    WEBRTC_USE_H264
    OPENSSL_IS_BORINGSSL
)

add_compile_options(
    -pipe
    -fPIC
)

include_directories(
    ./src
    ${WEBRTC_INCLUDE_DIR}
    ${WEBRTC_INCLUDE_DIR}/third_party/abseil-cpp
    ${WEBRTC_INCLUDE_DIR}/third_party/libyuv/include
    ${WEBRTC_INCLUDE_DIR}/third_party/boringssl/src/include
    ${WEBRTC_INCLUDE_DIR}/tools/json_schema_compiler
)

add_subdirectory(src/capturer)
add_subdirectory(src/codecs/h264)
add_subdirectory(src/codecs/v4l2)
add_subdirectory(src/common)
add_subdirectory(src/recorder)
add_subdirectory(src/rtc)
add_subdirectory(src/signaling)
add_subdirectory(src/track)

if(BUILD_TEST STREQUAL "http_server")
    add_executable(test-http-server test/test_http_server.cpp)
    target_link_libraries(test-http-server
        signaling
    )
elseif(BUILD_TEST STREQUAL "pulseaudio")
    add_executable(test-pulseaudio test/test_pulseaudio.cpp)
    target_link_libraries(test-pulseaudio
        pulse-simple pulse
    )
elseif(BUILD_TEST STREQUAL "recorder")
    add_executable(test-recorder test/test_recorder.cpp)
    target_link_libraries(test-recorder
        recorder
    )
elseif(BUILD_TEST STREQUAL "mqtt")
    add_executable(test-mqtt test/test_mqtt.cpp)
    target_link_libraries(test-mqtt
        signaling
    )
elseif(BUILD_TEST STREQUAL "websocket")
    add_executable(test-websocket test/test_websocket.cpp)
    target_link_libraries(test-websocket
        signaling
    )
elseif(BUILD_TEST STREQUAL "openh264")
    add_executable(test-openh264 test/test_openh264.cpp)
    target_link_libraries(test-openh264
        ${WEBRTC_LIBRARY}
    )
elseif(BUILD_TEST STREQUAL "v4l2_capturer")
    add_executable(test-v4l2-capturer test/test_v4l2_capturer.cpp)
    target_link_libraries(test-v4l2-capturer
        capturer
    )
elseif(BUILD_TEST STREQUAL "v4l2_encoder")
    add_executable(test-v4l2-encoder test/test_v4l2_encoder.cpp)
    target_link_libraries(test-v4l2-encoder
        capturer
    )
elseif(BUILD_TEST STREQUAL "v4l2_decoder")
    add_executable(test-v4l2-decoder test/test_v4l2_decoder.cpp)
    target_link_libraries(test-v4l2-decoder
        capturer
    )
elseif(BUILD_TEST STREQUAL "v4l2_scaler")
    add_executable(test-v4l2-scaler test/test_v4l2_scaler.cpp)
    target_link_libraries(test-v4l2-scaler
        capturer
    )
elseif(BUILD_TEST STREQUAL "libcamera")
    add_executable(test-libcamera test/test_libcamera.cpp)
    target_link_libraries(test-libcamera
        capturer
    )
else()
    add_subdirectory(src)
    add_executable(${PROJECT_NAME} src/main.cpp)
    target_link_libraries(${PROJECT_NAME}
        src
    )
endif()
