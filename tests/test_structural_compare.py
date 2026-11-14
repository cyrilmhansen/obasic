import unittest

from tools.structural_compare import align_instructions, pair_branches, parse_listing


def listing(rows):
    return "\n".join(f"    {op:<36} ; ${offset:06X} |" for offset, op in rows)


class StructuralCompareTests(unittest.TestCase):
    def test_relocated_branch_and_inserted_instruction_align(self):
        a = parse_listing(listing([
            (0, "MOVEQ #1,D0"), (2, "BRA.S _L0008"),
            (4, "ADDQ.W #1,D1"), (6, "RTS"), (8, "NOP"),
        ]))
        b = parse_listing(listing([
            (0, "MOVEQ #1,D0"), (2, "BRA.S _L000A"),
            (4, "ADDQ.W #1,D1"), (6, "NOP"), (8, "RTS"), (10, "NOP"),
        ]))
        pairs, _ = align_instructions(a, b)
        self.assertEqual(len(pairs), 5)
        flow = pair_branches(a, b, pairs)
        self.assertEqual(flow["matching"], 1)
        self.assertEqual(flow["changed_or_unmapped"], 0)

    def test_constant_change_is_not_normalized_away(self):
        a = parse_listing(listing([(0, "MOVEQ #1,D0"), (2, "RTS")]))
        b = parse_listing(listing([(0, "MOVEQ #2,D0"), (2, "RTS")]))
        pairs, _ = align_instructions(a, b)
        self.assertEqual([(a[i]["offset"], b[j]["offset"]) for i, j in pairs], [(2, 2)])

    def test_control_flow_target_change_is_reported(self):
        a = parse_listing(listing([(0, "BEQ.S _L0004"), (2, "RTS"), (4, "RTS")]))
        b = parse_listing(listing([(0, "BEQ.S _L0002"), (2, "RTS"), (4, "RTS")]))
        pairs, _ = align_instructions(a, b)
        flow = pair_branches(a, b, pairs)
        self.assertEqual(flow["changed_or_unmapped"], 1)

    def test_inserted_instruction_is_unpaired(self):
        a = parse_listing(listing([(0, "MOVEQ #1,D0"), (2, "RTS")]))
        b = parse_listing(listing([(0, "MOVEQ #1,D0"), (2, "NOP"), (4, "RTS")]))
        pairs, _ = align_instructions(a, b)
        self.assertEqual(len(pairs), 2)
        self.assertEqual([x["offset"] for j, x in enumerate(b) if j not in {q[1] for q in pairs}], [2])

    def test_short_rg_dis_offsets_are_parsed(self):
        ins = parse_listing("    RTS ; $0000 |\n    NOP ; $FFFE |")
        self.assertEqual([x["offset"] for x in ins], [0, 0xFFFE])


if __name__ == "__main__":
    unittest.main()
