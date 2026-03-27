import { formatDistanceToNow } from "date-fns";
import { parseISO } from "date-fns";
import { Braces } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { WorkflowJsonDialog } from "@/components/workflow/WorkflowJsonDialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { workflowApi } from "@/lib/api";
import type { WorkflowListItem } from "@/types/workflow";

export function WorkflowList() {
  const navigate = useNavigate();
  const [items, setItems] = useState<WorkflowListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<WorkflowListItem | null>(null);
  const [jsonWorkflowId, setJsonWorkflowId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await workflowApi.list();
      setItems(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const onCreate = async () => {
    if (!newName.trim()) return;
    try {
      const { data } = await workflowApi.create({ name: newName.trim() });
      setCreateOpen(false);
      setNewName("");
      navigate(`/workflows/${data.id}`);
    } catch (e) {
      console.error(e);
    }
  };

  const onPublish = async (id: string) => {
    try {
      await workflowApi.publish(id);
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  const onUnpublish = async (id: string) => {
    try {
      await workflowApi.unpublish(id);
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  const onDelete = async () => {
    if (!deleteTarget) return;
    try {
      await workflowApi.delete(deleteTarget.id);
      setDeleteTarget(null);
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="flex items-center justify-between border-b px-6 py-4">
        <h1 className="text-xl font-semibold tracking-tight">FlowForge</h1>
        <Button type="button" onClick={() => setCreateOpen(true)}>
          New Workflow
        </Button>
      </header>

      <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-8">
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading workflows…</p>
        ) : items.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No workflows yet. Create one to get started.
          </p>
        ) : (
          <ul className="divide-y rounded-lg border bg-card">
            {items.map((w) => (
              <li
                key={w.id}
                className="flex flex-wrap items-center gap-3 px-4 py-3 sm:flex-nowrap"
              >
                <Link
                  to={`/workflows/${w.id}`}
                  className="min-w-0 flex-1 font-medium text-primary hover:underline"
                >
                  {w.name}
                </Link>
                <Badge variant={w.status === "published" ? "default" : "outline"}>
                  {w.status === "published" ? "Published" : "Draft"}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {formatDistanceToNow(parseISO(w.updated_at), { addSuffix: true })}
                </span>
                <div className="flex shrink-0 flex-wrap gap-2">
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    title="View stored JSON"
                    onClick={() => setJsonWorkflowId(w.id)}
                  >
                    <Braces className="h-4 w-4" />
                  </Button>
                  {w.status === "draft" ? (
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      onClick={() => void onPublish(w.id)}
                    >
                      Publish
                    </Button>
                  ) : (
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      onClick={() => void onUnpublish(w.id)}
                    >
                      Unpublish
                    </Button>
                  )}
                  <Button
                    type="button"
                    size="sm"
                    variant="destructive"
                    onClick={() => setDeleteTarget(w)}
                  >
                    Delete
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </main>

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New workflow</DialogTitle>
          </DialogHeader>
          <Input
            placeholder="Workflow name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") void onCreate();
            }}
          />
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setCreateOpen(false)}>
              Cancel
            </Button>
            <Button type="button" onClick={() => void onCreate()}>
              Create
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {jsonWorkflowId ? (
        <WorkflowJsonDialog
          workflowId={jsonWorkflowId}
          open
          onOpenChange={(o) => {
            if (!o) setJsonWorkflowId(null);
          }}
        />
      ) : null}

      <Dialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete workflow?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            This cannot be undone. The workflow
            {deleteTarget ? ` “${deleteTarget.name}”` : ""} will be removed
            {deleteTarget?.status === "published" ? " and its published DAG file deleted." : "."}
          </p>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setDeleteTarget(null)}>
              Cancel
            </Button>
            <Button type="button" variant="destructive" onClick={() => void onDelete()}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
