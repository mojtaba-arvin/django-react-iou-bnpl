"""Constants for installment filtering options."""
from django.utils.translation import gettext_lazy as _


class InstallmentStatusFilters:
    """Constants for installment status filtering options."""

    UPCOMING = "upcoming"
    PAST = "past"
    ALL = "all"

    CHOICES = (
        (UPCOMING, _("Upcoming Installments")),
        (PAST, _("Past Installments")),
        (ALL, _("All Installments")),
    )

    VALID_FILTERS = {UPCOMING, PAST}

    @classmethod
    def get_help_text(cls) -> str:
        """Generate dynamic help text listing available filters.

        Returns:
            str: Formatted help text with available filters.
        """
        return _("Filter by status: %(filters)s") % {
            "filters": ", ".join(f"'{choice[0]}'" for choice in cls.CHOICES)
        }
