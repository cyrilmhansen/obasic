/*
 * GFA BASIC 3.6 / 3.6TT startup reconstruction
 *
 * Historical, evidence-led pseudocode. This is not a buildable replacement.
 * All addresses below are TEXT offsets unless marked as a workspace offset.
 * See analysis/gfa/STARTUP_36.md for sources, hashes, confidence, and caveats.
 */

/* GEMDOS enters at TEXT:$0000. $0002..$0025 contains an ESC sequence. */
void entry_stub(Basepage *bp)
{
    branch_to(TEXT_0026);
}

void entry_0026(void)
{
    /* The first word is the clear/home prefix used by the output buffer. */
    bss_output_prefix = word_at(TEXT_0002);
    bss_sentinel[0..3] = { 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff };
    jump_to(TEXT_181C);
}

/* Reached directly from $003E. Exact function boundary beyond this path is
 * uncertain; the range runs through command-tail setup at $1974. */
void initialize_and_select_mode(Basepage *bp /* A5 = 4(A7) */)
{
    byte *workspace = align_up_4(address_of_bss_start);  /* A6 */
    clear_bytes(workspace, 0x9000);  /* 0x900 iterations, 16 bytes each */
    global_workspace = workspace;

    /* TEXT:$17B4 has 26 absolute target longwords. */
    for (unsigned i = 0; i != 26; ++i) {
        write_jmp_absolute(workspace + 0xD6 + 6*i,
                           long_at(TEXT_17B4 + 4*i));
    }

    word_at(workspace + 0x21E) = 13;
    initialize_state_flags();             /* implementation not reconstructed */
    opaque_call(TEXT_2B48, 0);             /* D0 = TEXT:$0044, currently zero */

    /* Install a return trampoline and establish the historical stack. */
    set_stack(workspace + 0x6500);
    write_nop_jmp_absolute(workspace, TEXT_7C9C);
    store_long(workspace + 0xCC, bp);
    uint32_t owned_size = (uint32_t)(workspace + 0x8FD4) - (uint32_t)bp;
    store_long(workspace + 0xD0, owned_size);
    gemdos_mshrink(bp, owned_size);         /* TRAP #1, function 74; result ignored */

    rebase_vdi_aes_offsets(workspace);      /* target reached by JSR at $1898 */
    capture_palette();                      /* target reached by JSR at $189E */

    store_long(workspace + 0xC0, xbios_logbase());
    store_word(workspace + 0x206C, xbios_getrez());
    LineAResult la = linea_init();         /* opcode 0; A0/A1/A2 returned */
    store_long(workspace + 0xC4, la.variables);
    store_long(workspace + 0xC8, la.font_table);
    opaque_call(TEXT_ABB4);

    long largest = gemdos_malloc(-1);       /* TRAP #1, function 72 */
    long reserve = largest - 0x4000;
    store_long(workspace + 0x0C, reserve);
    store_long(workspace + 0x08, gemdos_malloc(reserve));
    /* The observed path does not test the returned pointer for NULL. */
    set_stack(workspace + 0x6500);

    setup_runtime_state();                 /* opaque helpers around $1902 */
    initialize_lookup_tables();            /* candidate TEXT:$1569E */
    startup_console_reset();                /* reaches TEXT:$1B16 */
    opaque_call(TEXT_A72A);                 /* vector/keyboard setup candidate */

    /* TOS basepage command tail: length byte at +$80, then bytes. */
    const uint8_t *tail = (const uint8_t *)bp + 0x80;
    uint8_t length = *tail++;
    if (length == 0) {
        interactive_fallback();
        return;
    }

    while (*tail == ' ') ++tail;
    bool option_prefix = (*tail == '-');
    if (option_prefix) ++tail;
    while (*tail == ' ') ++tail;

    /* Historical code copies until NUL. No bound check was observed.
     * The actual tail termination and memory safety are UNMEASURED. */
    uint8_t *dst = workspace + 0x452;
    while (*tail != 0) *dst++ = *tail++;
    push_byte(option_prefix);

    opaque_call(TEXT_A0B0);
    opaque_call(TEXT_A632);
    clear_register_a4();
    opaque_call(TEXT_8D6C);
    if (startup_command_rejected()) interactive_fallback();
    else jump_to(TEXT_1B0C);               /* then reset/dispatcher path */
}

/* Visible state-reset effects; individual helper contracts remain partial. */
void startup_console_reset(void)            /* TEXT:$1B16 */
{
    opaque_call(TEXT_1BA0);
    opaque_call(TEXT_A694);
    opaque_call(TEXT_CF84);
    terminal_write_nul_terminated(buffer_at(TEXT_1B5E));
    opaque_call(TEXT_BA0A);
    opaque_call(TEXT_A4AA);
    opaque_call(TEXT_A0B0);
    clear_observed_startup_globals();
    opaque_call_with_d0(TEXT_79FC, 0);
    opaque_call_with_d0(TEXT_ACA2, 78);     /* AES call; meaning of 78 unknown */
}

/* Candidate helper: uses Line-A opcodes 9 (show mouse) and 10 (hide mouse).
 * Exact visual effect depends on Line-A state and remains partly unmeasured. */
void mouse_guard_helpers(void)             /* TEXT:$1B7C..$1BCF */
{
    if (linea_state_at_workspace_minus_0x256()) linea_call(10);
    /* $1BA0 sets a flag, saves D0-D2/A0-A2 around opcode 9, then restores. */
}

/* Confirmed output primitive: A0 is a NUL-terminated string. */
void terminal_write_nul_terminated(const char *s) /* TEXT:$F914 */
{
    save_registers(D0_D2_A1_A3);
    while (*s != '\0') bios_bconout(2, (unsigned char)*s++);
    restore_registers(D0_D2_A1_A3);
}

/* The visible BIOS helper invokes TRAP #13, function 3, device 2. */
void bios_bconout(int device, unsigned char character);

/* Boundary only: the command/token table selects an indirect handler here. */
void dispatcher_boundary(void)             /* begins TEXT:$1BD6 */
{
    reset_workspace_and_stack(global_workspace);
    /* table selection then JSR (A0) at $1BEC; target set not reconstructed */
    unresolved_indirect_handler_call();
}

/* Explicitly opaque dependencies; names denote addresses, not semantics. */
void opaque_call(unsigned text_offset);
void opaque_call_with_d0(unsigned text_offset, long d0);
void interactive_fallback(void);           /* prompt/parser flow $1978..$1AC4 */
void setup_runtime_state(void);
void initialize_lookup_tables(void);
bool startup_command_rejected(void);
void rebase_vdi_aes_offsets(byte *workspace); /* $A94C adds A6 to 22 pointers */
void capture_palette(void);                 /* $A610 queries 16 colors via XBIOS #7 */
