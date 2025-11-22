# Makefile for Windows Packet Analyzer
# Supports both MinGW and MSVC compilers

# Detect compiler
# Set COMPILER=msvc for Microsoft Visual C++
# Set COMPILER=mingw for MinGW (default)
COMPILER ?= mingw

# Project name
PROJECT = packet-analyzer
TARGET = $(PROJECT).exe

# Directories
SRC_DIR = src
INC_DIR = include
OBJ_DIR = obj
BIN_DIR = bin

# Npcap/WinPcap SDK path (update this to your Npcap SDK installation)
# Download from: https://npcap.com/#download
NPCAP_SDK = C:/npcap-sdk-1.13

# Source files
SOURCES = $(wildcard $(SRC_DIR)/*.cpp)
OBJECTS = $(patsubst $(SRC_DIR)/%.cpp,$(OBJ_DIR)/%.o,$(SOURCES))

# Compiler flags for MinGW
ifeq ($(COMPILER),mingw)
    CXX = g++
    CXXFLAGS = -std=c++11 -Wall -I$(INC_DIR) -I$(NPCAP_SDK)/Include
    LDFLAGS = -L$(NPCAP_SDK)/Lib/x64 -lwpcap -lws2_32 -liphlpapi -static-libgcc -static-libstdc++
    RM = del /Q
    MKDIR = if not exist $(1) mkdir $(1)
    PATHSEP = \\
else ifeq ($(COMPILER),msvc)
    # MSVC settings
    CXX = cl
    CXXFLAGS = /EHsc /std:c++14 /W3 /I$(INC_DIR) /I$(NPCAP_SDK)/Include
    LDFLAGS = /link /LIBPATH:$(NPCAP_SDK)/Lib/x64 wpcap.lib ws2_32.lib iphlpapi.lib
    RM = del /Q
    MKDIR = if not exist $(1) mkdir $(1)
    PATHSEP = \\
    OBJ_EXT = .obj
endif

# Default target
.PHONY: all
all: dirs $(BIN_DIR)/$(TARGET)

# Create directories
.PHONY: dirs
dirs:
	@if not exist $(OBJ_DIR) mkdir $(OBJ_DIR)
	@if not exist $(BIN_DIR) mkdir $(BIN_DIR)

# MinGW build rules
ifeq ($(COMPILER),mingw)
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(BIN_DIR)/$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $@ $(LDFLAGS)
	@echo Build complete: $(BIN_DIR)/$(TARGET)
endif

# MSVC build rules
ifeq ($(COMPILER),msvc)
$(OBJ_DIR)/%.obj: $(SRC_DIR)/%.cpp
	$(CXX) $(CXXFLAGS) /c $< /Fo$@

$(BIN_DIR)/$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) /Fe$(BIN_DIR)/$(TARGET) $(LDFLAGS)
	@echo Build complete: $(BIN_DIR)/$(TARGET)
endif

# Run the program
.PHONY: run
run: all
	@echo Running $(PROJECT)...
	@$(BIN_DIR)\$(TARGET)

# Clean build files
.PHONY: clean
clean:
	@if exist $(OBJ_DIR) rd /s /q $(OBJ_DIR)
	@if exist $(BIN_DIR) rd /s /q $(BIN_DIR)
	@echo Cleaned build files

# Help
.PHONY: help
help:
	@echo ========================================
	@echo Windows Packet Analyzer - Build System
	@echo ========================================
	@echo.
	@echo Available targets:
	@echo   make all      - Build the project (default)
	@echo   make run      - Build and run the program
	@echo   make clean    - Remove build files
	@echo   make help     - Show this help message
	@echo.
	@echo Compiler options:
	@echo   make COMPILER=mingw   - Use MinGW compiler (default)
	@echo   make COMPILER=msvc    - Use Microsoft Visual C++
	@echo.
	@echo Before building:
	@echo   1. Install Npcap from https://npcap.com
	@echo   2. Download Npcap SDK from https://npcap.com/#download
	@echo   3. Update NPCAP_SDK path in Makefile
	@echo.
	@echo Example:
	@echo   make clean
	@echo   make all
	@echo   make run
	@echo ========================================

# Install instructions
.PHONY: install-info
install-info:
	@echo ========================================
	@echo Installation Requirements
	@echo ========================================
	@echo.
	@echo 1. Install Npcap (required for packet capture):
	@echo    - Download from: https://npcap.com
	@echo    - Install with "WinPcap API-compatible Mode" enabled
	@echo.
	@echo 2. Download Npcap SDK:
	@echo    - Download from: https://npcap.com/#download
	@echo    - Extract to a folder (e.g., C:\npcap-sdk-1.13)
	@echo    - Update NPCAP_SDK path in this Makefile
	@echo.
	@echo 3. Install a C++ compiler:
	@echo    MinGW Option:
	@echo    - Download from: https://www.mingw-w64.org
	@echo    - Or use MSYS2: https://www.msys2.org
	@echo    - Add to PATH environment variable
	@echo.
	@echo    MSVC Option:
	@echo    - Install Visual Studio or Build Tools
	@echo    - Use "Developer Command Prompt for VS"
	@echo.
	@echo 4. Build the project:
	@echo    - Open command prompt
	@echo    - Navigate to project directory
	@echo    - Run: make all
	@echo.
	@echo ========================================
