/* Iteration 144: ARM-only EFILE E32Main checkpoint helper. */

extern "C" void HtcleoGate4ArmProbe()
	{
	asm volatile(
		".word 0xe7f000f0\n"
		".word 0xe354000a\n"
		".word 0xea000000\n"
		".word 0x48313434\n"
		: : : "cc", "memory");
	}
