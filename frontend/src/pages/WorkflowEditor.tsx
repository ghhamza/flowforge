import { isAxiosError } from "axios";
import { ArrowLeft, Braces, Loader2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { WorkflowCanvas } from "@/components/canvas/WorkflowCanvas";
import { NodePalette } from "@/components/nodes/NodePalette";
import { ConfigPanel } from "@/components/panels/ConfigPanel";
import { WorkflowJsonDialog } from "@/components/workflow/WorkflowJsonDialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { nodeApi, workflowApi } from "@/lib/api";
import { useWorkflowStore } from "@/store/workflowStore";

function axiosDetailMessage(e: unknown): string {
  if (isAxiosError(e) && e.response?.data && typeof e.response.data === "object") {
    const d = (e.response.data as { detail?: unknown }).detail;
    if (typeof d === "string") return d;
  }
  return e instanceof Error ? e.message : "Request failed";
}

export function WorkflowEditor() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [nameEdit, setNameEdit] = useState("");
  const [saving, setSaving] = useState(false);
  const [publishError, setPublishError] = useState<string | null>(null);
  const [jsonDialogOpen, setJsonDialogOpen] = useState(false);

  const workflow = useWorkflowStore((s) => s.workflow);
  const nodeTypes = useWorkflowStore((s) => s.nodeTypes);
  const setNodeTypes = useWorkflowStore((s) => s.setNodeTypes);
  const loadCanvasFromWorkflow = useWorkflowStore((s) => s.loadCanvasFromWorkflow);
  const getCanvasPayload = useWorkflowStore((s) => s.getCanvasPayload);
  const reset = useWorkflowStore((s) => s.reset);

  const load = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const [{ data: wf }, { data: reg }] = await Promise.all([
        workflowApi.get(id),
        nodeApi.getRegistry(),
      ]);
      setNodeTypes(reg);
      loadCanvasFromWorkflow(wf);
      setNameEdit(wf.name);
    } catch (e) {
      console.error(e);
      navigate("/", { replace: true });
    } finally {
      setLoading(false);
    }
  }, [id, loadCanvasFromWorkflow, navigate, setNodeTypes]);

  useEffect(() => {
    void load();
    return () => {
      reset();
    };
  }, [load, reset]);

  const saveCanvas = async () => {
    if (!id || !workflow) return;
    if (workflow.status === "published") return;
    setSaving(true);
    try {
      const canvas = getCanvasPayload();
      const { data } = await workflowApi.update(id, { canvas });
      loadCanvasFromWorkflow(data);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  const saveName = async () => {
    if (!id || !workflow || !nameEdit.trim()) return;
    try {
      const { data } = await workflowApi.update(id, { name: nameEdit.trim() });
      loadCanvasFromWorkflow(data);
    } catch (e) {
      console.error(e);
    }
  };

  const publish = async () => {
    if (!id) return;
    setPublishError(null);
    try {
      const canvas = getCanvasPayload();
      await workflowApi.update(id, { canvas });
      const { data } = await workflowApi.publish(id);
      loadCanvasFromWorkflow(data);
    } catch (e) {
      console.error(e);
      setPublishError(axiosDetailMessage(e));
    }
  };

  const unpublish = async () => {
    if (!id) return;
    try {
      const { data } = await workflowApi.unpublish(id);
      loadCanvasFromWorkflow(data);
    } catch (e) {
      console.error(e);
    }
  };

  if (loading || !workflow) {
    return (
      <div className="flex min-h-screen items-center justify-center gap-2 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        Loading…
      </div>
    );
  }

  return (
    <div className="flex h-screen min-h-0 flex-col bg-background">
      <header className="flex shrink-0 flex-wrap items-center gap-2 border-b px-3 py-2">
        <Button type="button" variant="ghost" size="icon" asChild>
          <Link to="/" aria-label="Back">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <Input
          className="max-w-md border-transparent bg-transparent text-lg font-semibold hover:border-input"
          value={nameEdit}
          onChange={(e) => setNameEdit(e.target.value)}
          onBlur={() => void saveName()}
        />
        <div className="ml-auto flex min-w-0 max-w-xl flex-col items-end gap-1">
          {publishError ? (
            <p className="max-w-full rounded border border-destructive/50 bg-destructive/10 px-2 py-1 text-right text-xs text-destructive">
              {publishError}
            </p>
          ) : null}
          <div className="flex flex-wrap items-center gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setJsonDialogOpen(true)}
              title="View JSON stored in the database"
            >
              <Braces className="mr-1.5 h-4 w-4" />
              View JSON
            </Button>
            <Button
              type="button"
              variant="secondary"
              disabled={workflow.status === "published" || saving}
              onClick={() => void saveCanvas()}
            >
              {saving ? "Saving…" : "Save"}
            </Button>
            {workflow.status === "draft" ? (
              <Button type="button" onClick={() => void publish()}>
                Publish
              </Button>
            ) : (
              <Button type="button" variant="outline" onClick={() => void unpublish()}>
                Unpublish
              </Button>
            )}
          </div>
        </div>
      </header>

      <div className="flex min-h-0 flex-1 flex-col md:grid md:grid-cols-[220px_1fr_280px]">
        <div className="max-h-36 min-h-0 shrink-0 overflow-y-auto border-b md:max-h-none md:border-r md:border-b-0">
          <NodePalette nodeTypes={nodeTypes} />
        </div>
        <div className="min-h-0 flex-1 md:min-h-0">
          <WorkflowCanvas />
        </div>
        <div className="max-h-44 min-h-0 shrink-0 overflow-y-auto border-t md:max-h-none md:border-l md:border-t-0">
          <ConfigPanel />
        </div>
      </div>

      <div className="h-10 shrink-0 border-t bg-muted/20 text-center text-xs leading-10 text-muted-foreground">
        Execution logs — coming soon
      </div>

      {id ? (
        <WorkflowJsonDialog workflowId={id} open={jsonDialogOpen} onOpenChange={setJsonDialogOpen} />
      ) : null}
    </div>
  );
}
