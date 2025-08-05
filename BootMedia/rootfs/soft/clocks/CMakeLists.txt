cmake_minimum_required(VERSION 2.8)

	project(clock_sync)
	set(CMAKE_C_COMPILER /usr/bin/gcc)
	set(CMAKE_BUILD_TYPE Debug)

	set(CMAKE_C_FLAGS "-lrt")
	set(CMAKE_CXX_FLAGS "-lrt")
	set(SRCS "clock_sync.c" "toml.c" "i2c-chip.c" "semaphore.c")

	set(HDRS_320_LHC "Si5344-RevD-APLSMHQ-Registers.h" "toml.h" "i2c-chip.h" "semaphore.h")
	add_executable(clock_sync_320M_LHC ${SRCS} ${HDRS_320_LHC})
	set_target_properties(clock_sync_320M_LHC PROPERTIES COMPILE_FLAGS "-DF320p64_LHC")
	
