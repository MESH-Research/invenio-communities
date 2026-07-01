# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2024 CERN.
# Copyright (C) 2023-2025 Graz University of Technology.
# Copyright (C) 2024 KTH Royal Institute of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community schema."""

import re
from functools import partial
from uuid import UUID

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import CustomFieldsSchema
from invenio_records_resources.services.records.schema import (
    BaseGhostSchema,
    BaseRecordSchema,
)
from invenio_vocabularies.contrib.affiliations.schema import (
    AffiliationRelationSchema as BaseAffiliationRelationSchema,
)
from invenio_vocabularies.contrib.awards.schema import FundingRelationSchema
from invenio_vocabularies.services.schema import (
    VocabularyRelationSchema as VocabularySchema,
)
from marshmallow import (
    EXCLUDE,
    Schema,
    ValidationError,
    fields,
    post_dump,
    post_load,
    pre_load,
    validate,
    validates,
)
from marshmallow_utils.fields import (
    URL,
    ISODateString,
    NestedAttribute,
    SanitizedHTML,
    SanitizedUnicode,
    TrimmedString,
)
from marshmallow_utils.permissions import FieldPermissionsMixin


def _not_blank(**kwargs):
    """Returns a non-blank validation rule."""
    max_ = kwargs.get("max", "")
    return validate.Length(
        error=_(
            "Field cannot be blank or longer than {max_} characters.".format(max_=max_)
        ),
        min=1,
        **kwargs,
    )


def no_longer_than(max, **kwargs):
    """Returns a character limit validation rule."""
    return validate.Length(
        error=_("Field cannot be longer than {max} characters.".format(max=max)),
        max=max,
        **kwargs,
    )


def is_not_uuid(value):
    """Make sure value is not a UUID."""
    try:
        UUID(value)
        raise ValidationError(
            _("The ID must not be an Universally Unique IDentifier (UUID).")
        )
    except (ValueError, TypeError):
        pass


class CommunityAccessSchema(Schema):
    """Community Access Schema."""

    visibility = fields.Str(
        validate=validate.OneOf([
            "public",
            "restricted",
        ])
    )
    members_visibility = fields.Str(
        validate=validate.OneOf([
            "public",
            "restricted",
        ])
    )
    member_policy = fields.Str(
        validate=validate.OneOf([
            "open",
            "closed",
        ])
    )
    record_policy = fields.Str(
        validate=validate.OneOf([
            "open",
            "closed",
            "restricted",
        ])
    )
    record_submission_policy = fields.Str(
        validate=validate.OneOf([
            "open",
            "closed",
            "restricted",
        ])
    )
    review_policy = fields.Str(
        validate=validate.OneOf([
            "open",
            "closed",
            "members",
        ])
    )


# TODO: Probably this should be the default behavior for all relations
class AffiliationRelationSchema(BaseAffiliationRelationSchema):
    """Relaxed affiliation relation schema."""

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE


class CommunityMetadataSchema(Schema):
    """Community metadata schema."""

    title = SanitizedUnicode(required=True, validate=_not_blank(max=250))
    description = SanitizedUnicode(validate=_not_blank(max=250))

    curation_policy = SanitizedHTML(validate=no_longer_than(max=50000))
    page = SanitizedHTML(validate=no_longer_than(max=50000))

    type = fields.Nested(VocabularySchema, metadata={"type": "communitytypes"})
    website = URL(validate=_not_blank())
    funding = fields.List(fields.Nested(FundingRelationSchema))
    organizations = fields.List(fields.Nested(AffiliationRelationSchema))

    # TODO: Add when general vocabularies are ready
    # domains = fields.List(fields.Str())


class AgentSchema(Schema):
    """An agent schema, using a string for the ID to allow the "system" user."""

    user = fields.String(required=True)


class RemovalReasonSchema(VocabularySchema):
    """Schema for the removal reason."""

    id = fields.String(required=True)


class TombstoneSchema(Schema):
    """Schema for the record's tombstone."""

    removal_reason = fields.Nested(RemovalReasonSchema)
    note = SanitizedUnicode()
    removed_by = fields.Nested(AgentSchema, dump_only=True)
    removal_date = ISODateString(dump_only=True)
    citation_text = SanitizedUnicode()
    is_visible = fields.Boolean()


