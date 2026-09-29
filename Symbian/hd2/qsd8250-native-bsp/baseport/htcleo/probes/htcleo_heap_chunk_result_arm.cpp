/* Iteration 145: ARM-only RChunk::Create return-code checkpoint helper. */

extern "C" void HtcleoHeapChunkResultArmProbe(int aResult)
	{
	asm volatile(
		"mov r6, %0\n"
		".word 0xe7f000f0\n"
		".word 0xe354000b\n"
		".word 0xea000000\n"
		".word 0x48313435\n"
		: : "r" (aResult) : "r6", "cc", "memory");
	}
