import api from './api';
import {
  AnalyticsOverview,
  FraudTrendPoint,
  RiskDistributionItem,
  VolumePoint,
} from '../types';

export const analyticsService = {
  async getOverview(): Promise<AnalyticsOverview> {
    const response = await api.get<AnalyticsOverview>('/analytics/overview');
    return response.data;
  },

  async getFraudTrends(days = 30): Promise<FraudTrendPoint[]> {
    const response = await api.get<{ trends: FraudTrendPoint[] }>(`/analytics/fraud-trends?days=${days}`);
    return response.data.trends || [];
  },

  async getRiskDistribution(): Promise<RiskDistributionItem[]> {
    const response = await api.get<{ distribution: RiskDistributionItem[] }>('/analytics/risk-distribution');
    return response.data.distribution || [];
  },

  async getTransactionVolume(days = 30): Promise<VolumePoint[]> {
    const response = await api.get<{ volume: VolumePoint[] }>(`/analytics/transaction-volume?days=${days}`);
    return response.data.volume || [];
  },

  // Aliases
  overview() {
    return this.getOverview();
  },
  fraudTrends(days?: number) {
    return this.getFraudTrends(days);
  },
  riskDistribution() {
    return this.getRiskDistribution();
  },
  transactionVolume(days?: number) {
    return this.getTransactionVolume(days);
  },
};

export default analyticsService;
