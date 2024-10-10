import React from "react";
import ReactDOM from "react-dom";
import { CurationPolicyForm } from "./CurationPolicyForm";
import { OverridableContext, overrideStore } from "react-overridable";

const domContainer = document.getElementById("app");
const community = JSON.parse(domContainer.dataset.community);
const formConfig = JSON.parse(domContainer.dataset.formConfig);
const overriddenComponents = overrideStore.getAll();

ReactDOM.render(
  <OverridableContext.Provider value={overriddenComponents}>
    <CurationPolicyForm community={community} formConfig={formConfig} />
  </OverridableContext.Provider>,
  domContainer
);
