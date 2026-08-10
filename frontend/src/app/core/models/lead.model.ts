export type LeadStatus = 'received' | 'contacted' | 'qualified' | 'won' | 'lost';

export interface LeadDetail {
  id: string;
  name: string;
  emailAddress: string;
  company: string | null;
  phone: string | null;
  service: string;
  message: string;
  status: LeadStatus;
  createdAt: string;
  updatedAt: string;
}
