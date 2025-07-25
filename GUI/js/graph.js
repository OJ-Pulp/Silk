import { highlightedNodes, highlightedEdges } from './data.js';
import { updatePopup } from './popup.js';

// Shared state variables for toggling & selection mode
export const graphState = {
  invertNodes: false,
  invertEdges: false,
  isMovingEnabled: true,
  selectionMode: null,
  rectSelectionInProgress: false,
  showIDs: false,
};

// data.js or your graph module
export let uuids = [];
export let adjacencyMatrix = [];
export let nodeWeights = [];


export const selectedNodes = new Set();
export const selectedEdges = new Set();

export function clearSelection() {
  selectedNodes.clear();
  selectedEdges.clear();
}

export async function refreshGrab() {
  try {
    const response = await fetch("http://localhost:8001/get_network");
    if (!response.ok) throw new Error("Failed to fetch network data");

    const data = await response.json();

    // Update exported globals
    uuids = data.node_idxs;
    adjacencyMatrix = data.edge_matrix;
    nodeWeights = data.node_weights;

    console.log("Network data refreshed");
  } catch (error) {
    console.error("Error in refreshGrab:", error);
  }
}


export function renderGraph() {
    if (uuids.length === 0) {
      console.warn("Graph data is empty! Call refreshGrab() first.");
      return;
    }
    // Prepare nodes and links from adjacencyMatrix
    const nodes = uuids.map((id, i) => ({ id, index: i, weight: nodeWeights[i] }));
    const links = [];

    for (let i = 0; i < adjacencyMatrix.length; i++) {
      for (let j = i + 1; j < adjacencyMatrix[i].length; j++) {
        const w_ij = adjacencyMatrix[i][j];
        const w_ji = adjacencyMatrix[j][i];
        if (w_ij > 0 || w_ji > 0) {
          links.push({
            source: i,
            target: j,
            weight_ij: w_ij,
            weight_ji: w_ji,
            weight: Math.max(w_ij, w_ji),
          });
        }
      }
    }

    const svg = d3.select("svg");
    const bounding = svg.node().getBoundingClientRect();
    const width = bounding.width;
    const height = bounding.height;

    const tooltip = d3.select("#tooltip");
    const container = svg.append("g");

    // Force simulation with dynamic edge distance depending on invertEdges
    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links)
        .distance(d => graphState.invertEdges ? 50 + d.weight * 30 : 100 / d.weight)
        .strength(1)
        .id(d => d.index))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .stop();

    for (let i = 0; i < 300; i++) simulation.tick();

    function getNodeRadius(weight) {
      const minRadius = 1;   // ← Change this value to increase/decrease min size
      const maxRadius = 11;  // ← Change this value to increase/decrease max size

      const minWeight = Math.min(...nodes.map(n => n.weight));
      const maxWeight = Math.max(...nodes.map(n => n.weight));

      if (maxWeight === minWeight) return (minRadius + maxRadius) / 2;

      let normalized = (weight - minWeight) / (maxWeight - minWeight);
      if (graphState.invertNodes) normalized = 1 - normalized;

      return minRadius + normalized * (maxRadius - minRadius);
    }


    // Link hitboxes (for easier mouse events)
    const linkHitboxes = container.append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("class", "link-hitbox")
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y)
      .attr("stroke-width", 15)
      .attr("stroke", "transparent")
      .style("pointer-events", "stroke")
      .on("mouseover", (event, d) => {
        let tipText = `Edge (${nodes[d.source.index].id}, ${nodes[d.target.index].id}): ${d.weight_ij}`;
        if (d.weight_ij !== d.weight_ji) {
          tipText += `<br>Edge (${nodes[d.target.index].id}, ${nodes[d.source.index].id}): ${d.weight_ji}`;
        }
        showTooltip(event, tipText);
      })
      .on("mousemove", moveTooltip)
      .on("mouseout", hideTooltip)
      .on("click", (event, d) => {
        toggleEdgeSelection(d);
      });

    // Visible links
    const linkElements = container.append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("class", "link")
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y)
      .attr("stroke-width", d => 2)
      .on("mouseover", (event, d) => {
        let tipText = `Edge (${nodes[d.source.index].id}, ${nodes[d.target.index].id}): ${d.weight_ij}`;
        if (d.weight_ij !== d.weight_ji) {
          tipText += `<br>Edge (${nodes[d.target.index].id}, ${nodes[d.source.index].id}): ${d.weight_ji}`;
        }
        showTooltip(event, tipText);
      })
      .on("mousemove", moveTooltip)
      .on("mouseout", hideTooltip)
      .on("click", (event, d) => {
        toggleEdgeSelection(d);
      });

    // Nodes
    const nodeElements = container.append("g")
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("class", "node")
      .attr("r", d => getNodeRadius(d.weight))
      .attr("cx", d => d.x)
      .attr("cy", d => d.y)
      .on("mouseover", (event, d) => {
        showTooltip(event, `Node ${d.id}: ${d.weight}`);
      })
      .on("mousemove", moveTooltip)
      .on("mouseout", hideTooltip)
      .on("click", (event, d) => {
        const nodeId = d.id;
        if (selectedNodes.has(nodeId)) {
          selectedNodes.delete(nodeId);
        } else {
          selectedNodes.add(nodeId);
        }
        updateSelectionVisuals();
        updatePopupFromSelection();
      });

    // Node labels (for showing IDs)
    const nodeLabels = container.append("g")
      .selectAll("text")
      .data(nodes)
      .join("text")
      .attr("class", "node-label")
      .attr("x", d => d.x + 10) // Offset to avoid overlapping the node
      .attr("y", d => d.y + 4)  // Vertically centered
      .text(d => d.id)
      .style("font-size", "10px")
      .style("fill", "#666")
      .style("pointer-events", "none")
      .style("display", graphState.showIDs ? "block" : "none");


    function toggleEdgeSelection(d) {
      const uuidA = nodes[d.source.index].id;
      const uuidB = nodes[d.target.index].id;
      const forwardKey = `(${uuidA}, ${uuidB})`;
      const backwardKey = `(${uuidB}, ${uuidA})`;

      const forwardSelected = selectedEdges.has(forwardKey);
      const backwardSelected = selectedEdges.has(backwardKey);

      if (d.weight_ij !== d.weight_ji) {
        if (forwardSelected || backwardSelected) {
          selectedEdges.delete(forwardKey);
          selectedEdges.delete(backwardKey);
        } else {
          selectedEdges.add(forwardKey);
          selectedEdges.add(backwardKey);
        }
      } else {
        if (forwardSelected || backwardSelected) {
          selectedEdges.delete(forwardKey);
          selectedEdges.delete(backwardKey);
        } else {
          selectedEdges.add(forwardKey);
        }
      }

      updateSelectionVisuals();
      updatePopupFromSelection();
    }

    function updateSelectionVisuals() {
      nodeElements
        .classed("selected", d => selectedNodes.has(d.id))
        .classed("highlighted", d => highlightedNodes.includes(d.index) && !selectedNodes.has(d.id));

      linkElements
        .classed("selected-edge", d => {
          const uuidA = nodes[d.source.index].id;
          const uuidB = nodes[d.target.index].id;
          const forwardKey = `(${uuidA}, ${uuidB})`;
          const backwardKey = `(${uuidB}, ${uuidA})`;
          return selectedEdges.has(forwardKey) || selectedEdges.has(backwardKey);
        })
        .classed("highlighted", d => {
          const sourceId = nodes[d.source.index].id;
          const targetId = nodes[d.target.index].id;
          const isHighlighted = highlightedEdges.some(edge =>
            (edge.source === sourceId && edge.target === targetId) ||
            (edge.source === targetId && edge.target === sourceId)
          );
          const forwardKey = `(${sourceId}, ${targetId})`;
          const backwardKey = `(${targetId}, ${sourceId})`;
          const isSelected = selectedEdges.has(forwardKey) || selectedEdges.has(backwardKey);
          return isHighlighted && !isSelected;
        });
      
      nodeLabels.style("display", graphState.showIDs ? "block" : "none");
    }

    function updatePopupFromSelection() {
      const selectedItems = [];

      selectedNodes.forEach(id => {
        const node = nodes.find(n => n.id === id);
        if (node) {
          selectedItems.push({
            Type: 'Node',
            ID: node.id,
            Weight: node.weight,
            ...(node.data || {}) // Call backend
          });
        }
      });

      selectedEdges.forEach(key => {
        const [uuidA, uuidB] = key.slice(1, -1).split(', ').map(s => s.trim());
        const i = uuids.indexOf(uuidA);
        const j = uuids.indexOf(uuidB);
        const weight = adjacencyMatrix[i]?.[j];

        if (i !== -1 && j !== -1 && weight > 0) {
          selectedItems.push({
            Type: 'Edge',
            ID: key,
            Weight: weight,
            Data: { "test": "test" }
          });
        }
      });

      if (selectedItems.length === 0) {
        const panel = document.getElementById("popup");
        if (panel) panel.classList.add("hidden");
      } else {
        updatePopup(
          selectedItems,
          selectedNodes,
          selectedEdges,
          updateSelectionVisuals,
          updatePopupFromSelection
        );
      }
    }

    // Rectangle selection state
    graphState.selectionMode = null;
    graphState.rectSelectionInProgress = false;

    const selectionRect = svg.append("rect")
      .attr("class", "selection-rect")
      .attr("fill", "rgba(0, 120, 215, 0.3)")
      .attr("stroke", "rgba(0, 120, 215, 0.8)")
      .attr("stroke-width", 1)
      .style("display", "none");

    let selectionStart = null;

    svg.on("click", (event) => {
      if (graphState.selectionMode !== "rectangle") return;

      const [x, y] = d3.pointer(event, svg.node());

      if (!graphState.rectSelectionInProgress) {
        // First click: begin drawing rectangle
        selectionStart = [x, y];
        graphState.rectSelectionInProgress = true;

        selectionRect
          .attr("x", x)
          .attr("y", y)
          .attr("width", 0)
          .attr("height", 0)
          .style("display", "block");
      } else {
        // Second click: finalize selection rectangle
        const x0 = Math.min(selectionStart[0], x);
        const y0 = Math.min(selectionStart[1], y);
        const x1 = Math.max(selectionStart[0], x);
        const y1 = Math.max(selectionStart[1], y);

        selectionRect.style("display", "none");
        graphState.rectSelectionInProgress = false;
        graphState.selectionMode = null;
        svg.style("cursor", "default");

        // IMPORTANT: Convert rectangle screen coords to graph coords using inverse transform
        const currentTransform = d3.zoomTransform(container.node());
        const p0 = currentTransform.invert([x0, y0]);
        const p1 = currentTransform.invert([x1, y1]);

        const graphX0 = Math.min(p0[0], p1[0]);
        const graphY0 = Math.min(p0[1], p1[1]);
        const graphX1 = Math.max(p0[0], p1[0]);
        const graphY1 = Math.max(p0[1], p1[1]);

        // Select nodes in graph coordinates
        nodes.forEach(node => {
          const cx = node.x;
          const cy = node.y;
          if (cx >= graphX0 && cx <= graphX1 && cy >= graphY0 && cy <= graphY1) {
            selectedNodes.add(node.id);
          }
        });

        // Select edges if both endpoints fall inside selection rectangle
        links.forEach(link => {
          const sx = link.source.x;
          const sy = link.source.y;
          const tx = link.target.x;
          const ty = link.target.y;

          if (
            sx >= graphX0 && sx <= graphX1 && sy >= graphY0 && sy <= graphY1 &&
            tx >= graphX0 && tx <= graphX1 && ty >= graphY0 && ty <= graphY1
          ) {
            const uuidA = nodes[link.source.index].id;
            const uuidB = nodes[link.target.index].id;
            const forwardKey = `(${uuidA}, ${uuidB})`;
            const backwardKey = `(${uuidB}, ${uuidA})`;

            if (link.weight_ij !== link.weight_ji) {
              selectedEdges.add(forwardKey);
              selectedEdges.add(backwardKey);
            } else {
              selectedEdges.add(forwardKey);
            }
          }
        });

        updateSelectionVisuals();
        updatePopupFromSelection();
      }
    });

    // Optional ESC cancel selection
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        graphState.rectSelectionInProgress = false;
        graphState.selectionMode = null;
        selectionRect.style("display", "none");
        svg.style("cursor", "default");
      }
    });

    // Dynamic rectangle resizing during mousemove
    svg.on("mousemove", (event) => {
      if (!graphState.rectSelectionInProgress) return;

      const [x, y] = d3.pointer(event, svg.node());

      const x0 = Math.min(selectionStart[0], x);
      const y0 = Math.min(selectionStart[1], y);
      const width = Math.abs(x - selectionStart[0]);
      const height = Math.abs(y - selectionStart[1]);

      selectionRect
        .attr("x", x0)
        .attr("y", y0)
        .attr("width", width)
        .attr("height", height);
    });

    // Zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.1, 5])
      .on("zoom", event => {
        if (graphState.isMovingEnabled) {
          container.attr("transform", event.transform);
        }
      });

    svg.call(zoom);

    // Tooltip helpers
    function showTooltip(event, html) {
      tooltip
        .html(html)
        .style("opacity", 1)
        .style("left", (event.clientX + 10) + "px")
        .style("top", (event.clientY + 10) + "px");
    }

    function moveTooltip(event) {
      tooltip
        .style("left", (event.clientX + 10) + "px")
        .style("top", (event.clientY + 10) + "px");
    }

    function hideTooltip() {
      tooltip.style("opacity", 0);
    }

    // Initial update of visuals
    updateSelectionVisuals();
}

async function init() {
  await refreshGrab();
  renderGraph();
}

init().catch(error => {
  console.error("Error initializing graph:", error);
});
