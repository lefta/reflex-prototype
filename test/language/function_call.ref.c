#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

int32_t* ref_call(void)
{
    return (NULL);
}

int32_t main(int32_t ac, char** av)
{
    puts("Hello, world!\n");
    printf("With some mathematics: 4 * 8 = %d", 4 * 8);
    ref_call();
    return (0);
}
