#include <stddef.h>
#include <stdint.h>

void simple_fn(int32_t i)
{
}

void simple_fn_str(char* s)
{
}

int32_t* ref_call(void)
{
    return (NULL);
}

void inc(int32_t* nb)
{
    if (!nb)
    {
        return;
    }
    *nb += 1;
}

void inner_parens(int32_t i)
{
    if (!0)
    {
        i = 1;
        if (!0)
        {
            i = 2;
        }
        if (0)
        {
            i = 2;
        }
        i = 3;
    }
    i = 4;
    if (0)
    {
        i = 5;
    }
}

void func_with_default_params(int32_t par1, int32_t par2)
{
}

void func_with_trailing_comma(int32_t arg)
{
}

void declared_later(void);

int32_t main(int32_t ac, char** av)
{
    simple_fn(42);
    simple_fn(4 * 8);
    simple_fn_str("Hello, world!\n");
    ref_call();
    func_with_default_params(1, 2);
    func_with_default_params(3, 0);
    func_with_trailing_comma(4);
    declared_later();
    return (0);
}

void declared_later(void)
{
}
