import { useCallback, useEffect, useState } from "react";
import { Braces, Copy, Loader2, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { workflowApi } from "@/lib/api";

type Props = {
  workflowId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function WorkflowJsonDialog({ workflowId, open, onOpenChange }: Props) {
  const [jsonText, setJsonText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await workflowApi.get(workflowId);
      setJsonText(JSON.stringify(data, null, 2));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load workflow");
      setJsonText("");
    } finally {
      setLoading(false);
    }
  }, [workflowId]);

  useEffect(() => {
    if (open) void load();
  }, [open, load]);

  const copy = () => {
    void navigator.clipboard.writeText(jsonText);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[90vh] max-w-4xl flex-col gap-0 overflow-hidden p-0 sm:max-w-4xl">
        <DialogHeader className="shrink-0 space-y-1 px-6 pt-6">
          <DialogTitle className="flex items-center gap-2">
            <Braces className="h-5 w-5 text-muted-foreground" />
            Stored workflow JSON
          </DialogTitle>
          <DialogDescription>
            Full workflow row returned by the API (matches what is persisted for this workflow). Use
            Refresh after saving to pull the latest from the database.
          </DialogDescription>
        </DialogHeader>
        <div className="flex shrink-0 flex-wrap items-center gap-2 border-b px-6 pb-3">
          <Button type="button" variant="outline" size="sm" onClick={() => void load()} disabled={loading}>
            <RefreshCw className={`mr-1.5 h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button type="button" variant="outline" size="sm" onClick={copy} disabled={!jsonText}>
            <Copy className="mr-1.5 h-3.5 w-3.5" />
            Copy
          </Button>
        </div>
        <ScrollArea className="max-h-[65vh] min-h-0 flex-1 px-6 pb-6">
          <div className="pr-4 pt-1">
            {loading && !jsonText ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading…
              </div>
            ) : error ? (
              <p className="text-sm text-destructive">{error}</p>
            ) : (
              <pre className="break-all font-mono text-xs leading-relaxed text-foreground">
                {jsonText}
              </pre>
            )}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
