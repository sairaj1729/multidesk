import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Header from "./Header";
import RiskIndicator from "@/components/ui/RiskIndicator";
import RiskNotification from "@/components/ui/RiskNotification";

export function AppLayout() {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto bg-background">
          <Outlet />
        </main>
        <RiskIndicator />
        <RiskNotification />
      </div>
    </div>
  );
}

export default AppLayout;
