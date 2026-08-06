import { DEFAULT_SETTINGS, type GenerationSettings } from "../lib/types";

interface SettingsPanelProps {
  settings: GenerationSettings;
  onChange: (settings: GenerationSettings) => void;
  disabled?: boolean;
}

function Field<K extends keyof GenerationSettings>({
  label,
  settingKey,
  options,
  settings,
  onChange,
  disabled,
}: {
  label: string;
  settingKey: K;
  options: { value: GenerationSettings[K]; label: string }[];
  settings: GenerationSettings;
  onChange: (settings: GenerationSettings) => void;
  disabled?: boolean;
}) {
  return (
    <div>
      <label className="mb-1.5 block font-mono text-[10px] uppercase tracking-[0.14em] text-ink-faint">
        {label}
      </label>
      <div className="flex flex-wrap gap-1.5">
        {options.map((opt) => (
          <button
            key={String(opt.value)}
            type="button"
            disabled={disabled}
            onClick={() => onChange({ ...settings, [settingKey]: opt.value })}
            className={[
              "rounded-md border px-2.5 py-1 text-xs transition-colors",
              settings[settingKey] === opt.value
                ? "border-tally bg-tally/15 text-tally"
                : "border-base-hairline bg-base-raised text-ink-muted hover:border-scope",
              disabled && "opacity-40",
            ]
              .filter(Boolean)
              .join(" ")}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export function SettingsPanel({ settings, onChange, disabled }: SettingsPanelProps) {
  return (
    <div className="space-y-4 rounded-xl border border-base-hairline bg-base-panel p-4 shadow-panel">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-ink-faint">
          Generation settings
        </span>
        <button
          type="button"
          onClick={() => onChange(DEFAULT_SETTINGS)}
          disabled={disabled}
          className="font-mono text-[10px] uppercase text-ink-faint hover:text-ink disabled:opacity-40"
        >
          Reset
        </button>
      </div>

      <div>
        <label className="mb-1.5 block font-mono text-[10px] uppercase tracking-[0.14em] text-ink-faint">
          AI provider
        </label>
        <div className="flex flex-wrap gap-1.5">
          <span className="rounded-md border border-scope-dim bg-scope/10 px-2.5 py-1 text-xs text-scope">
            Gemini
          </span>
          {["GPT", "Claude"].map((p) => (
            <span
              key={p}
              className="cursor-not-allowed rounded-md border border-base-hairline bg-base-raised px-2.5 py-1 text-xs text-ink-faint"
              title="Coming soon — no API key configured for this provider yet"
            >
              {p} · Coming soon
            </span>
          ))}
        </div>
      </div>

      <Field
        label="Content length"
        settingKey="content_length"
        settings={settings}
        onChange={onChange}
        disabled={disabled}
        options={[
          { value: "short", label: "Short" },
          { value: "medium", label: "Medium" },
          { value: "long", label: "Long" },
        ]}
      />
      <Field
        label="Creativity"
        settingKey="creativity"
        settings={settings}
        onChange={onChange}
        disabled={disabled}
        options={[
          { value: "low", label: "Low" },
          { value: "medium", label: "Medium" },
          { value: "high", label: "High" },
        ]}
      />
      <Field
        label="Target platform"
        settingKey="target_platform"
        settings={settings}
        onChange={onChange}
        disabled={disabled}
        options={[
          { value: "youtube", label: "YouTube" },
          { value: "tiktok", label: "TikTok" },
          { value: "instagram", label: "Instagram" },
          { value: "blog", label: "Blog" },
        ]}
      />
      <Field
        label="Tone"
        settingKey="tone"
        settings={settings}
        onChange={onChange}
        disabled={disabled}
        options={[
          { value: "professional", label: "Professional" },
          { value: "educational", label: "Educational" },
          { value: "storytelling", label: "Storytelling" },
          { value: "humorous", label: "Humorous" },
        ]}
      />
      <Field
        label="Audience"
        settingKey="audience"
        settings={settings}
        onChange={onChange}
        disabled={disabled}
        options={[
          { value: "beginner", label: "Beginner" },
          { value: "intermediate", label: "Intermediate" },
          { value: "advanced", label: "Advanced" },
        ]}
      />
    </div>
  );
}
