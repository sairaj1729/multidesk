import { useState, useEffect } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { authService } from "@/services/auth";
import { Mail, ArrowLeft } from "lucide-react";

export default function VerifyEmail() {
  const [otp, setOtp] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [canResend, setCanResend] = useState(false);
  const [countdown, setCountdown] = useState(60);
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();

  const email = location.state?.email || "";

  useEffect(() => {
    if (!email) {
      navigate("/login");
      return;
    }

    // Start countdown for resend
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          setCanResend(true);
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [email, navigate]);

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    
    if (otp.length !== 6) {
      toast({
        title: "Invalid OTP",
        description: "Please enter a 6-digit OTP",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      const result = await authService.verifyEmail(email, otp);
      
      if (result.success) {
        toast({
          title: "Email Verified",
          description: "Your email has been verified successfully!",
        });
        navigate("/dashboard");
      } else {
        toast({
          title: "Verification Failed",
          description: result.error || "Invalid or expired OTP",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Verification Failed",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setIsResending(true);

    try {
      const result = await authService.resendVerificationOTP(email);
      
      if (result.success) {
        toast({
          title: "OTP Sent",
          description: "A new verification OTP has been sent to your email",
        });
        setCanResend(false);
        setCountdown(60);
        
        // Restart countdown
        const timer = setInterval(() => {
          setCountdown((prev) => {
            if (prev <= 1) {
              setCanResend(true);
              clearInterval(timer);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      } else {
        toast({
          title: "Failed to Send OTP",
          description: result.error || "Failed to send verification OTP",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Failed to Send OTP",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsResending(false);
    }
  };

  const formatOTP = (value) => {
    // Remove any non-numeric characters and limit to 6 digits
    const numericValue = value.replace(/\D/g, '').slice(0, 6);
    return numericValue;
  };

  const handleOTPChange = (e) => {
    const formatted = formatOTP(e.target.value);
    setOtp(formatted);
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

        {/* Verification Card */}
        <Card className="bg-white shadow-lg border-0">
          <CardHeader className="space-y-1 pb-6 text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Mail className="w-8 h-8 text-blue-600" />
            </div>
            <CardTitle className="text-2xl font-semibold text-gray-900">
              Verify Your Email
            </CardTitle>
            <CardDescription className="text-gray-600">
              We've sent a 6-digit verification code to
              <br />
              <span className="font-medium text-gray-900">{email}</span>
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleVerifyOTP} className="space-y-6">
              {/* OTP Input */}
              <div className="space-y-2">
                <Label htmlFor="otp" className="text-gray-700 font-medium">
                  Verification Code
                </Label>
                <Input
                  id="otp"
                  type="text"
                  placeholder="Enter 6-digit code"
                  value={otp}
                  onChange={handleOTPChange}
                  required
                  maxLength="6"
                  className="bg-gray-50 border-gray-200 focus:bg-white focus:border-blue-500 text-center text-lg tracking-widest"
                  disabled={isLoading}
                />
                <p className="text-xs text-gray-500 text-center">
                  Enter the 6-digit code sent to your email
                </p>
              </div>

              {/* Verify Button */}
              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5"
                disabled={isLoading || otp.length !== 6}
              >
                {isLoading ? (
                  <div className="flex items-center space-x-2 justify-center">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Verifying...</span>
                  </div>
                ) : (
                  "Verify Email"
                )}
              </Button>
            </form>

            {/* Resend Section */}
            <div className="text-center mt-6 space-y-2">
              <p className="text-sm text-gray-500">
                Didn't receive the code?
              </p>
              {canResend ? (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleResendOTP}
                  disabled={isResending}
                  className="text-blue-600 hover:text-blue-700"
                >
                  {isResending ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                      <span>Sending...</span>
                    </div>
                  ) : (
                    "Resend Code"
                  )}
                </Button>
              ) : (
                <p className="text-sm text-gray-400">
                  Resend code in {countdown}s
                </p>
              )}
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