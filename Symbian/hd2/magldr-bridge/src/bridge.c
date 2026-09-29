/*
 * Stage-001 MAGLDR bridge diagnostics for HTC HD2.
 *
 * This is deliberately freestanding and contains no Linux or Symbian runtime.
 * It verifies the hand-off before the QSD8250 EKA2 BSP is allowed to run.
 */

typedef unsigned int u32;
typedef unsigned short u16;

#define HTCLEO_MACHINE_TYPE       2524u

#define ATAG_NONE                 0x00000000u
#define ATAG_CORE                 0x54410001u
#define ATAG_INITRD2              0x54420005u

/* WinCE/MAGLDR-preserved scanout buffer used by the proven HD2 early console. */
#define HTC_FB_PHYS               0x03839000u
#define HTC_FB_WIDTH              480u
#define HTC_FB_HEIGHT             800u
#define HTC_FB_STRIDE_BYTES       (HTC_FB_WIDTH * 2u)

/* QSD8x50 MDP physical register block and DMA-P offsets. */
#define HTC_MDP_PHYS              0xaa200000u
#define MDP_DMA_P_START           0x00044u
#define MDP_MDDI_PARAM_WR_SEL     0x00090u
#define MDP_MDDI_PARAM            0x00094u
#define MDP_DMA_P_SIZE            0x90004u
#define MDP_DMA_P_IBUF_ADDR       0x90008u
#define MDP_DMA_P_IBUF_Y_STRIDE   0x9000cu
#define MDP_DMA_P_OUT_XY          0x90010u

#define RGB565(r, g, b) \
    ((u16)((((r) & 31u) << 11) | (((g) & 63u) << 5) | ((b) & 31u)))

#define COLOR_RED                 RGB565(31u, 0u, 0u)
#define COLOR_YELLOW              RGB565(31u, 63u, 0u)
#define COLOR_GREEN               RGB565(0u, 63u, 0u)
#define COLOR_CYAN                RGB565(0u, 63u, 31u)
#define COLOR_MAGENTA             RGB565(31u, 0u, 31u)

struct atag_header {
    u32 size;
    u32 tag;
};

struct atag_initrd2 {
    u32 start;
    u32 size;
};

struct atag {
    struct atag_header hdr;
    union {
        struct atag_initrd2 initrd2;
        u32 words[256];
    } u;
};

struct payload {
    u32 start;
    u32 size;
};

static inline void mmio_write(u32 address, u32 value)
{
    *(volatile u32 *)address = value;
}

static void drain_write_buffer(void)
{
    u32 zero = 0;
    __asm__ volatile("mcr p15, 0, %0, c7, c10, 4" : : "r"(zero) : "memory");
}

static void refresh_lcd(void)
{
    mmio_write(HTC_MDP_PHYS + MDP_DMA_P_SIZE,
               (HTC_FB_HEIGHT << 16) | HTC_FB_WIDTH);
    mmio_write(HTC_MDP_PHYS + MDP_DMA_P_IBUF_ADDR, HTC_FB_PHYS);
    mmio_write(HTC_MDP_PHYS + MDP_DMA_P_IBUF_Y_STRIDE,
               HTC_FB_STRIDE_BYTES);
    mmio_write(HTC_MDP_PHYS + MDP_DMA_P_OUT_XY, 0u);
    mmio_write(HTC_MDP_PHYS + MDP_MDDI_PARAM_WR_SEL, 0u);
    mmio_write(HTC_MDP_PHYS + MDP_MDDI_PARAM, 0x556500c3u);
    drain_write_buffer();
    mmio_write(HTC_MDP_PHYS + MDP_DMA_P_START, 0u);
    drain_write_buffer();
}

static void draw_stage_band(u32 stage, u16 color)
{
    volatile u16 *fb = (volatile u16 *)HTC_FB_PHYS;
    u32 first_row = (stage - 1u) * (HTC_FB_HEIGHT / 4u);
    u32 last_row = first_row + (HTC_FB_HEIGHT / 4u);
    u32 y;
    u32 x;

    for (y = first_row; y < last_row; ++y) {
        for (x = 0; x < HTC_FB_WIDTH; ++x)
            fb[y * HTC_FB_WIDTH + x] = color;
    }
    drain_write_buffer();
    refresh_lcd();
}

static int find_initrd(const struct atag *tag, struct payload *payload)
{
    u32 count;

    if (((u32)tag & 3u) != 0u)
        return 0;

    for (count = 0; count < 128u; ++count) {
        u32 words = tag->hdr.size;

        if (tag->hdr.tag == ATAG_NONE)
            return 0;
        if (words < 2u || words > 258u)
            return 0;
        if (tag->hdr.tag == ATAG_INITRD2) {
            if (words < 4u || tag->u.initrd2.start == 0u ||
                tag->u.initrd2.size < 0x400u)
                return 0;
            payload->start = tag->u.initrd2.start;
            payload->size = tag->u.initrd2.size;
            return 1;
        }
        tag = (const struct atag *)((const u32 *)tag + words);
    }
    return 0;
}

static int looks_like_symbian_rom(const struct payload *payload)
{
    u32 first;

    if (payload->start < 0x11800000u || payload->start >= 0x30000000u)
        return 0;
    if (payload->size < 0x1000u || payload->size > 0x04000000u)
        return 0;

    first = *(volatile const u32 *)payload->start;
    /* A Symbian ROM begins with an ARM B instruction to its reset entry. */
    return (first & 0xff000000u) == 0xea000000u;
}

void hd2_bridge_main(u32 boot_r0, u32 machine_type, const struct atag *tags)
{
    struct payload payload = { 0u, 0u };

    (void)boot_r0;
    draw_stage_band(1u, COLOR_RED);             /* zImage entry reached */

    if (machine_type != HTCLEO_MACHINE_TYPE) {
        draw_stage_band(2u, COLOR_MAGENTA);
        for (;;)
            ;
    }
    draw_stage_band(2u, COLOR_YELLOW);          /* HD2 machine ID valid */

    if (!find_initrd(tags, &payload)) {
        draw_stage_band(3u, COLOR_MAGENTA);
        for (;;)
            ;
    }
    draw_stage_band(3u, COLOR_GREEN);           /* ATAG_INITRD2 valid */

    if (!looks_like_symbian_rom(&payload)) {
        draw_stage_band(4u, COLOR_MAGENTA);
        for (;;)
            ;
    }
    draw_stage_band(4u, COLOR_CYAN);            /* ROM payload recognised */

#ifdef HD2_BRIDGE_JUMP_PAYLOAD
    /* Stage 003: transfer control to a payload linked at its ATAG address. */
    drain_write_buffer();
    ((void (*)(u32, u32, const struct atag *))payload.start)
        (boot_r0, machine_type, tags);

    /* A bring-up payload must never return. */
    draw_stage_band(4u, COLOR_MAGENTA);
#endif

    /* Stage 002 stops here; stage 003 stops here only if payload returned. */
    for (;;)
        ;
}
