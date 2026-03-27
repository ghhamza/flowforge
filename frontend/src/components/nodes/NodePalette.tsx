import { useMemo } from "react";

import { ScrollArea } from "@/components/ui/scroll-area";
import { Clock, Code, GitBranch, Globe, Play, type LucideIcon } from "lucide-react";

import type { NodeTypeSchema } from "@/types/nodes";

const ICONS: Record<string, LucideIcon> = {
  play: Play,
  clock: Clock,
  globe: Globe,
  code: Code,
  "git-branch": GitBranch,
};

type Props = {
  nodeTypes: NodeTypeSchema[];
};

export function NodePalette({ nodeTypes }: Props) {
  const grouped = useMemo(() => {
    const m = new Map<string, NodeTypeSchema[]>();
    for (const t of nodeTypes) {
      const list = m.get(t.category) ?? [];
      list.push(t);
      m.set(t.category, list);
    }
    for (const list of m.values()) {
      list.sort((a, b) => a.label.localeCompare(b.label));
    }
    return Array.from(m.entries()).sort(([a], [b]) => a.localeCompare(b));
  }, [nodeTypes]);

  return (
    <div className="flex h-full flex-col border-r bg-muted/30">
      <div className="border-b px-3 py-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Nodes
      </div>
      <ScrollArea className="flex-1">
        <div className="space-y-3 p-2">
          {grouped.map(([category, types]) => (
            <div key={category}>
              <p className="mb-1.5 px-1 text-[11px] font-medium text-muted-foreground">
                {category}
              </p>
              <div className="space-y-1">
                {types.map((t) => {
                  const Icon = ICONS[t.icon] ?? Code;
                  return (
                    <button
                      key={t.type}
                      type="button"
                      draggable
                      onDragStart={(e) => {
                        e.dataTransfer.setData("application/reactflow", t.type);
                        e.dataTransfer.effectAllowed = "move";
                      }}
                      className="flex w-full items-center gap-2 rounded-md border border-transparent bg-background px-2 py-1.5 text-left text-sm hover:border-border hover:bg-muted/60"
                      title={t.description}
                    >
                      <Icon className="h-4 w-4 shrink-0 text-muted-foreground" />
                      <span className="truncate">{t.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
