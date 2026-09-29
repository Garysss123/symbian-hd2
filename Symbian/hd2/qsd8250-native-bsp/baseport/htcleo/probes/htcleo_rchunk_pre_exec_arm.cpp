/* Iteration 147: ARM-only checkpoint immediately before Exec::ChunkCreate. */

extern "C" void HtcleoRChunkPreExecArmProbe(int aMaxSize)
	{
	asm volatile(
		"mov r6, %0\n"
		".word 0xe7f000f0\n"
		".word 0xe354000d\n"
		".word 0xea000000\n"
		".word 0x48313437\n"
		: : "r" (aMaxSize) : "r6", "cc", "memory");
	}
