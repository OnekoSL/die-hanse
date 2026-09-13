import { Route, Routes } from "react-router-dom";
import { DashboardPage } from "./pages/DashboardPage";
import { GamePage } from "./pages/GamePage";
import { RunDetailPage } from "./pages/RunDetailPage";
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<GamePage />} />
      <Route path="/game" element={<GamePage />} />
      <Route
        path="/backtest"
        element={
          <div className="dev-page">
            <a href="/">Zum Spiel</a>
            <DashboardPage />
          </div>
        }
      />
      <Route
        path="/runs/:runId"
        element={
          <div className="dev-page">
            <RunDetailPage />
          </div>
        }
      />
    </Routes>
  );
}
