import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';

import { LeadDetail, LeadStatus } from '../../core/models/lead.model';
import { LeadAdminService } from '../../core/services/lead-admin.service';

@Component({
  selector: 'app-admin-leads',
  standalone: true,
  imports: [DatePipe, FormsModule],
  templateUrl: './admin-leads.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrl: './admin-leads.component.css'
})
export class AdminLeadsComponent implements OnInit {
  private readonly leadAdminService = inject(LeadAdminService);

  readonly leads = signal<LeadDetail[]>([]);
  readonly isLoading = signal(false);
  readonly errorMessage = signal('');
  readonly statusFilter = signal<LeadStatus | ''>('received');
  readonly statusOptions: (LeadStatus | '')[] = [
    'received',
    'contacted',
    'qualified',
    'won',
    'lost',
    ''
  ];
  readonly expandedLeadId = signal<string | null>(null);
  readonly pendingLeadIds = signal<Set<string>>(new Set());

  ngOnInit(): void {
    this.loadLeads();
  }

  loadLeads(): void {
    this.isLoading.set(true);
    this.errorMessage.set('');

    const status = this.statusFilter() || undefined;

    this.leadAdminService
      .listAll(status)
      .pipe(finalize(() => this.isLoading.set(false)))
      .subscribe({
        next: leads => this.leads.set(leads),
        error: () => this.errorMessage.set('Unable to load leads. Please try again.')
      });
  }

  onFilterChange(status: LeadStatus | ''): void {
    this.statusFilter.set(status);
    this.loadLeads();
  }

  toggleExpanded(lead: LeadDetail): void {
    this.expandedLeadId.set(this.expandedLeadId() === lead.id ? null : lead.id);
  }

  updateStatus(lead: LeadDetail, status: LeadStatus): void {
    if (status === lead.status) {
      return;
    }

    this.pendingLeadIds.update(pending => new Set(pending).add(lead.id));
    this.leadAdminService
      .updateStatus(lead.id, status)
      .pipe(
        finalize(() => {
          this.pendingLeadIds.update(pending => {
            const next = new Set(pending);
            next.delete(lead.id);
            return next;
          });
        })
      )
      .subscribe({
        next: updated => {
          this.leads.update(items => items.map(item => (item.id === updated.id ? updated : item)));
        },
        error: () => this.errorMessage.set('Unable to update that lead.')
      });
  }

  isPending(id: string): boolean {
    return this.pendingLeadIds().has(id);
  }
}
