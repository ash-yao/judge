from dmoj.executors.CPP03 import Executor as CPPExecutor


class Executor(CPPExecutor):
    command = 'g++11'
    command_paths = ['g++-5', 'g++-4.9', 'g++-4.8', 'g++']
    std = 'c++11'
    name = 'CPP11'
    test_program = '''
#include <iostream>

int main() {
    auto input = std::cin.rdbuf();
    std::cout << input;
    return 0;
}
'''

    # TODO: These flags should be changed to refer to correct shared library, here we put file in /tmp/cppdynamic/
    # How to build the shared lib and have correct header file in lib direcotry is added in laicode-fe/go/grpc-dmoj/cpplib
    def get_ldflags(self):
        return ["-I", "/tmp/cppdynamic", "-L/tmp/cppdynamic", "-linternal","-include","/tmp/cppdynamic/solution_prologue.inl"]
