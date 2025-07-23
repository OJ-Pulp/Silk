import { graphState, renderGraph, clearSelection } from './graph.js';
import {rerenderGraph} from './topbar.js';
import { clearPopup } from './popup.js';

const modal = document.getElementById("survey-modal");
const formContainer = document.getElementById("survey-form-container");

let currentSurveyMode = null;

export function renderSurvey(mode, data = null) {
  currentSurveyMode = mode;
  modal.classList.remove("hidden");
  formContainer.innerHTML = ""; // clear previous content

  switch (mode) {
    case "edit-toolbar":
      renderEditToolbarForm();
      break;
    case "add-node":
      renderCreateNodeForm();
      break;
    case "add-edge":
      renderCreateEdgeForm();
      break;
    case "new-graph":
      renderCreateGraphForm();
      break;
    case "delete-graph":
      renderDeleteGraphForm();  
      break;
    case "save-graph":
      renderSaveGraphForm();
      break; // Not implemented
    case "edit-entities":
      renderEditEntitiesForm(data);
      break;
    default:
      formContainer.innerHTML = "<p>Unknown mode.</p>";
  }
}

function renderEditEntitiesForm(data) {
  const formContainer = document.getElementById("survey-form-container");
  if (!formContainer) {
    console.error("Form container not found");
    return;
  }

  console.log("Rendering editable Data form with:", data);

  const entityData = data.Data || {};
  let html = "<h4>Edit Entities</h4>";

  for (const [key, value] of Object.entries(entityData)) {
    html += `
      <div class="data-row" id="row-${key}">
        <label for="data-${key}">${key}:</label>
        <input type="text" id="data-${key}" value="${value}">
        <button type="button" class="delete-button" data-key="${key}">×</button>
      </div>
    `;
  }

  formContainer.innerHTML = html;

  // Prevent Enter key from triggering deletes or form submission
  formContainer.querySelectorAll("input").forEach(input => {
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
      }
    });
  });

  // Handle delete buttons
  formContainer.querySelectorAll(".delete-button").forEach(button => {
    button.addEventListener("click", (e) => {
      e.preventDefault();
      const keyToDelete = e.target.getAttribute("data-key");
      const row = document.getElementById(`row-${keyToDelete}`);
      if (row) row.remove();
      delete data.Data[keyToDelete];
    });
  });
}



// Edit Toolbar form
function renderEditToolbarForm() {
  const tools = [
    "Weight Nodes", 
    "Weight Edges", 
    "Traverse Graph", 
    "Cluster Graph", 
    "Compare Graph"
  ];

  formContainer.innerHTML = tools.map(tool => `
    <div class="form-row">
      <label for="${tool.toLowerCase().replace(/ /g, '-')}-methods">${tool}:</label>
      <select id="${tool.toLowerCase().replace(/ /g, '-')}-methods">
        <option>Loading...</option>
      </select>
    </div>
  `).join('');

  tools.forEach(async tool => {
    const toolId = `${tool.toLowerCase().replace(/ /g, '-')}-methods`;
    const select = document.getElementById(toolId);
    const methods = await fetch(`/api/tool-methods?tool=${encodeURIComponent(tool)}`).then(res => res.json());
    select.innerHTML = methods.map(m => `<option value="${m}">${m}</option>`).join('');
  });
}

// Create Node form
function renderCreateNodeForm() {
  formContainer.innerHTML = `
    <label>Node ID:</label>
    <input type="text" id="node-id">
    <div id="node-id-error" style="color: red; font-size: 0.85em; margin-top: 4px;"></div>
    <div style="text-align: center; margin-top: 12px;">
      <button id="add-entity-btn" type="button">Add Entity</button>
    </div>
  `;
  // TODO: Make it so I can put in graph ids and it is a text input seperated by commas
  // And it auto-completes with existing graph ids. If the id does not exist then show read lines under the text
  // and dont allow for the form to be submitted until it is corrected
  // Make entities similar for the key-value pairs but allow for submition even if they keys are 
  // not found within the database
  document.getElementById("add-entity-btn").onclick = () => {
    addKeyValueEntityField("entity-list-container");
  };
}


// Create Edge form
function renderCreateEdgeForm() {
  const nodes = getNodesFromFrontend();

  formContainer.innerHTML = `
    <label>Node #1:</label>
    <select id="node1">${nodes.map(n => `<option>${n}</option>`).join('')}</select>
    <label>Node #2:</label>
    <select id="node2">${nodes.map(n => `<option>${n}</option>`).join('')}</select>
    <div id="edge-id-error" style="color: red; font-size: 0.85em; margin-top: 4px;"></div>
    <div style="text-align: center; margin-top: 12px;">
      <button id="add-edge-entity-btn" type="button">Add Entity</button>
    </div>
  `;

  document.getElementById("add-edge-entity-btn").onclick = () => {
    addKeyValueEntityField("edge-entity-list-container");
  };
}

