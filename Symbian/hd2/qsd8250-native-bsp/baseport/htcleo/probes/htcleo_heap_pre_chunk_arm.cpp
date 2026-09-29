/* Iteration 150: all-ARM EUSER checkpoint before RChunk::Create. */

extern "C" void HtcleoHeapPreChunkArmProbe(int aMaxLength)
	{
	asm volatile(
		"mov r6, %0\n"
		".word 0xe7f000f0\n"
		".word 0xe354000f\n"
		".word 0xea000000\n"
		".word 0x48313530\n"
		: : "r" (aMaxLength) : "r6", "cc", "memory");
	}
