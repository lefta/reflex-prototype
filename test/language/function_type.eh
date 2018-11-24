void fun1() {}
int fun2(int i) {}
int fun3(int i, int j) {}
ref int[] fun4(ref int[] arr) {}
void fun5(ref char c,) {}

void vfun1(int i, int...)
void vfun2(int[]...)
void vfun3(int i, ...)
void vfun4(...)

int main() {
  func<void()> pfn1 = fun1
  func<int(int)> pfn2 = fun2
  func<int(int, int)> pfn3 = fun3
  func<ref int[](ref int[])> pfn4 = fun4
  func<void(ref char)> pfn5 = fun5

  func<void(int, int...)> vpfn1 = vfun1
  func<void(int[]...)> vpfn2 = vfun2
  func<void(int, ...)> vpfn3 = vfun3
  func<void(...)> vpfn4 = vfun4

  pfn1()
  pfn2(0)
  int i = pfn2(0)
  pfn3(0, 0)
  i = pfn3(0, 0)
  pfn4(null)
  ref int[] rai = pfn4(null)
  int[] ai = pfn4(null)
  str s = "123456"
  pfn5(s[0],)
  return 0
}
