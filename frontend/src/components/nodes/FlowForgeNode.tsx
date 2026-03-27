import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Clock, Code, GitBranch, Globe, Play, type LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import type { FlowForgeRfNode } from "@/store/workflowStore";
import { useWorkflowStore } from "@/store/workflowStore";

const ICONS: Record<string, LucideIcon> = {
  play: Play,
  clock: Clock,
  globe: Globe,
  code: Code,
  "git-branch": GitBranch,
};

const CATEGORY_BAR: Record<string, string> = {
  Triggers: "bg-emerald-600/90",
  HTTP: "bg-sky-600/90",
  Logic: "bg-violet-600/90",
  Custom: "bg-amber-600/90",
};

function FlowForgeNodeInner({ data, selected }: NodeProps<FlowForgeRfNode>) {
  const nodeTypes = useWorkflowStore((s) => s.nodeTypes);
  const spec = nodeTypes.find((t) => t.type === data.kind);
  const category = spec?.category ?? "Custom";
  const Icon = ICONS[spec?.icon ?? "code"] ?? Code;
  const bar = CATEGORY_BAR[category] ?? "bg-zinc-600/90";

  return (
    <div
      className={cn(
        "min-w-[160px] overflow-hidden rounded-lg border bg-card text-card-foreground shadow-sm",
        selected ? "border-primary ring-2 ring-primary/30" : "border-border",
      )}
    >
      <Handle type="target" position={Position.Top} className="!h-2 !w-2 !bg-muted-foreground" />
      <div className={cn("flex items-center gap-2 px-2 py-1 text-xs font-medium text-white", bar)}>
        <Icon className="h-3.5 w-3.5 shrink-0" aria-hidden />
        <span className="truncate">{spec?.label ?? data.kind}</span>
      </div>
      <div className="px-2 py-2 text-sm font-medium leading-tight">{data.label}</div>
      <Handle
        type="source"
        position={Position.Bottom}
        className="!h-2 !w-2 !bg-muted-foreground"
      />
    </div>
  );
}

export const FlowForgeNode = memo(FlowForgeNodeInner);
