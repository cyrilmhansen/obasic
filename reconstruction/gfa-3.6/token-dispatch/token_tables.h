#ifndef GFA36_TOKEN_TABLES_H
#define GFA36_TOKEN_TABLES_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/*
 * Reconstructed representation of the two workspace maps built at
 * TEXT:$1569E. Every relative pointer is a 68000 big-endian word in the
 * original; this host model stores the decoded numeric value as uint16_t.
 */
enum {
    GFA36_CHARACTER_TABLE_TEXT = 0x11EDB,
    GFA36_TOKEN_TABLE_TEXT = 0x1111E,
    GFA36_STRING_BASE_TEXT = 0x12CBA,
    GFA36_CHARACTER_WORDS = 0x1D0,
    GFA36_TOKEN_WORDS = 0x200,
    GFA36_CHARACTER_WORKSPACE = 0x0D2C,
    GFA36_TOKEN_WORKSPACE = 0x10CC,
    GFA36_DISPATCH_VECTOR_TEXT = 0x1BF8,
    GFA36_DISPATCH_VECTOR_LONGWORDS = 26
};

typedef struct {
    uint16_t character[GFA36_CHARACTER_WORDS];
    uint16_t token[GFA36_TOKEN_WORDS];
} Gfa36TokenTables;

typedef enum {
    GFA36_MAP_CHARACTER,
    GFA36_MAP_TOKEN
} Gfa36MapKind;

/*
 * Parses the observed length-prefixed records and builds the maps. The
 * preceding_character_word models workspace:$D2A, which startup clears to 0.
 * Returns false on malformed records, out-of-range keys, or odd token offsets.
 */
bool gfa36_build_tables(const uint8_t *text, size_t text_size,
                        uint16_t preceding_character_word,
                        Gfa36TokenTables *tables);

/* token_word is the 16-bit value read by the text renderer. */
bool gfa36_token_map_lookup(const Gfa36TokenTables *tables,
                            uint16_t token_word, uint16_t *relative_pointer);

/* character_byte is the byte after renderer token decoding. */
bool gfa36_character_map_lookup(const Gfa36TokenTables *tables,
                                uint8_t character_byte,
                                uint16_t *relative_pointer);

/* Extended-character path at TEXT:$158D0 adds $E0 before map lookup. */
bool gfa36_extended_character_map_lookup(const Gfa36TokenTables *tables,
                                         uint8_t character_byte,
                                         uint16_t *relative_pointer);

/* Sign-extends the stored word, as ADDA.W does on the 68000. */
bool gfa36_resolve_text_pointer(uint16_t relative_pointer,
                                size_t text_size, size_t *text_offset);

/*
 * The dispatcher at TEXT:$1BE8 indexes the first-level longword vector.
 * Only the 26-entry vector boundary is modeled; its handlers are opaque.
 */
bool gfa36_dispatch_vector_target(const uint8_t *text, size_t text_size,
                                  uint16_t d6_byte_offset,
                                  size_t *target_text_offset);

#endif
