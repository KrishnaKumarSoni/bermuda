import React, { useState, useEffect } from 'react';
import { Download, RefreshCw } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/services/api';
import { useAuthStore } from '@/stores/authStore';
import { FormResponse } from '@/types';

interface ResponsesModalProps {
  formId: string;
  formTitle: string;
  isOpen: boolean;
  onClose: () => void;
}

export const ResponsesModal: React.FC<ResponsesModalProps> = ({
  formId,
  formTitle,
  isOpen,
  onClose,
}) => {
  const [responses, setResponses] = useState<FormResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const { toast } = useToast();
  const { user } = useAuthStore();

  const fetchResponses = async () => {
    if (!user) return;

    setIsLoading(true);
    try {
      const rawData = await apiService.getFormResponses(formId, user);
      console.log('Raw API response:', rawData);
      
      // Map the API response to match FormResponse interface
      const mappedResponses: FormResponse[] = rawData.map((item: any) => ({
        response_id: item.session_id || `response_${Date.now()}`,
        form_id: formId,
        session_id: item.session_id,
        responses: item.data || {},
        demographics: item.demographics || {},
        transcript: item.transcript || [],
        created_at: item.timestamp || new Date().toISOString(),
        device_id: item.device_id,
        location: item.location ? {
          city: item.location.city || item.location,
          country: item.location.country
        } : undefined
      }));
      
      console.log('Mapped responses:', mappedResponses);
      setResponses(mappedResponses);
    } catch (error) {
      console.error('Error fetching responses:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch responses',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const exportToCSV = async () => {
    setIsExporting(true);
    try {
      // Get form structure to build proper headers
      const form = await apiService.getForm(formId);

      if (responses.length === 0) {
        toast({
          title: 'No Data',
          description: 'No responses to export',
          variant: 'destructive',
        });
        return;
      }

      // Build CSV headers
      const headers = ['Response ID', 'Submitted At', 'Session ID'];

      // Add demographic headers if they exist
      if (form.demographics && form.demographics.length > 0) {
        headers.push(
          ...form.demographics.map((demo: string) => `Demo: ${demo}`)
        );
      }

      // Add question headers
      form.questions.forEach((question: any, index: number) => {
        headers.push(`Q${index + 1}: ${question.text?.substring(0, 50)}...`);
      });

      // Build CSV rows
      const csvRows = [headers.join(',')];

      responses.forEach((response) => {
        const row = [
          response.response_id,
          new Date(response.created_at).toLocaleString(),
          response.session_id,
        ];

        // Add demographic data
        if (form.demographics && form.demographics.length > 0) {
          form.demographics.forEach((demo: string) => {
            row.push(response.demographics?.[demo] || '');
          });
        }

        // Add question responses
        form.questions.forEach((question: any) => {
          const answer = response.responses[question.id] || '';
          // Escape commas and quotes in CSV
          const escapedAnswer =
            typeof answer === 'string'
              ? `"${answer.replace(/"/g, '""')}"`
              : answer;
          row.push(escapedAnswer);
        });

        csvRows.push(row.join(','));
      });

      // Download CSV
      const csvContent = csvRows.join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${formTitle.replace(/[^a-z0-9]/gi, '_')}_responses.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast({
        title: 'Success',
        description: 'Responses exported successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to export responses',
        variant: 'destructive',
      });
    } finally {
      setIsExporting(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchResponses();
    }
  }, [isOpen, formId]);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[80vh] p-6">
        <DialogHeader className="mb-4">
          <DialogTitle className="flex items-center justify-between">
            <span>Form Responses: {formTitle}</span>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={fetchResponses}
                disabled={isLoading}
              >
                <RefreshCw
                  className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`}
                />
                Refresh
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={exportToCSV}
                disabled={isExporting || responses.length === 0}
              >
                <Download className="w-4 h-4 mr-2" />
                Export CSV
              </Button>
            </div>
          </DialogTitle>
        </DialogHeader>

        <div className="max-h-[calc(80vh-8rem)] overflow-y-auto pr-2">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-6 h-6 animate-spin mr-2" />
              Loading responses...
            </div>
          ) : responses.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No responses yet</p>
            </div>
          ) : (
            <div className="space-y-4 pb-4">
              <div className="text-sm text-muted-foreground mb-4 sticky top-0 bg-white py-2 border-b">
                {responses.length} response{responses.length !== 1 ? 's' : ''}{' '}
                found
              </div>

              {responses.map((response, index) => (
                <Card key={response.response_id}>
                  <CardHeader>
                    <CardTitle className="text-base">
                      Response #{index + 1}
                    </CardTitle>
                    <div className="text-sm text-muted-foreground">
                      Submitted:{' '}
                      {new Date(response.created_at).toLocaleString()}
                      <span className="ml-4">
                        Session: {response.session_id?.substring(0, 8)}...
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {/* Demographics */}
                    {response.demographics &&
                      Object.keys(response.demographics).length > 0 && (
                        <div className="mb-4">
                          <h4 className="text-sm font-medium mb-2">
                            Demographics
                          </h4>
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            {Object.entries(response.demographics).map(
                              ([key, value]) => (
                                <div key={key} className="flex">
                                  <span className="font-medium capitalize mr-2">
                                    {key}:
                                  </span>
                                  <span>{value as string}</span>
                                </div>
                              )
                            )}
                          </div>
                        </div>
                      )}

                    {/* Responses */}
                    <div>
                      <h4 className="text-sm font-medium mb-2">Responses</h4>
                      <div className="space-y-2">
                        {Object.entries(response.responses).map(
                          ([questionText, answer]) => (
                            <div key={questionText} className="text-sm">
                              <span className="font-medium text-gray-700">
                                {questionText}:
                              </span>
                              <span className="ml-2">
                                {typeof answer === 'object'
                                  ? JSON.stringify(answer)
                                  : String(answer)}
                              </span>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
