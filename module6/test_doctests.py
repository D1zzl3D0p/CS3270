"""
Doctest runner for pytest.

This module runs all doctests in script.py using pytest.
"""

import doctest
import script


def test_doctests():
    """Run all doctests in script.py"""
    result = doctest.testmod(
        script,
        verbose=False,
        optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
    )
    assert result.failed == 0, f"{result.failed} doctests failed"
