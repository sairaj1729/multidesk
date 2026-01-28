import React from "react";
import { Mail, MessageCircle, Book, ExternalLink } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

const faqs = [
  {
    question: "How do I connect my Jira instance?",
    answer: "Navigate to Integrations → Jira and click 'Connect'. You'll need your Jira domain, email, and API token. Follow the step-by-step guide in the connection form."
  },
  {
    question: "Why are my tasks not syncing?",
    answer: "Check your Jira connection status in the Integrations page. Ensure your API token is valid and your Jira instance is accessible. Try reconnecting if issues persist."
  },
  {
    question: "How often does data sync with Jira?",
    answer: "Data syncs automatically every 15 minutes. You can also trigger a manual sync from the Dashboard or Integrations page."
  },
  {
    question: "Can I export my data?",
    answer: "Yes, you can export reports and data from the Reports section. Multiple formats including CSV and PDF are supported."
  },
  {
    question: "How do I add new team members?",
    answer: "Go to Users → Add User and fill in the required information. New users will receive an email invitation to set up their account."
  },
  {
    question: "What permissions can I set for users?",
    answer: "Multi Desk supports role-based permissions including Admin, Manager, and User roles. Each role has different access levels to features and data."
  }
];

export default function Help() {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Help & Support</h1>
        <p className="text-muted-foreground">Get help and find answers to common questions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Contact Options */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-foreground">Get Support</h2>
          
          <Card>
            <CardHeader className="pb-4">
              <div className="flex items-center space-x-2">
                <Mail className="w-5 h-5 text-dashboard-primary" />
                <CardTitle className="text-base">Email Support</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <CardDescription>
                Get in touch with our support team for technical assistance.
              </CardDescription>
              <Button variant="outline" className="w-full">
                <Mail className="w-4 h-4 mr-2" />
                support@multidesk.com
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-4">
              <div className="flex items-center space-x-2">
                <MessageCircle className="w-5 h-5 text-dashboard-success" />
                <CardTitle className="text-base">Live Chat</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <CardDescription>
                Chat with our support team in real-time during business hours.
              </CardDescription>
              <Button variant="outline" className="w-full">
                <MessageCircle className="w-4 h-4 mr-2" />
                Start Chat
              </Button>
              <p className="text-xs text-muted-foreground">Mon-Fri, 9 AM - 6 PM EST</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-4">
              <div className="flex items-center space-x-2">
                <Book className="w-5 h-5 text-dashboard-info" />
                <CardTitle className="text-base">Documentation</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <CardDescription>
                Browse our comprehensive documentation and user guides.
              </CardDescription>
              <Button variant="outline" className="w-full">
                <Book className="w-4 h-4 mr-2" />
                View Docs
                <ExternalLink className="w-3 h-3 ml-1" />
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* FAQ Section */}
        <div className="lg:col-span-2">
          <h2 className="text-lg font-semibold text-foreground mb-4">Frequently Asked Questions</h2>
          
          <Card>
            <CardContent className="p-6">
              <Accordion type="single" collapsible className="w-full">
                {faqs.map((faq, index) => (
                  <AccordionItem key={index} value={`item-${index}`}>
                    <AccordionTrigger className="text-left">
                      {faq.question}
                    </AccordionTrigger>
                    <AccordionContent className="text-muted-foreground">
                      {faq.answer}
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </CardContent>
          </Card>

          {/* Additional Resources */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Additional Resources</CardTitle>
              <CardDescription>More ways to get help and stay updated</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button variant="outline" className="justify-start">
                  <Book className="w-4 h-4 mr-2" />
                  Getting Started Guide
                  <ExternalLink className="w-3 h-3 ml-auto" />
                </Button>
                <Button variant="outline" className="justify-start">
                  <MessageCircle className="w-4 h-4 mr-2" />
                  Community Forum
                  <ExternalLink className="w-3 h-3 ml-auto" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
