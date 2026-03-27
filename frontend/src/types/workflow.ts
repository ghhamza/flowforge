export type WorkflowStatus = "draft" | "published";

export interface WorkflowListItem {
  id: string;
  name: string;
  status: WorkflowStatus;
  tags: string[];
  updated_at: string;
}

export interface Canvas {
  nodes: CanvasNode[];
  edges: CanvasEdge[];
}

export interface CanvasNode {
  id: string;
  type: string;
  label: string;
  position: { x: number; y: number };
  config: Record<string, unknown>;
}

export interface CanvasEdge {
  source: string;
  target: string;
}

export interface WorkflowResponse {
  id: string;
  name: string;
  description: string | null;
  status: WorkflowStatus;
  canvas: Canvas;
  schedule: string | null;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface WorkflowCreate {
  name: string;
  description?: string | null;
}

export interface WorkflowUpdate {
  name?: string | null;
  description?: string | null;
  canvas?: Canvas;
  schedule?: string | null;
  tags?: string[] | null;
}
