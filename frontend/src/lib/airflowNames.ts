/**
 * Mirrors backend `app.codegen.naming.slugify_label` — Airflow task_id for a canvas node.
 */
export function airflowTaskIdForNode(label: string, nodeId: string): string {
  let s = label.trim().toLowerCase();
  s = s.replace(/[^a-z0-9]+/g, "_");
  s = s.replace(/^_+|_+$/g, "");
  if (!s) s = "task";
  if (s.length > 200) s = s.slice(0, 200);
  const short = nodeId.replace(/-/g, "").slice(0, 8);
  return `${s}_${short}`;
}
