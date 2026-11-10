export type UserRole = 'ADMIN' | 'INVESTIGATOR' | 'USER';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type RecommendedAction = 'ALLOW' | 'FLAG_FOR_REVIEW' | 'BLOCK';
export type TransactionStatus = 'PENDING' | 'FLAGGED' | 'APPROVED' | 'REJECTED';

export interface FeatureAttribution {
  feature: string;
  impact: string;
  value?: number;
  shap_value?: number;
}

export interface Prediction {
  prediction_id: string;
  transaction_id: string;
  fraud_probability: number;
  prediction: 'LEGITIMATE' | 'FRAUD';
  risk_level: RiskLevel;
  recommended_action: RecommendedAction;
  model_version: string;
  inference_latency_ms: number;
  rule_triggers: string[];
  explanations: FeatureAttribution[];
  created_at: string;
}

export interface Transaction {
  id: string;
  external_transaction_id: string;
  user_id?: string;
  amount: number;
  transaction_time: string;
  merchant_category: string;
  device_id?: string;
  location?: string;
  status: TransactionStatus;
  investigation_notes?: string;
  created_at: string;
  updated_at: string;
  prediction?: Prediction;
}

export interface PaginatedTransactions {
  items: Transaction[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AnalyticsOverview {
  total_transactions: number;
  fraudulent_transactions: number;
  legitimate_transactions: number;
  pending_investigations: number;
  flagged_transactions: number;
  fraud_rate_percentage: number;
  total_dollar_volume: number;
  fraud_dollar_volume: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
}

export interface FraudTrendPoint {
  timestamp: string;
  total_volume: number;
  fraud_count: number;
  total_amount: number;
  fraud_amount: number;
}

export interface RiskDistributionItem {
  risk_level: string;
  count: number;
  percentage: number;
}

export interface VolumePoint {
  date: string;
  transaction_count: number;
  dollar_volume: number;
}

export interface ModelInfo {
  version: string;
  model_name: string;
  artifact_path: string;
  status: 'ACTIVE' | 'CANDIDATE' | 'DEPRECATED';
  trained_at?: string;
  input_features: string[];
  num_features: number;
  optimal_threshold: number;
}

export interface ModelMetrics {
  version: string;
  model_name: string;
  status: string;
  metrics: {
    pr_auc: number;
    roc_auc: number;
    f1: number;
    precision: number;
    recall: number;
    rates?: {
      false_positive_rate: number;
      false_negative_rate: number;
    };
  };
  confusion_matrix: {
    tp: number;
    fp: number;
    tn: number;
    fn: number;
  };
  comparison_table?: any[];
}

export interface ModelVersion {
  id: string;
  version: string;
  model_name: string;
  artifact_path: string;
  metrics: Record<string, any>;
  status: 'ACTIVE' | 'CANDIDATE' | 'DEPRECATED';
  approved_by?: string;
  created_at: string;
  updated_at: string;
}

