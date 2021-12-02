
BUILD_DIR ?= ./build
SOURCE_DIR ?= ./libcheckers

CXXFLAGS=-std=c++17 -g
LDFLAGS=-g

all: $(BUILD_DIR)/checkers_test

SOURCES=checkers.cc scorer.cc checkers_test.cc scorer_test.cc

OBJECTS=$(addprefix $(BUILD_DIR)/,$(SOURCES:.cc=.o))

$(BUILD_DIR)/%.o: $(SOURCE_DIR)/%.cc $(SOURCE_DIR)/checkers.h
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

$(BUILD_DIR)/checkers_test: $(OBJECTS)
	$(CXX) $(LDFLAGS) -o $@ $^ -lstdc++

clean:
	rm -f $(BUILD_DIR)/checkers_test
	rm -f $(OBJECTS)
	rm -f $(SOURCE_DIR)/py_checkers.cpp
	rm -f $(SOURCE_DIR)/py_checkers.*.so
	rm -f $(SOURCE_DIR)/py_scorer.cpp
	rm -f $(SOURCE_DIR)/py_scorer.*.so