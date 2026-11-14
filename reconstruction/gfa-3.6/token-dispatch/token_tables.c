#include "token_tables.h"

#include <string.h>

static uint16_t read_be16(const uint8_t *p)
{
    return (uint16_t)(((uint16_t)p[0] << 8) | p[1]);
}

static uint32_t read_be32(const uint8_t *p)
{
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
           ((uint32_t)p[2] << 8) | (uint32_t)p[3];
}

static bool build_one_map(const uint8_t *text, size_t text_size,
                          size_t start, Gfa36MapKind kind,
                          Gfa36TokenTables *tables)
{
    size_t pos = start;
    const size_t fixed_size = kind == GFA36_MAP_CHARACTER ? 4u : 6u;

    if (start >= text_size)
        return false;

    while (pos < text_size) {
        const uint8_t prefix = text[pos];
        size_t record_size;
        uint16_t key;
        uint16_t relative;

        /* The signed-byte test is BMI on the record length byte. */
        if ((prefix & 0x80u) != 0)
            return true;

        record_size = fixed_size + prefix;
        if (record_size > text_size - pos)
            return false;

        if (kind == GFA36_MAP_CHARACTER) {
            key = text[pos + prefix + 3u];
            if (text[pos + prefix + 2u] != 0)
                key = (uint16_t)(key + 0xE0u);
            if (key >= GFA36_CHARACTER_WORDS)
                return false;
            tables->character[key] =
                (uint16_t)((int32_t)pos - GFA36_STRING_BASE_TEXT);
        } else {
            key = read_be16(text + pos + prefix + 2u);
            if ((key & 1u) != 0 || key / 2u >= GFA36_TOKEN_WORDS)
                return false;
            relative = (uint16_t)((int32_t)pos - GFA36_STRING_BASE_TEXT);
            tables->token[key / 2u] = relative;
        }
        pos += record_size;
    }

    /* A high-bit sentinel is required; falling off TEXT is malformed. */
    return false;
}

static void fill_zero_words(uint16_t *words, size_t count, uint16_t previous)
{
    size_t i;
    for (i = 0; i < count; ++i) {
        if (words[i] == 0)
            words[i] = previous;
        else
            previous = words[i];
    }
}

bool gfa36_build_tables(const uint8_t *text, size_t text_size,
                        uint16_t preceding_character_word,
                        Gfa36TokenTables *tables)
{
    size_t i;
    if (text == NULL || tables == NULL)
        return false;

    memset(tables, 0, sizeof(*tables));
    if (!build_one_map(text, text_size, GFA36_CHARACTER_TABLE_TEXT,
                       GFA36_MAP_CHARACTER, tables) ||
        !build_one_map(text, text_size, GFA36_TOKEN_TABLE_TEXT,
                       GFA36_MAP_TOKEN, tables))
        return false;

    /* TEXT:$1570A..$1571C: slot zero reads workspace:$D2A. */
    fill_zero_words(tables->character, GFA36_CHARACTER_WORDS,
                    preceding_character_word);
    /* Contiguous maps: token slot zero inherits character slot 463. */
    fill_zero_words(tables->token, GFA36_TOKEN_WORDS,
                    tables->character[GFA36_CHARACTER_WORDS - 1u]);

    /* TEXT:$1573A..$1574A, expressed as word slots in the second map. */
    tables->token[0x3C] = 0;
    tables->token[0x3F] = 0;
    for (i = 0x4C; i <= 0x57; ++i)
        tables->token[i] = 0;
    return true;
}

bool gfa36_token_map_lookup(const Gfa36TokenTables *tables,
                            uint16_t token_word, uint16_t *relative_pointer)
{
    const uint16_t byte_offset = (uint16_t)(token_word >> 1);
    const uint16_t slot = (uint16_t)(byte_offset >> 1);
    if (tables == NULL || relative_pointer == NULL ||
        (token_word & 1u) != 0 || (byte_offset & 1u) != 0 ||
        slot >= GFA36_TOKEN_WORDS)
        return false;
    *relative_pointer = tables->token[slot];
    return true;
}

bool gfa36_character_map_lookup(const Gfa36TokenTables *tables,
                                uint8_t character_byte,
                                uint16_t *relative_pointer)
{
    if (tables == NULL || relative_pointer == NULL)
        return false;
    *relative_pointer = tables->character[character_byte];
    return true;
}

bool gfa36_extended_character_map_lookup(const Gfa36TokenTables *tables,
                                         uint8_t character_byte,
                                         uint16_t *relative_pointer)
{
    const uint16_t key = (uint16_t)(character_byte + 0xE0u);
    if (tables == NULL || relative_pointer == NULL ||
        key >= GFA36_CHARACTER_WORDS)
        return false;
    *relative_pointer = tables->character[key];
    return true;
}

bool gfa36_resolve_text_pointer(uint16_t relative_pointer,
                                size_t text_size, size_t *text_offset)
{
    const int32_t resolved = (int32_t)GFA36_STRING_BASE_TEXT +
                             (int16_t)relative_pointer;
    if (text_offset == NULL || resolved < 0 ||
        (size_t)resolved >= text_size)
        return false;
    *text_offset = (size_t)resolved;
    return true;
}

bool gfa36_dispatch_vector_target(const uint8_t *text, size_t text_size,
                                  uint16_t d6_byte_offset,
                                  size_t *target_text_offset)
{
    size_t entry;
    uint32_t target;
    if (text == NULL || target_text_offset == NULL ||
        (d6_byte_offset & 3u) != 0 ||
        d6_byte_offset >= GFA36_DISPATCH_VECTOR_LONGWORDS * 4u)
        return false;
    entry = GFA36_DISPATCH_VECTOR_TEXT + d6_byte_offset;
    if (entry > text_size || text_size - entry < 4u)
        return false;
    target = read_be32(text + entry);
    if (target >= text_size)
        return false;
    *target_text_offset = (size_t)target;
    return true;
}
