const getTotalTabs = () => {
  const workflowTabs = document.querySelector(".workflow-tabs");
  if (!workflowTabs) return 1; // Default to 1 if no tabs container found

  const tabElements = workflowTabs.querySelectorAll(".workflow-tab");
  return tabElements.length || 1; // Return count of tabs, minimum 1
};

const getLoadingSpinner = (color) => {
  if (!document.querySelector("#spinner-animation")) {
    const style = document.createElement("style");
    style.id = "spinner-animation";
    style.textContent = `
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `;
    document.head.appendChild(style);
  }

  return `
      <span class="loading-spinner" style="
        display: block;
        width: 80px;
        height: 80px;
        border: 3px solid ${color};
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s linear infinite;
      "></span>
    `;
};

const findMenuList = () => {
  // Try different possible menu list IDs
  const possibleMenuLists = [
    "#pv_id_9_0_list",
    "#pv_id_10_0_list",
    ".p-menubar-root-list", // Backup selector
  ];

  for (const selector of possibleMenuLists) {
    const menuList = document.querySelector(selector);
    if (menuList) return menuList;
  }
  return null;
};

const deleteWorkflowFromStorage = (tabIndex) => {
  // Delete the workflow at the current index
  const currentKey = `workflow - ${tabIndex}`;
  localStorage.removeItem(currentKey);

  // Shift down indices for all subsequent workflows
  let nextIndex = tabIndex + 1;
  let nextKey = `workflow - ${nextIndex}`;

  while (localStorage.getItem(nextKey) !== null) {
    // Get the workflow from the next index
    const workflowData = localStorage.getItem(nextKey);
    // Move it to the previous index
    localStorage.setItem(`workflow - ${nextIndex - 1}`, workflowData);
    // Remove the old entry
    localStorage.removeItem(nextKey);

    // Move to next index
    nextIndex++;
    nextKey = `workflow - ${nextIndex}`;
  }
};

export { deleteWorkflowFromStorage, findMenuList, getLoadingSpinner, getTotalTabs };
