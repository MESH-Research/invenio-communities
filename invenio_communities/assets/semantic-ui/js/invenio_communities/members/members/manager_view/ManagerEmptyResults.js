import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Header, Icon, Segment, Grid } from "semantic-ui-react";
import { withState } from "react-searchkit";
import { i18next } from "@translations/invenio_communities/i18next";
import { InvitationsContextProvider } from "../../../api/invitations/InvitationsContextProvider";
import { InvitationsMembersModalWithSearchKit } from "../../invitations/invitationsModal/InvitationsMembersModal";

class ManagerEmptyResultsCmp extends Component {
  render() {
    const {
      resetQuery,
      extraContent,
      queryString,
      community,
      groupsEnabled,
      rolesCanInvite,
    } = this.props;

    return (
      <Segment.Group>
        <Segment as={Grid} className="computer only">
          <Grid.Column width="13" />
          <Grid.Column width="3">
            <InvitationsContextProvider community={community}>
              <InvitationsMembersModalWithSearchKit
                rolesCanInvite={rolesCanInvite}
                groupsEnabled={groupsEnabled}
                community={community}
              />
            </InvitationsContextProvider>
          </Grid.Column>
        </Segment>
        <Segment placeholder textAlign="center">
          <Header icon>
            <Icon name="search" />
            {i18next.t("No matching members found.")}
          </Header>
          {queryString && (
            <p>
              <em>
                {i18next.t("Current search")} "{queryString}"
              </em>
            </p>
          )}
          <Button primary onClick={() => resetQuery()}>
            {i18next.t("Clear query")}
          </Button>
          {extraContent}
        </Segment>
      </Segment.Group>
    );
  }
}

ManagerEmptyResultsCmp.propTypes = {
  resetQuery: PropTypes.func.isRequired,
  queryString: PropTypes.string.isRequired,
  rolesCanInvite: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
  groupsEnabled: PropTypes.bool.isRequired,
  extraContent: PropTypes.node,
};

ManagerEmptyResultsCmp.defaultProps = {
  extraContent: null,
};

export const ManagerEmptyResults = withState(ManagerEmptyResultsCmp);
