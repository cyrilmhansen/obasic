/*
 * Historical reconstruction, P3-D/1.
 * Source basis: work/p3c3/target-body-5d04.s, rg-dis 0.11.46,
 * runtime TEXT base observed as $E904.  This is deliberately partial:
 * it models only operations supported by static decoding and the two
 * natural fixtures PRINT "A" and PRINT 1+2.  It is not a named PRINT
 * handler and does not claim to reproduce opaque subroutines.
 */
#include <stdint.h>

typedef struct {
    uint8_t  format_counter_1c2;
    int16_t  format_20f2;
    int16_t  state_20b2;
    uint16_t width_20ae;
    uint16_t column_20b0;
    uint8_t *format_table_7c6;
    uint8_t *scratch_1c6;
} GfaFrame;

typedef enum { OUTPUT_BCONOUT, OUTPUT_FWRITE, OUTPUT_UNKNOWN } OutputRoute;

typedef struct {
    OutputRoute route;
    int16_t device_or_adjusted_format;
    const uint8_t *bytes;
    uint32_t count;
} OutputObservation;

/* Static skeleton of TEXT+$5D04 (runtime $14608 in P3-C3). */
static OutputObservation emit_bytes(GfaFrame *f, const uint8_t *src,
                                    uint32_t count) {
    /* $5E12..$5E24: format_20f2 is read, then a signed adjustment is made. */
    int16_t d6 = f->format_20f2;
    if (d6 >= 0) {
        /* The captured body branches to an opaque continuation at $5F58.
         * Its semantics were not observed in P3-D/1. */
        return (OutputObservation){OUTPUT_UNKNOWN, d6, src, count};
    }
    d6 = (int16_t)(d6 + 6);
    if (d6 < 0) {
        /* Static path at $5E44: GEMDOS Fwrite (#64), handle -3 ($FFFD). */
        return (OutputObservation){OUTPUT_FWRITE, d6, src, count};
    }
    /* $5E24..$5E3C: for each byte, push character, device, BIOS #3. */
    return (OutputObservation){OUTPUT_BCONOUT, d6, src, count};
}

/* Corresponds to $5D04 entry and $5DAE spacing/format preparation. */
static void output_body_skeleton(GfaFrame *f, const uint8_t **token) {
    f->format_counter_1c2 = 0;                 /* CLR.B $1C2(A6) */
    /* $5D0C..$5D4A compares (*token) with 89,70,33,34,87,161..163.
     * The dc.w words and their destinations are not assigned semantics here. */
    while (**token != 70) {
        /* Dedicated branches include the observed space/format paths. */
        ++*token;
        break;                                  /* opaque token cases */
    }

    /* For a known spacing count n, the decoded loop does:
     *   counter += n;
     *   d7 = format_table_7c6[format_20f2];
     *   scan a 13-byte formatting record, with DBRA and tab/backspace rules;
     *   store d7 back to format_table_7c6[format_20f2].
     * The exact record interpretation is not established. */
}

/* Measured natural cases, not a general-language contract. */
static OutputObservation measured_case(GfaFrame *f, const uint8_t *result,
                                       uint32_t count) {
    return emit_bytes(f, result, count);
}

/* Historical effects confirmed by P3-C3 for the two fixtures:
 *   PRINT "A"  -> Bconout(device 2, character $41)
 *   PRINT 1+2  -> Bconout(device 2, character $33)
 * At TEXT+$5E36, D0=$1 and D6=$2; return chain is $11070->$14650->$104F2.
 * The preceding dynamic blocks and the general meaning of fields remain opaque. */
