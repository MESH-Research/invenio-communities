# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Communities Service API config."""

from invenio_records_resources.services.records.config import \
    RecordServiceConfig
from invenio_records_resources.services.records.config import \
    SearchOptions as SearchOptionsBase
from invenio_records_resources.services.records.links import RecordLink, \
    pagination_links
from invenio_records_resources.services.records.search import terms_filter
from invenio_records_resources.services.records.components import \
    MetadataComponent, DataComponent

from invenio_communities.communities.records.api import Community

from .components import PIDComponent
from .permissions import CommunityPermissionPolicy
from .schema import CommunitySchema


class SearchOptions(SearchOptionsBase):
    """Search options."""

    facets_options = dict(
        aggs={
            'type': {
                'terms': {'field': 'metadata.type'},
            },
            'domain': {
                'terms': {'field': 'metadata.domains'},
            },
        },
        post_filters={
            'type': terms_filter('metadata.type'),
            'domain': terms_filter('metadata.domains'),
        }
    )


class CommunityServiceConfig(RecordServiceConfig):
    """Communities service configuration."""

    # Common configuration
    permission_policy_cls = CommunityPermissionPolicy

    # Record specific configuration
    record_cls = Community

    # Search configuration
    search = SearchOptions

    # Service schema
    schema = CommunitySchema

    links_item = {
        "self": RecordLink("{+api}/communities/{id}"),
    }

    links_search = pagination_links("{+api}/communities{?args*}")

    # Service components
    components = [
        DataComponent,
        MetadataComponent,
        PIDComponent
    ]
