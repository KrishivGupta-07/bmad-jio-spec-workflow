import { createContext, useContext, useState } from "react";
import { cn } from "@/lib/utils";

type AccordionContextValue = {
  isOpen: (value: string) => boolean;
  toggle: (value: string) => void;
};

const AccordionContext = createContext<AccordionContextValue | null>(null);

export function Accordion({
  children,
  className,
  type = "multiple",
  defaultValue = [],
}: {
  children: React.ReactNode;
  className?: string;
  type?: "single" | "multiple";
  defaultValue?: string[];
}) {
  const [open, setOpen] = useState<string[]>(defaultValue);

  const isOpen = (value: string) => open.includes(value);
  const toggle = (value: string) =>
    setOpen((prev) => {
      if (prev.includes(value)) return prev.filter((v) => v !== value);
      return type === "single" ? [value] : [...prev, value];
    });

  return (
    <AccordionContext.Provider value={{ isOpen, toggle }}>
      <div className={cn("space-y-2", className)}>{children}</div>
    </AccordionContext.Provider>
  );
}

export function AccordionItem({
  value,
  trigger,
  children,
  className,
}: {
  value: string;
  trigger: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  const ctx = useContext(AccordionContext);
  if (!ctx) throw new Error("AccordionItem must be used within Accordion");
  const open = ctx.isOpen(value);

  return (
    <div className={cn("overflow-hidden rounded-lg border bg-card", className)}>
      <button
        type="button"
        onClick={() => ctx.toggle(value)}
        className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left hover:bg-muted/40"
        aria-expanded={open}
      >
        <div className="min-w-0 flex-1">{trigger}</div>
        <svg
          className={cn(
            "h-4 w-4 flex-shrink-0 text-muted-foreground transition-transform",
            open && "rotate-180",
          )}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>
      {open && <div className="border-t px-4 py-4">{children}</div>}
    </div>
  );
}
