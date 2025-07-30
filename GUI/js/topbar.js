import { graphState, renderGraph, clearSelection} from './graph.js';
import { highlightedNodes, highlightedEdges } from './data.js';
import { renderSurvey } from './survey.js';
import { clearPopup } from './popup.js';

// --- Dropdown Toggle Logic ---

document.querySelectorAll('.menu-title').forEach(title => {
  title.addEventListener('click', (e) => {
    e.stopPropagation(); // Prevent global click from firing

    const currentMenu = title.parentElement;

    // Close all other menus
    document.querySelectorAll('.menu').forEach(menu => {
      if (menu !== currentMenu) menu.classList.remove('open');
    });

    // Toggle this one
    currentMenu.classList.toggle('open');
  });
});

document.addEventListener('click', (e) => {
  if (!e.target.closest('.menu')) {
    document.querySelectorAll('.menu').forEach(menu => menu.classList.remove('open'));
  }
});

// --- Toolbar Button Handlers ---
const newDatabaseBtn = document.getElementById("newDatabaseBtn"); const openDatabaseBtn = document.getElementById("openDatabaseBtn");
const importDataBtn = document.getElementById("importDataBtn");
const exportDataBtn = document.getElementById("exportDataBtn");


const invertNodesBtn = document.getElementById("invertNodesBtn");
const invertEdgesBtn = document.getElementById("invertEdgesBtn");
const showIDsBtn = document.getElementById("showIDsBtn");
const rectSelectBtn = document.getElementById("rectSelectBtn");
newDatabaseBtn.addEventListener("click", () => {
  fetch("http://localhost:8001/new_database", {
    method: "POST",
  })
    .then(response => response.json())
    .then(data => {
      if (data.status === "cancelled") return;
    })
    .then(() => {
      if (!document.contains(newDatabaseBtn)) return; // skip if cancelled
      clearSelection();
      clearPopup();
      rerenderGraph();
      closeDropdownContaining(newDatabaseBtn);
    })
    .catch(error => {
      console.error("Error creating database:", error);
    });
});


openDatabaseBtn.addEventListener("click", () => {
  fetch("http://localhost:8001/upload_database", {
    method: "POST",
  })
    .then(response => response.json())
    .then(data => {
      if (data.status === "cancelled") return;
    })
    .then(() => {
      if (!document.contains(openDatabaseBtn)) return;
      clearSelection();
      clearPopup();
      rerenderGraph();
      closeDropdownContaining(openDatabaseBtn);
    })
    .catch(error => {
      console.error("Error uploading database:", error);
    });
});

importDataBtn.addEventListener("click", () => {
  fetch("http://localhost:8001/import_data", {
    method: "POST",
  })
    .then(response => response.json())
    .then(data => {
      if (data.status === "cancelled") return;
    })
    .then(() => {
      if (!document.contains(importDataBtn)) return;
      clearSelection();
      clearPopup();
      rerenderGraph();
      closeDropdownContaining(importDataBtn);
    })
    .catch(error => {
      console.error("Error importing data:", error);
    });
});

exportDataBtn.addEventListener("click", () => {
  fetch("http://localhost:8001/export_data", {
    method: "POST",
  })
    .then(response => response.json())
    .then(data => {
      if (data.status === "cancelled") return;
      console.log("Data exported:", data);
      closeDropdownContaining(exportDataBtn);
    })
    .catch(error => {
      console.error("Error exporting data:", error);
    });
});

invertNodesBtn.addEventListener("click", () => {
  graphState.invertNodes = !graphState.invertNodes;
  updateCheckmark(invertNodesBtn, graphState.invertNodes);
  rerenderGraph();
});

invertEdgesBtn.addEventListener("click", () => {
  graphState.invertEdges = !graphState.invertEdges;
  updateCheckmark(invertEdgesBtn, graphState.invertEdges);
  rerenderGraph();
});

showIDsBtn.addEventListener("click", () => {
  graphState.showIDs = !graphState.showIDs;
  updateCheckmark(showIDsBtn, graphState.showIDs);
  rerenderGraph();
});

rectSelectBtn.addEventListener("click", () => {
  graphState.selectionMode = "rectangle";
  document.querySelector("svg").style.cursor = "crosshair";
  closeDropdownContaining(rectSelectBtn);
});

// --- Checkmark Handler (only for invert buttons) ---

function updateCheckmark(button, isChecked) {
  const label = button.getAttribute('data-label') || button.textContent.replace('✔', '').trim();
  button.setAttribute('data-label', label);
  button.innerHTML = isChecked
    ? `${label} <span style="color: grey; float: right;">✔</span>`
    : label;
}

// --- Utility to close dropdown ---

function closeDropdownContaining(button) {
  const menu = button.closest('.menu');
  if (menu) menu.classList.remove('open');
}

// --- Rerender Logic ---

export function rerenderGraph() {
  d3.select("svg").selectAll("*").remove();
  renderGraph(highlightedNodes, highlightedEdges);
}

// --- Survey Form Triggers ---

// These rely on exact button text from your HTML structure.
// You can also add IDs to your dropdown-items to be more precise.

const surveyMap = {
  "edit toolbar": "edit-toolbar",
  "add node": "add-node",
  "add edge": "add-edge",
  "new graph": "new-graph",
  "save graph": "save-graph",
  "delete graph": "delete-graph",
  "display graph": "display-graph",
  "generate graph": "generate-graph",
};

document.querySelectorAll('.dropdown-item').forEach(item => {
  const text = item.textContent.trim().toLowerCase();
  const mode = surveyMap[text];
  if (mode) {
    item.addEventListener("click", () => {
      renderSurvey(mode);
    });
  }
});
