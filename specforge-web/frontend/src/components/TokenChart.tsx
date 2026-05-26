import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { LLMCall } from "@/lib/api";

type Props = {
  calls: LLMCall[];
};

export function TokenChart({ calls }: Props) {
  const data = calls.map((c, i) => ({
    name: `#${i + 1}`,
    prompt: c.prompt_tokens,
    completion: c.completion_tokens,
    cost: Number(c.cost_usd),
  }));

  if (data.length === 0) {
    return <p className="text-sm text-muted-foreground">No token data yet.</p>;
  }

  return (
    <div className="h-48 w-full">
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" fontSize={11} />
          <YAxis fontSize={11} />
          <Tooltip />
          <Bar dataKey="prompt" stackId="a" fill="#3b82f6" name="Prompt" />
          <Bar dataKey="completion" stackId="a" fill="#10b981" name="Completion" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
