#include <iostream>
#include <windows.h>
#include <winuser.h>

using namespace std;

int main(int argc, char** argv)
{
  cout << "Hello, compiled with GCC " __VERSION__ << endl;
  if (0) {
    // Confirm that we can compile and link with this API from libuser32.a, since that has been a point of failure when cross-compiling Qt (5.11.2)
    ChangeWindowMessageFilterEx(NULL, 0, 0, NULL);
  }
  return 0;
}