import { useEffect, useMemo } from "react";
import {
  ArrowLeftRight,
  Clock,
  Code,
  GitBranch,
  Globe,
  Play,
  type LucideIcon,
} from "lucide-react";

import { ScrollArea } from "@/components/ui/scroll-area";
import { DynamicField } from "@/components/panels/DynamicField";
import { airflowTaskIdForNode } from "@/lib/airflowNames";
import { useWorkflowStore } from "@/store/workflowStore";

const ICONS: Record<string, LucideIcon> = {
  play: Play,
  clock: Clock,
  globe: Globe,
  code: Code,
  "git-branch": GitBranch,
  "arrow-left-right": ArrowLeftRight,
};

export function ConfigPanel() {
  const selectedNodeId = useWorkflowStore((s) => s.selectedNodeId);
  const nodes = useWorkflowStore((s) => s.nodes);
  const nodeTypes = useWorkflowStore((s) => s.nodeTypes);
  const updateNodeConfig = useWorkflowStore((s) => s.updateNodeConfig);
  const selectNode = useWorkflowStore((s) => s.selectNode);

  const node = useMemo(
    () => nodes.find((n) => n.id === selectedNodeId),
    [nodes, selectedNodeId],
  );
  const spec = useMemo(
    () => nodeTypes.find((t) => t.type === node?.data.kind),
    [nodeTypes, node?.data.kind],
  );

  const edges = useWorkflowStore((s) => s.edges);
  const branchDownstreamTaskIds = useMemo(() => {
    if (!node || node.data.kind !== "condition_branch") return [];
    const targetIds = edges
      .filter((e) => e.source === node.id)
      .map((e) => e.target);
    const sorted = [...new Set(targetIds)].sort();
    return sorted.map((tid) => {
      const n = nodes.find((x) => x.id === tid);
      if (!n) return null;
      return airflowTaskIdForNode(n.data.label, n.id);
    }).filter((x): x is string => x !== null);
  }, [node, edges, nodes]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") selectNode(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [selectNode]);

  if (!node || !spec) {
    return (
      <div className="flex h-full items-center justify-center border-l bg-muted/20 px-4 text-center text-sm text-muted-foreground">
        Select a node to edit its configuration.
      </div>
    );
  }

  const Icon = ICONS[spec.icon] ?? Code;

  return (
    <div className="flex h-full flex-col border-l bg-muted/30">
      <div className="border-b px-3 py-2">
        <div className="flex items-center gap-2">
          <Icon className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-semibold">{spec.label}</span>
        </div>
        <p className="mt-1 text-xs text-muted-foreground">{spec.description}</p>
        {branchDownstreamTaskIds.length > 0 ? (
          <div className="mt-2 rounded border border-border bg-muted/40 px-2 py-1.5 text-xs">
            <p className="font-medium text-foreground">Use these in return &apos;…&apos;:</p>
            <ul className="mt-1 space-y-0.5 font-mono text-[11px] text-muted-foreground">
              {branchDownstreamTaskIds.map((tid) => (
                <li key={tid}>{tid}</li>
              ))}
            </ul>
          </div>
        ) : node.data.kind === "condition_branch" ? (
          <p className="mt-2 text-xs text-amber-700 dark:text-amber-400">
            Connect outgoing edges from this branch to downstream tasks — then allowed task ids
            appear here.
          </p>
        ) : null}
      </div>
      <ScrollArea className="flex-1">
        <div className="space-y-4 p-3">
          {spec.config_fields.map((f) => (
            <DynamicField
              key={f.name}
              field={f}
              value={node.data.config[f.name] ?? f.default}
              onChange={(name, val) => {
                updateNodeConfig(node.id, { [name]: val });
              }}
            />
          ))}
          {spec.config_fields.length === 0 ? (
            <p className="text-xs text-muted-foreground">No configurable fields.</p>
          ) : null}
        </div>
      </ScrollArea>
    </div>
  );
}
