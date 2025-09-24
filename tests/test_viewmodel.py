import pytest

from app.viewmodel import ViewModel
from npc.models import CareerLevel


def test_add_career_str_and_undo(monkeypatch):
    """Verify ViewModel.add_career_str expands via data.loader.get_career_levels,
    records a single history group, and undo_last_career removes those items."""
    vm = ViewModel()

    # fake expansion: get_career_levels("Smith", 2) -> two CareerLevel objects
    def fake_get_career_levels(name, upto):
        return [
            CareerLevel(career=name, level=1, status=""),
            CareerLevel(career=name, level=2, status=""),
        ]

    # ViewModel imports get_career_levels into its module namespace, patch that name
    monkeypatch.setattr("app.viewmodel.get_career_levels", fake_get_career_levels)

    added = vm.add_career_str("Smith:2")
    # Expect two levels added
    assert len(added) == 2
    assert len(vm.career_levels) == 2
    # History should have one group containing the two CareerLevel objects
    assert len(vm._history) == 1
    assert vm._history[0] == added

    removed = vm.undo_last_career()
    assert removed == added
    assert len(vm.career_levels) == 0
    assert vm._history == []
