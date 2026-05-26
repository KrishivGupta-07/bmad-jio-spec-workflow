import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { ProjectDashboard } from "./pages/ProjectDashboard";
import { ProjectsList } from "./pages/ProjectsList";
import { RunDetail } from "./pages/RunDetail";
import "./index.css";

const queryClient = new QueryClient();

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ProjectsList />} />
          <Route path="/projects/:slug" element={<ProjectDashboard />} />
          <Route path="/projects/:slug/runs/:runId" element={<RunDetail />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
