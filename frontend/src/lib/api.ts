import axios from "axios";

import type {
  WorkflowCreate,
  WorkflowListItem,
  WorkflowResponse,
  WorkflowUpdate,
} from "@/types/workflow";
import type { NodeTypeSchema } from "@/types/nodes";

const api = axios.create({ baseURL: "/api" });

export const workflowApi = {
  list: () => api.get<WorkflowListItem[]>("/workflows"),
  get: (id: string) => api.get<WorkflowResponse>(`/workflows/${id}`),
  create: (data: WorkflowCreate) => api.post<WorkflowResponse>("/workflows", data),
  update: (id: string, data: WorkflowUpdate) =>
    api.put<WorkflowResponse>(`/workflows/${id}`, data),
  delete: (id: string) => api.delete(`/workflows/${id}`),
  publish: (id: string) => api.post<WorkflowResponse>(`/workflows/${id}/publish`),
  unpublish: (id: string) => api.post<WorkflowResponse>(`/workflows/${id}/unpublish`),
};

export const nodeApi = {
  getRegistry: () => api.get<NodeTypeSchema[]>("/nodes/registry"),
};
