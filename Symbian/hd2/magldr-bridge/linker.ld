OUTPUT_ARCH(arm)
ENTRY(_start)

SECTIONS
{
    . = 0x11808000;
    __image_start = .;

    .text : ALIGN(4)
    {
        KEEP(*(.start))
        *(.text*)
        *(.rodata*)
    }

    .data : ALIGN(4)
    {
        *(.data*)
    }

    .bss (NOLOAD) : ALIGN(8)
    {
        __bss_start = .;
        *(.bss*)
        *(COMMON)
        __bss_end = .;
    }

    __image_end = .;

    /DISCARD/ :
    {
        *(.comment*)
        *(.note*)
        *(.ARM.attributes*)
    }
}

