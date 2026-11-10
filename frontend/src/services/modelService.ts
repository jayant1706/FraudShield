import api from './api';
import { ModelInfo, ModelMetrics, ModelVersion } from '../types';

export const modelService = {
  async getModelInfo(): Promise<ModelInfo> {
    const response = await api.get<ModelInfo>('/model/info');
    return response.data;
  },

  async getModelMetrics(): Promise<ModelMetrics> {
    const response = await api.get<ModelMetrics>('/model/metrics');
    return response.data;
  },

  async listVersions(): Promise<ModelVersion[]> {
    const response = await api.get<ModelVersion[]>('/model/versions');
    return response.data;
  },

  async triggerRetraining(datasetVersion = 'latest', forceRetrain = false): Promise<any> {
    const response = await api.post('/model/retrain', {
      dataset_version: datasetVersion,
      force_retrain: forceRetrain,
    });
    return response.data;
  },

  async promoteVersion(versionId: string): Promise<ModelVersion> {
    const response = await api.post<ModelVersion>(`/model/versions/${versionId}/promote`);
    return response.data;
  },

  // Aliases
  info() {
    return this.getModelInfo();
  },
  metrics() {
    return this.getModelMetrics();
  },
  versions() {
    return this.listVersions();
  },
  retrain(datasetVersion?: string, forceRetrain?: boolean) {
    return this.triggerRetraining(datasetVersion, forceRetrain);
  },
};

export default modelService;
