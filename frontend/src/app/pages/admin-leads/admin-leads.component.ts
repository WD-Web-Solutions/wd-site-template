import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';

import { LeadDetail, LeadNote, LeadStatus } from '../../core/models/lead.model';
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

  readonly notes = signal<LeadNote[]>([]);
  readonly notesLoading = signal(false);
  readonly isAddingNote = signal(false);
  newNoteBody = '';

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
    if (this.expandedLeadId() === lead.id) {
      this.expandedLeadId.set(null);
      return;
    }

    this.expandedLeadId.set(lead.id);
    this.newNoteBody = '';
    this.notesLoading.set(true);

    this.leadAdminService
      .listNotes(lead.id)
      .pipe(finalize(() => this.notesLoading.set(false)))
      .subscribe({
        next: notes => this.notes.set(notes),
        error: () => this.errorMessage.set('Unable to load notes.')
      });
  }

  submitNote(leadId: string): void {
    const body = this.newNoteBody.trim();
    if (!body) {
      return;
    }

    this.isAddingNote.set(true);
    this.leadAdminService
      .addNote(leadId, body)
      .pipe(finalize(() => this.isAddingNote.set(false)))
      .subscribe({
        next: note => {
          this.notes.update(existing => [note, ...existing]);
          this.newNoteBody = '';
        },
        error: () => this.errorMessage.set('Unable to add that note.')
      });
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
