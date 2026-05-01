#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import caption


class CaptionMappingTests(unittest.TestCase):
    def test_tightened_timeline_mapping_skips_removed_gaps(self) -> None:
        windows = [(0.0, 2.0), (4.0, 6.0)]
        self.assertEqual(caption.map_to_tightened(1.0, windows), 1.0)
        self.assertEqual(caption.map_to_tightened(4.5, windows), 2.5)
        self.assertIsNone(caption.map_to_tightened(3.0, windows))

    def test_load_caption_words_without_tighten_maps_to_combined_timeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            transcript = Path(tmp) / "transcript.json"
            transcript.write_text(json.dumps({
                "segments": [
                    {
                        "words": [
                            {"word": "Hello", "start": 0.2, "end": 0.5},
                            {"word": "world", "start": 0.5, "end": 0.9},
                            {"word": "skip", "start": 1.2, "end": 1.4},
                        ],
                    },
                ],
            }))
            cfg = {
                "transcripts": [
                    {
                        "path": str(transcript),
                        "combined_offset": 2.0,
                        "leading_trim": 0.1,
                        "max_original": 1.0,
                    },
                ],
            }

            words, keep_windows = caption.load_caption_words(cfg)

            self.assertEqual(keep_windows, [])
            self.assertEqual([w.text for w in words], ["Hello", "world"])
            self.assertAlmostEqual(words[0].start, 2.1)
            self.assertAlmostEqual(words[0].end, 2.4)
            self.assertAlmostEqual(words[1].start, 2.4)
            self.assertAlmostEqual(words[1].end, 2.8)
            self.assertTrue(words[1].break_after)

    def test_load_caption_words_with_tighten_still_skips_removed_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            transcript = Path(tmp) / "transcript.json"
            transcript.write_text(json.dumps({
                "segments": [
                    {
                        "words": [
                            {"word": "keep", "start": 0.2, "end": 0.6},
                            {"word": "drop", "start": 2.2, "end": 2.6},
                            {"word": "again", "start": 4.2, "end": 4.6},
                        ],
                    },
                ],
            }))
            tighten = Path(tmp) / "tighten.json"
            tighten.write_text(json.dumps({
                "keep": [
                    {"start": 0.0, "end": 1.0},
                    {"start": 4.0, "end": 5.0},
                ],
            }))
            cfg = {
                "tighten_config": str(tighten),
                "transcripts": [{"path": str(transcript)}],
            }

            words, keep_windows = caption.load_caption_words(cfg)

            self.assertEqual(keep_windows, [(0.0, 1.0), (4.0, 5.0)])
            self.assertEqual([w.text for w in words], ["keep", "again"])
            self.assertAlmostEqual(words[0].start, 0.2)
            self.assertAlmostEqual(words[1].start, 1.2)

    def test_phrase_annotation_keeps_emphasis_and_replacements(self) -> None:
        words = [
            caption.Word("day", 0.0, 0.2),
            caption.Word("one", 0.2, 0.4),
            caption.Word("AI,", 0.5, 0.7),
            caption.Word("agent", 0.7, 1.0),
            caption.Word("recorded.", 1.0, 1.2),
        ]
        cfg = {
            "emphasis_words": ["AI agent"],
            "style": {"text_replacements": {"day one": "Day 1", "recorded": "recording"}},
        }

        annotated = caption.annotate_words(words, cfg)

        self.assertEqual([w.display for w in annotated[:2]], ["Day", "1"])
        self.assertEqual(annotated[2].display, "AI")
        self.assertTrue(annotated[2].emphasis)
        self.assertTrue(annotated[3].emphasis)
        self.assertEqual(annotated[2].phrase_id, annotated[3].phrase_id)
        self.assertEqual(annotated[4].display, "recording")

    def test_step_one_replacement_overrides_number_conversion(self) -> None:
        words = [
            caption.Word("Step", 0.0, 0.2),
            caption.Word("one", 0.2, 0.4),
        ]
        cfg = {
            "group_phrases": ["step one"],
            "style": {"text_replacements": {"step one": "Step one"}},
        }

        annotated = caption.annotate_words(words, cfg)

        self.assertEqual([w.display for w in annotated], ["Step", "one"])

    def test_split_numeric_tokens_are_merged_before_paging(self) -> None:
        words = [
            caption.Word("2", 0.0, 0.2),
            caption.Word(",000", 0.2, 0.4, break_after=True),
            caption.Word("comments.", 0.4, 0.7, break_after=True),
        ]

        merged = caption.merge_split_numeric_tokens(words)

        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0].text, "2,000")
        self.assertTrue(merged[0].break_after)

    def test_impact_phrases_become_single_centered_pages(self) -> None:
        words = [
            caption.Word("That's", 0.0, 0.3),
            caption.Word("write,", 0.3, 0.6),
            caption.Word("edit,", 0.9, 1.2),
            caption.Word("publish,", 1.5, 1.9),
        ]
        cfg = {
            "impactPhrases": ["write edit publish"],
            "maxWordsPerPage": 3,
            "anchor": "lower_safe",
            "stylePreset": "founder_pop",
        }

        pages = caption.build_caption_pages(caption.annotate_words(words, cfg), cfg)

        self.assertEqual([p.text for p in pages], ["That's", "write edit publish"])
        self.assertEqual(pages[1].anchor, "mid_safe")
        self.assertEqual(pages[1].style_preset, "impact_word")

    def test_impact_once_and_last_words_limit_repeated_beats(self) -> None:
        words = [
            caption.Word("black", 0.0, 0.2),
            caption.Word("video", 0.2, 0.4),
            caption.Word("black", 0.8, 1.0),
            caption.Word("review", 1.2, 1.4),
            caption.Word("review", 1.8, 2.0),
        ]
        cfg = {
            "impactOnceWords": ["black"],
            "impactLastWords": ["review"],
        }

        annotated = caption.annotate_words(words, cfg)

        self.assertEqual(
            [w.role for w in annotated],
            ["impact", "word", "word", "word", "impact"],
        )

    def test_pages_respect_phrase_boundaries(self) -> None:
        words = [
            caption.Word("I", 0.0, 0.1, display="I"),
            caption.Word("built", 0.1, 0.3, display="built"),
            caption.Word("AI", 0.3, 0.5, display="AI", phrase_id="p1"),
            caption.Word("agent", 0.5, 0.7, display="agent", phrase_id="p1"),
            caption.Word("captions", 0.7, 1.0, display="captions."),
        ]
        cfg = {
            "maxWordsPerPage": 3,
            "maxCharsPerPage": 24,
            "anchor": "lower_safe",
            "stylePreset": "founder_pop",
        }

        pages = caption.build_caption_pages(words, cfg)

        self.assertEqual(len(pages), 2)
        self.assertEqual(pages[1].words[0].display, "AI")
        self.assertEqual(pages[1].words[1].display, "agent")

    def test_raw_punctuation_and_segment_breaks_still_split_pages(self) -> None:
        words = [
            caption.Word("beginning", 0.0, 0.2, display="beginning"),
            caption.Word("to", 0.2, 0.4, display="to"),
            caption.Word("end", 0.4, 0.6, display="end", break_after=True),
            caption.Word("That's", 0.6, 0.8, display="That's"),
            caption.Word("write,", 0.8, 1.0, display="write"),
        ]
        cfg = {
            "maxWordsPerPage": 4,
            "maxCharsPerPage": 40,
            "anchor": "lower_safe",
            "stylePreset": "founder_pop",
        }

        pages = caption.build_caption_pages(words, cfg)

        self.assertEqual([p.text for p in pages], ["beginning to end", "That's write"])

    def test_sentence_boundary_does_not_pull_next_sentence_word(self) -> None:
        words = [
            caption.Word("Day", 0.0, 0.2, display="Day"),
            caption.Word("one.", 0.2, 0.4, display="1"),
            caption.Word("The", 0.4, 0.6, display="The"),
            caption.Word("audio", 0.6, 0.8, display="audio"),
        ]
        cfg = {
            "maxWordsPerPage": 4,
            "minWordsPerPage": 3,
            "maxCharsPerPage": 40,
            "anchor": "lower_safe",
            "stylePreset": "founder_pop",
        }

        pages = caption.build_caption_pages(words, cfg)

        self.assertEqual([p.text for p in pages], ["Day 1", "The audio"])

    def test_hyphenated_split_token_replacement(self) -> None:
        words = [
            caption.Word("on", 0.0, 0.2),
            caption.Word("-screen", 0.2, 0.4),
            caption.Word("visuals", 0.4, 0.6),
        ]
        cfg = {
            "style": {"text_replacements": {"on -screen": "onscreen"}},
        }

        annotated = caption.annotate_words(words, cfg)

        self.assertEqual([w.display for w in annotated], ["onscreen", "", "visuals"])

    def test_omits_configured_standalone_connector_pages(self) -> None:
        words = [
            caption.Word("but", 0.0, 0.2, display="but"),
            caption.Word("the", 0.2, 0.4, display="the"),
            caption.Word("video", 0.4, 0.6, display="video"),
            caption.Word("worked", 0.6, 0.8, display="worked", break_after=True),
        ]
        cfg = {
            "maxWordsPerPage": 1,
            "maxCharsPerPage": 20,
            "omitStandaloneWords": ["but", "the"],
            "anchor": "lower_safe",
            "stylePreset": "founder_pop",
        }

        pages = caption.build_caption_pages(words, cfg)

        self.assertEqual([p.text for p in pages], ["video", "worked"])


if __name__ == "__main__":
    unittest.main()
