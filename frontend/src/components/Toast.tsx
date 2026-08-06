import { useEffect } from "react";

export interface Toast {
  id: number;
  text: string;
  tone?: "success" | "error";
}

export function ToastStack({ toasts, onDismiss }: { toasts: Toast[]; onDismiss: (id: number) => void }) {
  return (
    <div className="pointer-events-none fixed bottom-5 right-5 z-50 flex flex-col gap-2">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} onDismiss={onDismiss} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: (id: number) => void }) {
  useEffect(() => {
    const timer = setTimeout(() => onDismiss(toast.id), 2800);
    return () => clearTimeout(timer);
  }, [toast.id, onDismiss]);

  return (
    <div
      className={[
        "pointer-events-auto animate-fade-in rounded-lg border px-4 py-2.5 text-sm shadow-panel",
        toast.tone === "error"
          ? "border-alert/40 bg-base-panel text-alert"
          : "border-scope-dim bg-base-panel text-scope",
      ].join(" ")}
    >
      {toast.text}
    </div>
  );
}
