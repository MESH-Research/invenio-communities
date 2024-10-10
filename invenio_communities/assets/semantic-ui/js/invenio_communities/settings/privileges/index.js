import CommunityPrivilegesForm from "./CommunityPriviledgesForm";
import ReactDOM from "react-dom";
import React from "react";
import { OverridableContext, overrideStore } from "react-overridable";

const domContainer = document.getElementById("app");
const formConfig = JSON.parse(domContainer.dataset.formConfig);
const community = JSON.parse(domContainer.dataset.community);
const overriddenComponents = overrideStore.getAll();

ReactDOM.render(
  <OverridableContext.Provider value={overriddenComponents}>
    <CommunityPrivilegesForm formConfig={formConfig} community={community} />
  </OverridableContext.Provider>,
  domContainer
);
