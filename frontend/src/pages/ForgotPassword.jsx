import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { authService } from "@/services/auth";
import { Mail, ArrowLeft } from "lucide-react";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const result = await authService.forgotPassword(email);
      
      if (result.success) {
        setEmailSent(true);
        toast({
          title: "Reset Email Sent",
          description: "Please check your email for password reset instructions",
        });
      } else {
        toast({
          title: "Failed to Send Email",
          description: result.error || "Failed to send password reset email",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Failed to Send Email",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleProceedToReset = () => {
    navigate("/reset-password", { state: { email } });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Back Button */}
        <div className="mb-6">
          <Link
            to="/"
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Login
          </Link>
        </div>

        {/* Logo/Brand Section */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Multi Desk</h1>
          <p className="text-gray-600">Jira Dashboard & Task Management</p>
        </div>

        {/* Forgot Password Card */}
        <Card className="bg-white shadow-lg border-0">
          <CardHeader className="space-y-1 pb-6 text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Mail className="w-8 h-8 text-blue-600" />
            </div>
            <CardTitle className="text-2xl font-semibold text-gray-900">
              {emailSent ? "Check Your Email" : "Forgot Password?"}
            </CardTitle>
            <CardDescription className="text-gray-600">
              {emailSent
                ? "We've sent password reset instructions to your email address"
                : "Enter your email address and we'll send you a link to reset your password"
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!emailSent ? (
              <form onSubmit={handleForgotPassword} className="space-y-6">
                {/* Email Field */}
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-gray-700 font-medium">
                    Email Address
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="bg-gray-50 border-gray-200 focus:bg-white focus:border-blue-500"
                    disabled={isLoading}
                  />
                </div>

                {/* Send Reset Email Button */}
                <Button
                  type="submit"
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <div className="flex items-center space-x-2 justify-center">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Sending...</span>
                    </div>
                  ) : (
                    "Send Reset Email"
                  )}
                </Button>
              </form>
            ) : (
              <div className="space-y-6">
                {/* Success Message */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <Mail className="h-5 w-5 text-green-400" />
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-green-800">
                        Email Sent Successfully
                      </h3>
                      <div className="mt-2 text-sm text-green-700">
                        <p>
                          We've sent password reset instructions to{" "}
                          <span className="font-medium">{email}</span>
                        </p>
                        <p className="mt-1">
                          Check your email and follow the instructions to reset your password.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="space-y-3">
                  <Button
                    onClick={handleProceedToReset}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5"
                  >
                    I Have the Reset Code
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={() => setEmailSent(false)}
                    className="w-full"
                  >
                    Try Different Email
                  </Button>
                </div>
              </div>
            )}

            {/* Back to Login Link */}
            <div className="text-center mt-6">
              <Link
                to="/"
                className="text-sm text-blue-600 hover:text-blue-700 hover:underline"
              >
                Back to Sign In
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        {/* <div className="text-center mt-8 text-sm text-gray-500">
          <p>© 2024 Multi Desk. All rights reserved.</p>
        </div> */}
      </div>
    </div>
  );
}