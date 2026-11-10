import api from './api';
import { Prediction } from '../types';

export interface PredictionPayload {
  transaction_id: string;
  amount: number;
  transaction_time?: string;
  merchant_category: string;
  device_id?: string;
  location?: string;
  user_id?: string;
  features?: Record<string, number>;
}

export interface BatchPredictionPayload {
  transactions: PredictionPayload[];
}

export interface BatchPredictionResponse {
  total_processed: number;
  predictions: Prediction[];
  summary: {
    total_records: number;
    fraud_predictions: number;
    high_risk_flags: number;
    fraud_rate_pct: number;
  };
}

export const predictionService = {
  async predict(payload: PredictionPayload): Promise<Prediction> {
    const response = await api.post<Prediction>('/predictions/predict', payload);
    return response.data;
  },

  async predictBatch(payload: BatchPredictionPayload): Promise<BatchPredictionResponse> {
    const response = await api.post<BatchPredictionResponse>('/predictions/batch', payload);
    return response.data;
  },

  async getPrediction(predictionId: string): Promise<Prediction> {
    const response = await api.get<Prediction>(`/predictions/${predictionId}`);
    return response.data;
  },
};

