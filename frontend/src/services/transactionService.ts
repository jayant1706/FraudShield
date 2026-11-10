import api from './api';
import { PaginatedTransactions, Transaction, TransactionStatus } from '../types';

export interface TransactionFilters {
  page?: number;
  page_size?: number;
  status?: string;
  risk_level?: string;
  merchant_category?: string;
  search?: string;
  min_amount?: number;
  max_amount?: number;
  start_date?: string;
  end_date?: string;
}

export const transactionService = {
  async listTransactions(filters: TransactionFilters = {}): Promise<PaginatedTransactions> {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        params.append(key, String(val));
      }
    });

    const response = await api.get<PaginatedTransactions>(`/transactions?${params.toString()}`);
    return response.data;
  },

  async getTransaction(id: string): Promise<Transaction> {
    const response = await api.get<Transaction>(`/transactions/${id}`);
    return response.data;
  },

  async updateStatus(
    id: string,
    status: TransactionStatus,
    investigationNotes?: string
  ): Promise<Transaction> {
    const response = await api.patch<Transaction>(`/transactions/${id}/status`, {
      status,
      investigation_notes: investigationNotes,
    });
    return response.data;
  },

  async createTransaction(payload: Partial<Transaction>): Promise<Transaction> {
    const response = await api.post<Transaction>('/transactions', payload);
    return response.data;
  },

  // Aliases
  list(filters?: TransactionFilters) {
    return this.listTransactions(filters);
  },
  get(id: string) {
    return this.getTransaction(id);
  },
};

export default transactionService;
