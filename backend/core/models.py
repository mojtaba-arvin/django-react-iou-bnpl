from django.db import models
from django.utils.translation import gettext_lazy as _


class AbstractTimestampedModel(models.Model):
    """Abstract base model that adds created/updated timestamps.

    Attributes:
        created_at (datetime): When this record was first created.
        updated_at (datetime): When this record was last modified.
    """

    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('Timestamp when this record was created.'),
        db_index=True
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('Timestamp when this record was last updated.'),
    )

    class Meta:
        abstract = True
        get_latest_by = 'created_at'
