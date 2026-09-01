import type { ReactNode } from "react";
import clsx from "clsx";

export function Card({ children, className, onClick }: { children: ReactNode; className?: string; onClick?: () => void }) {
  return (
    <div onClick={onClick} className={clsx("bg-white rounded-xl border border-ink-100 shadow-sm p-5", onClick && "cursor-pointer", className)}>
      {children}
    </div>
  );
}

export function CardHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="flex items-start justify-between mb-4">
      <div>
        <h3 className="text-base font-semibold text-ink-900">{title}</h3>
        {subtitle && <p className="text-sm text-ink-500 mt-0.5">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function Button({
  children,
  onClick,
  type = "button",
  variant = "primary",
  size = "md",
  disabled,
  className,
}: {
  children: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md";
  disabled?: boolean;
  className?: string;
}) {
  const variants = {
    primary: "bg-brand-600 text-white hover:bg-brand-700 disabled:bg-brand-300",
    secondary: "bg-ink-100 text-ink-700 hover:bg-ink-200",
    danger: "bg-red-600 text-white hover:bg-red-700",
    ghost: "bg-transparent text-ink-700 hover:bg-ink-100",
  };
  const sizes = { sm: "px-3 py-1.5 text-sm", md: "px-4 py-2 text-sm" };
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={clsx(
        "rounded-lg font-medium transition-colors disabled:cursor-not-allowed",
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </button>
  );
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "success" | "warning" | "danger" | "brand" }) {
  const tones = {
    neutral: "bg-ink-100 text-ink-700",
    success: "bg-emerald-100 text-emerald-700",
    warning: "bg-amber-100 text-amber-700",
    danger: "bg-red-100 text-red-700",
    brand: "bg-brand-100 text-brand-700",
  };
  return <span className={clsx("inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium", tones[tone])}>{children}</span>;
}

export function PriorityBadge({ priority }: { priority: string }) {
  const tone = priority === "high" ? "danger" : priority === "medium" ? "warning" : "neutral";
  return <Badge tone={tone as any}>{priority} priority</Badge>;
}

export function ProgressBar({ value, tone = "brand" }: { value: number; tone?: "brand" | "success" | "warning" | "danger" }) {
  const clamped = Math.max(0, Math.min(100, value));
  const colors = {
    brand: "bg-brand-500",
    success: "bg-emerald-500",
    warning: "bg-amber-500",
    danger: "bg-red-500",
  };
  return (
    <div className="w-full bg-ink-100 rounded-full h-2 overflow-hidden">
      <div className={clsx("h-full rounded-full transition-all", colors[tone])} style={{ width: `${clamped}%` }} />
    </div>
  );
}

export function EmptyState({ title, description, action }: { title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="text-center py-10 px-4">
      <p className="text-ink-700 font-medium">{title}</p>
      {description && <p className="text-sm text-ink-500 mt-1 max-w-sm mx-auto">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function Spinner({ className }: { className?: string }) {
  return (
    <div className={clsx("animate-spin rounded-full border-2 border-ink-200 border-t-brand-600", className)} style={{ width: 24, height: 24 }} />
  );
}

export function PageLoading() {
  return (
    <div className="flex items-center justify-center py-24">
      <Spinner />
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3">
      {message}
    </div>
  );
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement> & { label?: string; error?: string }) {
  const { label, error, className, ...rest } = props;
  return (
    <label className="block">
      {label && <span className="block text-sm font-medium text-ink-700 mb-1">{label}</span>}
      <input
        {...rest}
        className={clsx(
          "w-full rounded-lg border border-ink-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent",
          error && "border-red-400",
          className
        )}
      />
      {error && <span className="text-xs text-red-600 mt-1 block">{error}</span>}
    </label>
  );
}

export function Select(
  props: React.SelectHTMLAttributes<HTMLSelectElement> & { label?: string; error?: string; children: ReactNode }
) {
  const { label, error, className, children, ...rest } = props;
  return (
    <label className="block">
      {label && <span className="block text-sm font-medium text-ink-700 mb-1">{label}</span>}
      <select
        {...rest}
        className={clsx(
          "w-full rounded-lg border border-ink-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent bg-white",
          error && "border-red-400",
          className
        )}
      >
        {children}
      </select>
      {error && <span className="text-xs text-red-600 mt-1 block">{error}</span>}
    </label>
  );
}
