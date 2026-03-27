import {
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
  type Connection,
  type Edge,
  type EdgeChange,
  type Node,
  type NodeChange,
  type OnConnect,
  type OnEdgesChange,
  type OnNodesChange,
  type XYPosition,
} from "@xyflow/react";
import { create } from "zustand";

import type { Canvas } from "@/types/workflow";
import type { NodeTypeSchema } from "@/types/nodes";
import type { WorkflowResponse } from "@/types/workflow";

export type FlowForgeNodeData = {
  kind: string;
  label: string;
  config: Record<string, unknown>;
};

export type FlowForgeRfNode = Node<FlowForgeNodeData, "flowforge">;

function defaultConfig(spec: NodeTypeSchema | undefined): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const f of spec?.config_fields ?? []) {
    if (f.default !== undefined && f.default !== null) {
      out[f.name] = f.default;
    }
  }
  return out;
}

function apiCanvasToFlow(
  canvas: Canvas,
): { nodes: FlowForgeRfNode[]; edges: Edge[] } {
  const nodes: FlowForgeRfNode[] = canvas.nodes.map((n) => ({
    id: n.id,
    type: "flowforge",
    position: n.position,
    data: {
      kind: n.type,
      label: n.label,
      config: n.config ?? {},
    },
  }));
  const edges: Edge[] = canvas.edges.map((e, i) => ({
    id: `e-${e.source}-${e.target}-${i}`,
    source: e.source,
    target: e.target,
    type: "smoothstep",
  }));
  return { nodes, edges };
}

interface WorkflowStore {
  workflow: WorkflowResponse | null;
  nodes: FlowForgeRfNode[];
  edges: Edge[];
  nodeTypes: NodeTypeSchema[];
  selectedNodeId: string | null;

  setWorkflow: (workflow: WorkflowResponse) => void;
  setNodes: (nodes: FlowForgeRfNode[]) => void;
  setEdges: (edges: Edge[]) => void;
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  addNode: (typeKey: string, position: XYPosition) => void;
  updateNodeConfig: (nodeId: string, config: Record<string, unknown>) => void;
  updateNodeLabel: (nodeId: string, label: string) => void;
  selectNode: (nodeId: string | null) => void;
  setNodeTypes: (types: NodeTypeSchema[]) => void;
  loadCanvasFromWorkflow: (w: WorkflowResponse) => void;
  getCanvasPayload: () => Canvas;
  reset: () => void;
}

export const useWorkflowStore = create<WorkflowStore>((set, get) => ({
  workflow: null,
  nodes: [],
  edges: [],
  nodeTypes: [],
  selectedNodeId: null,

  setWorkflow: (workflow) => set({ workflow }),
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),

  onNodesChange: (changes: NodeChange[]) => {
    set((s) => ({
      nodes: applyNodeChanges(changes, s.nodes) as FlowForgeRfNode[],
    }));
  },

  onEdgesChange: (changes: EdgeChange[]) => {
    set((s) => ({
      edges: applyEdgeChanges(changes, s.edges),
    }));
  },

  onConnect: (connection: Connection) => {
    set((s) => ({
      edges: addEdge(
        { ...connection, type: "smoothstep" },
        s.edges,
      ),
    }));
  },

  addNode: (typeKey, position) => {
    const spec = get().nodeTypes.find((t) => t.type === typeKey);
    const label = spec?.label ?? typeKey;
    const config = defaultConfig(spec);
    const id = crypto.randomUUID();
    const node: FlowForgeRfNode = {
      id,
      type: "flowforge",
      position,
      data: { kind: typeKey, label, config },
    };
    set((s) => ({ nodes: [...s.nodes, node] }));
  },

  updateNodeConfig: (nodeId, config) => {
    set((s) => ({
      nodes: s.nodes.map((n) =>
        n.id === nodeId
          ? {
              ...n,
              data: {
                ...n.data,
                config: { ...n.data.config, ...config },
              },
            }
          : n,
      ),
    }));
  },

  updateNodeLabel: (nodeId, label) => {
    set((s) => ({
      nodes: s.nodes.map((n) =>
        n.id === nodeId ? { ...n, data: { ...n.data, label } } : n,
      ),
    }));
  },

  selectNode: (nodeId) => set({ selectedNodeId: nodeId }),

  setNodeTypes: (nodeTypes) => set({ nodeTypes }),

  loadCanvasFromWorkflow: (w) => {
    const { nodes, edges } = apiCanvasToFlow(w.canvas);
    set({
      workflow: w,
      nodes,
      edges,
      selectedNodeId: null,
    });
  },

  getCanvasPayload: () => {
    const { nodes, edges } = get();
    return {
      nodes: nodes.map((n) => ({
        id: n.id,
        type: n.data.kind,
        label: n.data.label,
        position: n.position,
        config: n.data.config,
      })),
      edges: edges.map((e) => ({
        source: e.source,
        target: e.target,
      })),
    };
  },

  reset: () =>
    set({
      workflow: null,
      nodes: [],
      edges: [],
      selectedNodeId: null,
    }),
}));
