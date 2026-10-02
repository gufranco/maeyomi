"""The sizes and spacing a card face is laid out with, in millimetres and points."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CardStyle:
    """Sizes and spacing for one card face, in millimetres and points."""

    padding_mm: float = 4.0
    band_height_mm: float = 11.5
    stat_block_mm: float = 15.0
    min_ability_block_mm: float = 10.5
    block_gap_mm: float = 0.8
    swipe_block_mm: float = 2.8
    title_size_pt: float = 12.0
    name_line_mm: float = 4.5
    band_title_size_pt: float = 9.0
    band_detail_size_pt: float = 7.0
    stat_size_pt: float = 15.0
    stat_label_size_pt: float = 5.5
    stat_icon_mm: float = 4.6
    ability_icon_mm: float = 8.0
    ability_label_size_pt: float = 5.5
    ability_size_pt: float = 6.5
    ability_line_mm: float = 2.75
    swipe_size_pt: float = 5.5
    corner_mm: float = 2.4
    border: bool = True
