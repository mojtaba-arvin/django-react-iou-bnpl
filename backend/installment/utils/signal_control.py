import contextlib
from typing import Generator

from installment.signals import skip_installment_creation, enable_installment_creation


@contextlib.contextmanager
def disable_installment_creation_signal() -> Generator[None, None, None]:
    """
    Context manager to temporarily disable the installment creation signal.

    This is useful in test setups where automatic installment creation via signals
    should be suppressed to keep the test scope focused and deterministic.

    Usage:
        with disable_installment_creation_signal():
            # create test data without triggering installment creation
            ...
    """
    skip_installment_creation()
    try:
        yield
    finally:
        enable_installment_creation()