class DeletionStatusSchema(Schema):
    """Schema for the record deletion status."""

    is_deleted = fields.Boolean(dump_only=True)
    status = fields.String(dump_only=True)


_HEX_COLOR_RE = re.compile(r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")
_FONT_FAMILY_RE = re.compile(r"^[\w\s,'\".-]+$")
_FONT_SIZE_RE = re.compile(r"^\d+(\.\d+)?(em|rem|px|%)$")
_FONT_WEIGHT_KEYWORDS = frozenset({"normal", "bold", "bolder", "lighter"})
_NO_CSS_BREAKOUT_RE = re.compile(r"^[^;{}\\]*$")
_FONT_KEYS = frozenset({"family", "weight", "size"})


def _expand_hex(value: str) -> str:
    """Normalize ``#rgb`` to ``#rrggbb``.

    Args:
        value: Hex color string.

    Returns:
        Lowercase ``#rrggbb`` string.
    """
    if len(value) == 4:
        return "#" + "".join(ch * 2 for ch in value[1:])
    return value.lower()


class HexColorField(TrimmedString):
    """Hex color field (``#rgb`` or ``#rrggbb``); normalizes on deserialize."""

    default_error_messages = {
        "invalid": _("Must be a hex color (#RGB or #RRGGBB)."),
    }

    def _deserialize(self, value, attr, data, **kwargs):
        """Validate and normalize a hex color string.

        Returns:
            Normalized hex color, or empty string / ``None`` when unset.
        """
        value = super()._deserialize(value, attr, data, **kwargs)
        if value is None or value == "":
            return value
        if not _HEX_COLOR_RE.match(value):
            raise self.make_error("invalid")
        return _expand_hex(value)


class CommunityThemeStyleSchema(Schema):
    """``theme.style`` — colors, header flags, and optional font dict."""

    class Meta:
        """Schema options."""

        unknown = EXCLUDE

    primaryColor = HexColorField(allow_none=True)
    primaryTextColor = HexColorField(allow_none=True)
    secondaryColor = HexColorField(allow_none=True)
    secondaryTextColor = HexColorField(allow_none=True)
    tertiaryColor = HexColorField(allow_none=True)
    tertiaryTextColor = HexColorField(allow_none=True)
    mainHeaderBackgroundColor = HexColorField(allow_none=True)

    mainHeaderUseLogo = fields.Boolean(allow_none=True)
    mainHeaderUseGradient = fields.Boolean(allow_none=True)

    font = fields.Dict(allow_none=True)

    @validates("font")
    def validate_font(self, value):
        """Validate ``font.family``, ``font.weight``, and ``font.size`` when present.

        Raises:
            ValidationError: When any font sub-key is invalid or unknown.
        """
        if not value:
            return

        unknown = set(value) - _FONT_KEYS
        if unknown:
            raise ValidationError(
                _("Unknown font keys: %(keys)s") % {"keys": ", ".join(sorted(unknown))}
            )

        family = value.get("family")
        if family is not None:
            if not isinstance(family, str):
                raise ValidationError(_("font.family must be a string."))
            family = family.strip()
            if len(family) > 200:
                raise ValidationError(_("font.family is too long."))
            if not _NO_CSS_BREAKOUT_RE.match(family):
                raise ValidationError(_("font.family must not contain ; { } or \\."))
            if not _FONT_FAMILY_RE.match(family):
                raise ValidationError(_("font.family has invalid characters."))

        weight = value.get("weight")
        if weight is not None:
            if isinstance(weight, int):
                if weight < 100 or weight > 900 or weight % 100 != 0:
                    raise ValidationError(
                        _("font.weight must be 100–900 in steps of 100.")
                    )
            elif isinstance(weight, str):
                w = weight.strip()
                if w not in _FONT_WEIGHT_KEYWORDS and not re.fullmatch(r"[1-9]00", w):
                    raise ValidationError(
                        _(
                            "font.weight must be normal, bold, bolder, lighter, "
                            "or 100–900."
                        )
                    )
            else:
                raise ValidationError(_("font.weight must be a string or integer."))

        size = value.get("size")
        if size is not None:
            if not isinstance(size, str):
                raise ValidationError(_("font.size must be a string."))
            size = size.strip()
            if len(size) > 20:
                raise ValidationError(_("font.size is too long."))
            if not _FONT_SIZE_RE.match(size):
                raise ValidationError(
                    _("font.size must be a length (em, rem, px, or %).")
                )


class CommunityThemeSchema(Schema):
    """Community theme schema."""

    style = fields.Nested(CommunityThemeStyleSchema)
    brand = fields.Str()
    enabled = fields.Boolean()
    autogeneratedLogo = fields.Boolean()


class ChildrenSchema(Schema):
    """Children schema."""

    allow = fields.Boolean()


class BaseCommunitySchema(BaseRecordSchema, FieldPermissionsMixin):
    """Base schema for the community metadata."""

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    field_dump_permissions = {
        # hide 'is_verified' behind a permission
        "is_verified": "moderate",
    }

    id = fields.String(dump_only=True)
    slug = SanitizedUnicode(
        required=True,
        validate=[
            _not_blank(max=100),
            validate.Regexp(
                r"^[-\w]+$",
                flags=re.ASCII,
                error=_(
                    "The identifier should contain only letters, numbers, or dashes."
                ),
            ),
            is_not_uuid,
        ],
    )
    metadata = NestedAttribute(CommunityMetadataSchema, required=True)
    access = NestedAttribute(CommunityAccessSchema, required=True)

    custom_fields = NestedAttribute(
        partial(CustomFieldsSchema, fields_var="COMMUNITIES_CUSTOM_FIELDS")
    )

    is_verified = fields.Boolean(dump_only=True)

    theme = fields.Nested(CommunityThemeSchema, allow_none=True)

    tombstone = fields.Nested(TombstoneSchema, dump_only=True)

    deletion_status = fields.Nested(DeletionStatusSchema, dump_only=True)

    children = NestedAttribute(ChildrenSchema)

    @post_dump
    def post_dump(self, data, many, **kwargs):
        """Hide tombstone info if the record isn't deleted and metadata if it is."""
        is_deleted = (data.get("deletion_status") or {}).get("is_deleted", False)
        tombstone_visible = (data.get("tombstone") or {}).get("is_visible", True)

        if data.get("custom_fields") is None:
            data.pop("custom_fields", None)

        if data.get("theme") is None:
            data.pop("theme", None)

        if not is_deleted or not tombstone_visible:
            data.pop("tombstone", None)

        return data


class CommunityParentSchema(BaseCommunitySchema):
    """Community parent schema."""


class CommunitySchema(BaseCommunitySchema):
    """Community schema."""

    parent = NestedAttribute(CommunityParentSchema, dump_only=True, allow_none=True)

    @post_dump
    def post_dump(self, data, many, **kwargs):
        """Hide parent field if it's not present."""
        data = super().post_dump(data, many, **kwargs)
        if data.get("parent") is None:
            data.pop("parent", None)
        return data

    @post_load(pass_original=True)
    def filter_parent_id(self, in_data, original_data, **kwargs):
        """Simply keep the parent id."""
        if "parent" in original_data:
            in_data["parent"] = (
                dict(id=original_data["parent"]["id"])
                if original_data["parent"]
                else None
            )
        return in_data

    @pre_load
    def initialize_custom_fields(self, data, **kwargs):
        """Ensure custom fields are initialized.

        We need to do that so that validation can take place in case a configured
        field is marked as required.
        """
        data.setdefault("custom_fields", {})
        return data

    @post_load
    def lowercase(self, in_data, **kwargs):
        """Ensure slug is lowercase."""
        in_data["slug"] = in_data["slug"].lower()
        return in_data


class CommunityFeaturedSchema(Schema):
    """Community Featured schema."""

    id = fields.Int(dump_only=True)
    start_date = fields.DateTime(
        required=True,
        metadata={
            "title": _("start date"),
            "description": _("Accepted format: YYYY-MM-DD hh:mm"),
            "placeholder": "YYYY-MM-DD hh:mm",
        },
    )


class CommunityGhostSchema(BaseGhostSchema):
    """Community ghost schema."""

    id = SanitizedUnicode(dump_only=True)
    metadata = fields.Constant(
        {
            "title": _("Deleted community"),
            "description": _("The community was deleted."),
        },
        dump_only=True,
    )
