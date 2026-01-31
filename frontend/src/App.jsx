import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import Login from "./pages/Login";
import Register from "./pages/Register";
import VerifyEmail from "./pages/VerifyEmail";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Dashboard from "./pages/Dashboard";
import Tasks from "./pages/Tasks";
import DataManagement from "./pages/DataManagement";
import Reports from "./pages/Reports";
import Users from "./pages/Users";
import Integrations from "./pages/Integrations";
import JiraConnection from "./pages/JiraConnection";
import Settings from "./pages/Settings";
import Help from "./pages/Help";
import Risks from "./pages/Risks";
import AssigneeProfile from "./pages/AssigneeProfile";
import AssignedTasks from "./pages/AssignedTasks";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* Authentication Routes */}
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          
          {/* Protected Dashboard Routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }>
            <Route index element={<Dashboard />} />
          </Route>
          <Route path="/tasks" element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }>
            <Route index element={<Tasks />} />
          </Route>
          <Route path="/data-management" element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }>
            <Route index element={<DataManagement />} />
          </Route>
          <Route path="/reports" element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }>
            <Route index element={<Reports />} />
          </Route>
          <Route path="/users" element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }>
            <Route index element={<Users />} />
          </Route>
          <Route path="/integrations" element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }>
            <Route index element={<Integrations />} />
          </Route>
          <Route path="/settings" element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }>
            <Route index element={<Settings />} />
          </Route>
          <Route path="/help" element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }>
            <Route index element={<Help />} />
          </Route>
          
          {/* Risk Management Route */}
          <Route path="/risks" element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }>
            <Route index element={<Risks />} />
          </Route>
          
          {/* Assignee Profile Routes */}
          <Route path="/assignee/:accountId" element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }>
            <Route index element={<AssigneeProfile />} />
          </Route>
          
          <Route path="/assignee/:accountId/tasks" element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }>
            <Route index element={<AssignedTasks />} />
          </Route>
          
          {/* Standalone Routes */}
          <Route path="/jira-connection" element={<JiraConnection />} />
          
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;