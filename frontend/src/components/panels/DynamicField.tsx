import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { ConfigField } from "@/types/nodes";

type Props = {
  field: ConfigField;
  value: unknown;
  onChange: (name: string, value: unknown) => void;
};

export function DynamicField({ field, value, onChange }: Props) {
  const id = `cfg-${field.name}`;

  return (
    <div className="space-y-1.5">
      <Label htmlFor={id} className="text-xs">
        {field.label}
        {field.required ? " *" : ""}
      </Label>
      {field.description ? (
        <p className="text-[11px] text-muted-foreground">{field.description}</p>
      ) : null}

      {field.field_type === "string" && (
        <Input
          id={id}
          placeholder={field.placeholder ?? ""}
          value={typeof value === "string" ? value : String(value ?? "")}
          onChange={(e) => onChange(field.name, e.target.value)}
        />
      )}

      {field.field_type === "select" && (
        <select
          id={id}
          className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm"
          value={typeof value === "string" ? value : String(field.default ?? "")}
          onChange={(e) => onChange(field.name, e.target.value)}
        >
          {(field.options ?? []).map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>
      )}

      {field.field_type === "number" && (
        <Input
          id={id}
          type="number"
          value={typeof value === "number" ? value : Number(value ?? 0)}
          onChange={(e) => onChange(field.name, Number(e.target.value))}
        />
      )}

      {field.field_type === "boolean" && (
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={Boolean(value)}
            onChange={(e) => onChange(field.name, e.target.checked)}
          />
          Enable
        </label>
      )}

      {(field.field_type === "code" || field.field_type === "json") && (
        <textarea
          id={id}
          className="min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-xs"
          placeholder={field.placeholder ?? ""}
          value={
            typeof value === "string"
              ? value
              : value !== undefined && value !== null
                ? JSON.stringify(value, null, 2)
                : ""
          }
          onChange={(e) => {
            if (field.field_type === "json") {
              try {
                const parsed = JSON.parse(e.target.value || "null") as unknown;
                onChange(field.name, parsed);
              } catch {
                onChange(field.name, e.target.value);
              }
            } else {
              onChange(field.name, e.target.value);
            }
          }}
        />
      )}

      {field.field_type === "key_value" && (
        <KeyValueEditor
          value={value}
          onChange={(v) => onChange(field.name, v)}
        />
      )}
    </div>
  );
}

function KeyValueEditor({
  value,
  onChange,
}: {
  value: unknown;
  onChange: (v: Record<string, string>) => void;
}) {
  const obj =
    value && typeof value === "object" && !Array.isArray(value)
      ? (value as Record<string, string>)
      : {};
  const entries = Object.entries(obj);
  const rows: [string, string][] =
    entries.length > 0
      ? (entries.map(([k, v]) => [k, String(v)]) as [string, string][])
      : [["", ""]];

  const setRows = (next: [string, string][]) => {
    const o: Record<string, string> = {};
    for (const [k, v] of next) {
      if (k.trim()) o[k] = v;
    }
    onChange(o);
  };

  return (
    <div className="space-y-2">
      {rows.map(([k, v], i) => (
        <div key={i} className="flex gap-1">
          <Input
            placeholder="Header"
            value={k}
            onChange={(e) => {
              const nk: [string, string][] = [...rows];
              nk[i] = [e.target.value, v];
              setRows(nk);
            }}
          />
          <Input
            placeholder="Value"
            value={v}
            onChange={(e) => {
              const nk: [string, string][] = [...rows];
              nk[i] = [k, e.target.value];
              setRows(nk);
            }}
          />
        </div>
      ))}
      <button
        type="button"
        className="text-xs text-primary underline"
        onClick={() => setRows([...rows, ["", ""] as [string, string]])}
      >
        Add row
      </button>
    </div>
  );
}
