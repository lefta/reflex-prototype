include stdio

const ref const int print_int(const ref const int i)
{
	printf("%d\n", i)
	return ref i
}

int main()
{
	const int i = 42
	const ref const int j = ref print_int(ref i)
	ref const int k = ref i
	int l = 21
	const ref int m = ref l
	return 0
}