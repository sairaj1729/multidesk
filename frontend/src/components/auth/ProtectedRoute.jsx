import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "@/services/auth";

export default function ProtectedRoute({ children }) {
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      if (!authService.isAuthenticated()) {
        navigate("/");
        return;
      }

      // Check if user data is valid by fetching current user
      const result = await authService.getCurrentUser();
      if (!result.success) {
        authService.logout();
        navigate("/");
        return;
      }

      // Check if user is verified
      if (!authService.isVerified()) {
        const user = authService.getUser();
        navigate("/verify-email", { state: { email: user?.email } });
        return;
      }
    };

    checkAuth();
  }, [navigate]);

  if (!authService.isAuthenticated()) {
    return null;
  }

  return children;
}