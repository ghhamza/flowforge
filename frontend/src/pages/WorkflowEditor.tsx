import { ArrowLeft, Loader2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { WorkflowCanvas } from "@/components/canvas/WorkflowCanvas";
import { NodePalette } from "@/components/nodes/NodePalette";
import { ConfigPanel } from "@/components/panels/ConfigPanel";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { nodeApi, workflowApi } from "@/lib/api";
import { useWorkflowStore } from "@/store/workflowStore";

export function WorkflowEditor() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [nameEdit, setNameEdit] = useState("");
  const [saving, setSaving] = useState(false);

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
    try {
      const canvas = getCanvasPayload();
      await workflowApi.update(id, { canvas });
      const { data } = await workflowApi.publish(id);
      loadCanvasFromWorkflow(data);
    } catch (e) {
      console.error(e);
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
        <div className="ml-auto flex flex-wrap items-center gap-2">
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
    </div>
  );
}