function addKeyValueEntityField(containerId) {
  let container = document.getElementById(containerId);

  // If the container doesn't exist yet, create and append it
  if (!container) {
    container = document.createElement("div");
    container.id = containerId;
    container.style.marginTop = "12px";
    container.style.minHeight = "40px"; // to avoid layout jump
    document.querySelector("form").appendChild(container); // or another specific parent
  }

  // Prevent adding if last key or value is empty
  const lastKey = container.querySelector(".entity-key:last-of-type");
  const lastVal = container.querySelector(".entity-value:last-of-type");

  if (lastKey && lastVal && (!lastKey.value.trim() || !lastVal.value.trim())) {
    return;
  }

  const wrapper = document.createElement("div");
  wrapper.style.display = "flex";
  wrapper.style.gap = "8px";
  wrapper.style.marginBottom = "8px";
  wrapper.style.alignItems = "flex-end";

  const keyCol = document.createElement("div");
  keyCol.style.flex = "1";
  keyCol.innerHTML = `
    <div style="color: gray; font-size: 0.75em;">Key</div>
    <input type="text" class="entity-key" style="width: 100%;">
  `;

  const valCol = document.createElement("div");
  valCol.style.flex = "1";
  valCol.innerHTML = `
    <div style="color: gray; font-size: 0.75em;">Value</div>
    <input type="text" class="entity-value" style="width: 100%;">
  `;

  const removeBtn = document.createElement("button");
  removeBtn.textContent = "✕";
  removeBtn.type = "button";
  removeBtn.style.border = "none";
  removeBtn.style.background = "none";
  removeBtn.style.color = "red";
  removeBtn.style.cursor = "pointer";
  removeBtn.style.fontSize = "1.1em";
  removeBtn.style.paddingBottom = "6px";
  removeBtn.onclick = () => wrapper.remove();

  wrapper.appendChild(keyCol);
  wrapper.appendChild(valCol);
  wrapper.appendChild(removeBtn);

  container.appendChild(wrapper);
}




// Create Graph form
function renderCreateGraphForm() {
  formContainer.innerHTML = `
    <label>Graph ID:</label>
    <input type="text" id="graph-id">
  `;
}


// Delete Graph form
async function renderDeleteGraphForm() {
  const res = await fetch("http://localhost:8001/get_graphs");
  const data = await res.json();
  const graphs = data.graphs || [];

  if (graphs.length === 0) {
    formContainer.innerHTML = `<p>No graphs available to delete.</p>`;
    return;
  }

  formContainer.innerHTML = `
    <label for="graph-select">Select Graph to Delete:</label>
    <select id="graph-select" style="margin-bottom: 12px;">
      ${graphs.map(g => `<option value="${g}">${g}</option>`).join("")}
    </select>
    <div style="margin-top: 12px;">
      <input type="checkbox" id="confirm-delete-checkbox">
      I understand this will permanently delete the graph.
    </div>
  `;
}

async function renderSaveGraphForm() {
    formContainer.innerHTML = `
    <label>Graph ID:</label>
    <input type="text" id="graph-id">
  `;
}

// Stub for node list, replace with real data
function getNodesFromFrontend() {
  return window.graphNodes || ["NodeA", "NodeB", "NodeC"];
}

// Close modal button
document.getElementById("close-survey").addEventListener("click", () => {
  modal.classList.add("hidden");
});

// Generic Save button handler

