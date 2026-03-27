import { useEffect, useMemo } from "react";
import { Clock, Code, GitBranch, Globe, Play, type LucideIcon } from "lucide-react";

import { ScrollArea } from "@/components/ui/scroll-area";
import { DynamicField } from "@/components/panels/DynamicField";
import { useWorkflowStore } from "@/store/workflowStore";

const ICONS: Record<string, LucideIcon> = {
  play: Play,
  clock: Clock,
  globe: Globe,
  code: Code,
  "git-branch": GitBranch,
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
