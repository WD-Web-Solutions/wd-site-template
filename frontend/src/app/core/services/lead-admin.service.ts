import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { LeadDetail, LeadStatus } from '../models/lead.model';

@Injectable({
  providedIn: 'root'
})
export class LeadAdminService {
  constructor(private readonly http: HttpClient) {}

  listAll(status?: LeadStatus): Observable<LeadDetail[]> {
    const url = status
      ? `/api/admin/contact-requests?status=${status}`
      : '/api/admin/contact-requests';
    return this.http.get<LeadDetail[]>(url);
  }

  updateStatus(id: string, status: LeadStatus): Observable<LeadDetail> {
    return this.http.patch<LeadDetail>(`/api/admin/contact-requests/${id}/status`, { status });
  }
}
