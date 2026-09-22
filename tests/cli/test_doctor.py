"""Tests for the check-the-machine command.

The point of a doctor is that somebody reads it, so a check that can only
report one answer is worse than no check. Each of these pins a finding that can
genuinely go either way on a real machine.
"""

import pytest

from maeyomi.cli import doctor
from maeyomi.cli.doctor import Finding, State, machine, package, report, worst


def named(findings: tuple[Finding, ...], name: str) -> Finding:
    return next(finding for finding in findings if finding.name == name)


def test_the_machine_section_says_what_runs_the_program() -> None:
    found = named(machine(), "python")

    assert found.state is State.OK
    assert "3.1" in found.detail


def test_the_machine_section_reports_whether_japanese_can_be_printed() -> None:
    found = named(machine(), "terminal")

    assert found.state in {State.OK, State.WARN}
    assert found.detail


def test_the_machine_section_reports_room_for_the_pdfs() -> None:
    found = named(machine(), "free space")

    assert found.state is State.OK
    assert "GB" in found.detail


def test_the_decoder_is_checked_against_a_known_card() -> None:
    found = named(package(), "decoder")

    assert found.state is State.OK
    assert "4902102072618" in found.detail


def test_a_drawn_barcode_is_decoded_back_rather_than_assumed() -> None:
    found = named(package(), "barcode")

    assert found.state is State.OK
    assert "decoded" in found.detail


def test_the_japanese_font_is_checked_because_every_card_needs_it() -> None:
    found = named(package(), "japanese font")

    assert found.state is State.OK
    assert "HeiseiKakuGo-W5" in found.detail


def test_the_palette_is_rechecked_rather_than_trusted() -> None:
    found = named(package(), "palette")

    assert found.state is State.OK


def test_both_card_lists_are_counted() -> None:
    assert "572" in named(package(), "official cards").detail
    assert named(package(), "supermarket").state is State.OK


def test_the_whole_report_carries_both_sections() -> None:
    names = [finding.name for finding in report()]

    assert "python" in names
    assert "decoder" in names


def test_the_worst_finding_decides_the_verdict() -> None:
    findings = (
        Finding("a", State.OK, ""),
        Finding("b", State.WARN, ""),
        Finding("c", State.OK, ""),
    )

    assert worst(findings) is State.WARN


def test_an_empty_report_is_not_a_pass() -> None:
    with pytest.raises(ValueError, match="nothing was checked"):
        worst(())


def test_a_terminal_that_cannot_print_japanese_is_a_warning_not_a_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(doctor.sys, "stdout", _Terminal("ascii"))

    found = named(machine(), "terminal")

    assert found.state is State.WARN
    assert "ascii" in found.detail


def test_a_terminal_with_no_encoding_at_all_is_reported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(doctor.sys, "stdout", _Terminal(None))

    assert named(machine(), "terminal").state is State.WARN


def test_a_full_disk_is_a_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    def full(_: object) -> _Usage:
        return _Usage(0)

    monkeypatch.setattr(doctor.shutil, "disk_usage", full)

    assert named(machine(), "free space").state is State.WARN


def test_a_decoder_that_reads_a_known_card_wrongly_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(doctor, "KNOWN_DEFENCE", 1)

    found = named(package(), "decoder")

    assert found.state is State.FAIL
    assert "expected" in found.detail


def test_a_symbol_nothing_can_read_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(_: object) -> list[str]:
        message = "no reader available"
        raise OSError(message)

    monkeypatch.setattr(doctor, "decode_pdf", refuse)

    found = named(package(), "barcode")

    assert found.state is State.FAIL
    assert "no reader available" in found.detail


def test_a_symbol_that_reads_back_as_something_else_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def wrong(_: object) -> list[str]:
        return ["0000000000000"]

    monkeypatch.setattr(doctor, "decode_pdf", wrong)

    assert named(package(), "barcode").state is State.FAIL


def test_a_missing_japanese_font_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def latin(_: str) -> str:
        return "Helvetica"

    monkeypatch.setattr(doctor, "font_for", latin)

    found = named(package(), "japanese font")

    assert found.state is State.FAIL
    assert "Helvetica" in found.detail


def test_a_palette_that_stopped_holding_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(doctor, "audit_palette", lambda: ("bird and human print as one grey",))

    found = named(package(), "palette")

    assert found.state is State.FAIL
    assert "one grey" in found.detail


class _Terminal:
    def __init__(self, encoding: str | None) -> None:
        self.encoding = encoding


class _Usage:
    def __init__(self, free: int) -> None:
        self.free = free