// Generic save button
document.getElementById("save-survey").addEventListener("click", async () => {
  if (currentSurveyMode === "delete-graph") {
    const dropdown = document.getElementById("graph-select");
    const checkbox = document.getElementById("confirm-delete-checkbox");

    // Create or reuse error message div
    let errorDiv = document.getElementById("delete-graph-error");
    if (!errorDiv) {
      errorDiv = document.createElement("div");
      errorDiv.id = "delete-graph-error";
      errorDiv.style.color = "red";
      errorDiv.style.fontSize = "0.85em";
      errorDiv.style.marginTop = "8px";
      formContainer.appendChild(errorDiv);
    }
    errorDiv.textContent = "";

    if (!dropdown || !checkbox) {
      errorDiv.textContent = "Unexpected error: form elements not found.";
      return;
    }

    if (!checkbox.checked) {
      errorDiv.textContent = "Please confirm deletion by checking the box.";
      return;
    }

    const selectedGraph = dropdown.value;
    if (!selectedGraph) {
      errorDiv.textContent = "Please select a graph to delete.";
      return;
    }

    try {
      const res = await fetch("http://localhost:8001/delete_graph", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: selectedGraph }),
      });
      if (res.ok) {
        errorDiv.remove(); // Clean up
        clearSelection();
        clearPopup();
        rerenderGraph();
        modal.classList.add("hidden");
      } else {
        errorDiv.textContent = "Failed to delete graph.";
        console.error(await res.text());
      }
    } catch (err) {
      console.error("Error deleting graph:", err);
      errorDiv.textContent = "An unexpected error occurred.";
    }
  } else if (currentSurveyMode == "save-graph") {
    const input = document.getElementById("graph-id");
    const id = input?.value?.trim();

    // Create or reuse error div
    let errorDiv = document.getElementById("graph-id-error");
    if (!errorDiv) {
      errorDiv = document.createElement("div");
      errorDiv.id = "graph-id-error";
      errorDiv.style.color = "red";
      errorDiv.style.fontSize = "0.85em";
      errorDiv.style.marginTop = "4px";
      input.insertAdjacentElement("afterend", errorDiv);
    }

    // Clear any previous error
    errorDiv.textContent = "";

    if (!id) {
      errorDiv.textContent = "Graph ID is required.";
      return;
    }

    try {
      const checkRes = await fetch("http://localhost:8001/check_id", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      const checkJson = await checkRes.json();

      if (checkJson.exists) {
        errorDiv.textContent = "This Graph ID is already taken.";
        return;
      }

      const createRes = await fetch("http://localhost:8001/save_current_graph", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });

      if (createRes.ok) {
        if (errorDiv) errorDiv.remove();
        clearSelection();
        clearPopup();
        rerenderGraph();
        modal.classList.add("hidden");
      } else {
        errorDiv.textContent = "Failed to create graph.";
        console.error(await createRes.text());
      }
    } catch (err) {
      console.error("Error during graph creation:", err);
      errorDiv.textContent = "An unexpected error occurred.";
    }
  } else if (currentSurveyMode === "create-node") {
  const id = document.getElementById("node-id")?.value?.trim();
  const errorDiv = document.getElementById("node-id-error");
  errorDiv.textContent = "";

  if (!id) {
    errorDiv.textContent = "Node ID is required.";
    return;
  }

  try {
    const checkRes = await fetch("http://localhost:8001/check_id", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });
    const checkJson = await checkRes.json();
    if (checkJson.exists) {
      errorDiv.textContent = "This Node ID already exists.";
      return;
    }

    const keyEls = document.querySelectorAll("#entity-list-container .entity-key");
    const valEls = document.querySelectorAll("#entity-list-container .entity-value");

    const entities = {};
    for (let i = 0; i < keyEls.length; i++) {
      const key = keyEls[i].value.trim();
      const value = valEls[i].value.trim();
      if (key) entities[key] = value;
    }

    const res = await fetch("http://localhost:8001/create_node", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, entities }),
    });

    if (res.ok) {
      errorDiv.textContent = "";
      clearSelection();
      clearPopup();
      rerenderGraph();
      modal.classList.add("hidden");
    } else {
      errorDiv.textContent = "Failed to create node.";
    }
  } catch (err) {
    console.error("Node creation error:", err);
    errorDiv.textContent = "Unexpected error.";
    }
  } else if (currentSurveyMode === "create-edge") {
    const node1 = document.getElementById("node1")?.value;
    const node2 = document.getElementById("node2")?.value;
    const errorDiv = document.getElementById("edge-id-error");
    errorDiv.textContent = "";

    if (!node1 || !node2) {
      errorDiv.textContent = "Both nodes must be selected.";
      return;
    }

    try {
      const keyEls = document.querySelectorAll("#edge-entity-list-container .entity-key");
      const valEls = document.querySelectorAll("#edge-entity-list-container .entity-value");

      const entities = {};
      for (let i = 0; i < keyEls.length; i++) {
        const key = keyEls[i].value.trim();
        const value = valEls[i].value.trim();
        if (key) entities[key] = value;
      }

      const res = await fetch("http://localhost:8001/create_edge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ node1, node2, entities }),
      });

      if (res.ok) {
        errorDiv.textContent = "";
        clearSelection();
        clearPopup();
        rerenderGraph();
        modal.classList.add("hidden");
      } else {
        errorDiv.textContent = "Failed to create edge.";
      }
    } catch (err) {
      console.error("Edge creation error:", err);
      errorDiv.textContent = "Unexpected error.";
    }
  } else if (currentSurveyMode === "new-graph") {
    const input = document.getElementById("graph-id");
    const id = input?.value?.trim();

    // Create or reuse error div
    let errorDiv = document.getElementById("graph-id-error");
    if (!errorDiv) {
      errorDiv = document.createElement("div");
      errorDiv.id = "graph-id-error";
      errorDiv.style.color = "red";
      errorDiv.style.fontSize = "0.85em";
      errorDiv.style.marginTop = "4px";
      input.insertAdjacentElement("afterend", errorDiv);
    }

    // Clear any previous error
    errorDiv.textContent = "";

    if (!id) {
      errorDiv.textContent = "Graph ID is required.";
      return;
    }

    try {
      const checkRes = await fetch("http://localhost:8001/check_id", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      const checkJson = await checkRes.json();

      if (checkJson.exists) {
        errorDiv.textContent = "This Graph ID is already taken.";
        return;
      }

      const createRes = await fetch("http://localhost:8001/create_graph", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });

      if (createRes.ok) {
        if (errorDiv) errorDiv.remove();
        clearSelection();
        clearPopup();
        rerenderGraph();
        modal.classList.add("hidden");
      } else {
        errorDiv.textContent = "Failed to create graph.";
        console.error(await createRes.text());
      }
    } catch (err) {
      console.error("Error during graph creation:", err);
      errorDiv.textContent = "An unexpected error occurred.";
    }
  } else {
      modal.classList.add("hidden");
    }
});

