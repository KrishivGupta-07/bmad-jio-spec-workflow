import { cn } from "@/lib/utils";

const variants: Record<string, string> = {
  default: "bg-muted text-muted-foreground",
  success: "bg-emerald-100 text-emerald-800",
  failure: "bg-red-100 text-red-800",
  running: "bg-blue-100 text-blue-800",
  halted: "bg-red-200 text-red-900",
  pending: "bg-gray-100 text-gray-700",
};

export function Badge({
  children,
  variant = "default",
  className,
}: {
  children: React.ReactNode;
  variant?: keyof typeof variants;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        variants[variant] ?? variants.default,
        className,
      )}
    >
      {children}
    </span>
  );
}
