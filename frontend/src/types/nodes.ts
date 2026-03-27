export interface ConfigField {
  name: string;
  field_type: string;
  label: string;
  required: boolean;
  default: unknown;
  options: string[] | null;
  placeholder: string | null;
  description: string | null;
}

export interface NodeTypeSchema {
  type: string;
  label: string;
  category: string;
  icon: string;
  description: string;
  config_fields: ConfigField[];
}
