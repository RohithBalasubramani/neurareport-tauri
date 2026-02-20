/**
 * Connector Store - Zustand store for database and cloud storage connectors.
 */
import { create } from 'zustand';
import * as connectorsApi from '../api/connectors';

const useConnectorStore = create((set, get) => ({
  // State
  connectorTypes: [],
  connections: [],
  currentConnection: null,
  schema: null,
  queryResult: null,
  files: [],
  loading: false,
  testing: false,
  querying: false,
  error: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Connector Discovery
  fetchConnectorTypes: async () => {
    set({ loading: true, error: null });
    try {
      const types = await connectorsApi.listConnectorTypes();
      set({ connectorTypes: types || [], loading: false });
      return types;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  getConnectorsByCategory: async (category) => {
    try {
      const types = await connectorsApi.listConnectorsByCategory(category);
      return types;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  // Connection Test
  testConnection: async (connectorType, config) => {
    set({ testing: true, error: null });
    try {
      const result = await connectorsApi.testConnection(connectorType, config);
      set({ testing: false });
      return result;
    } catch (err) {
      set({ error: err.message, testing: false });
      return { success: false, error: err.message };
    }
  },

  // Connection CRUD
  createConnection: async (connectorType, name, config) => {
    set({ loading: true, error: null });
    try {
      const connection = await connectorsApi.createConnection(connectorType, name, config);
      set((state) => ({
        connections: [connection, ...state.connections].slice(0, 200),
        currentConnection: connection,
        loading: false,
      }));
      return connection;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  fetchConnections: async (params = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await connectorsApi.listConnections(params);
      set({ connections: response.connections || [], loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  getConnection: async (connectionId) => {
    set({ loading: true, error: null });
    try {
      const connection = await connectorsApi.getConnection(connectionId);
      set({ currentConnection: connection, loading: false });
      return connection;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  deleteConnection: async (connectionId) => {
    set({ loading: true, error: null });
    try {
      await connectorsApi.deleteConnection(connectionId);
      set((state) => ({
        connections: state.connections.filter((c) => c.id !== connectionId),
        currentConnection: state.currentConnection?.id === connectionId ? null : state.currentConnection,
        loading: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  // Health & Schema
  checkHealth: async (connectionId) => {
    set({ testing: true, error: null });
    try {
      const result = await connectorsApi.checkConnectionHealth(connectionId);
      // Update connection status
      set((state) => ({
        connections: state.connections.map((c) =>
          c.id === connectionId ? { ...c, status: result.success ? 'connected' : 'error' } : c
        ),
        testing: false,
      }));
      return result;
    } catch (err) {
      set({ error: err.message, testing: false });
      return { success: false, error: err.message };
    }
  },

  fetchSchema: async (connectionId) => {
    set({ loading: true, error: null });
    try {
      const schema = await connectorsApi.getConnectionSchema(connectionId);
      set({ schema, loading: false });
      return schema;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Query Execution
  executeQuery: async (connectionId, query, parameters = null, limit = 1000) => {
    set({ querying: true, error: null, queryResult: null });
    try {
      const result = await connectorsApi.executeQuery(connectionId, query, parameters, limit);
      set({ queryResult: result, querying: false });
      return result;
    } catch (err) {
      set({ error: err.message, querying: false });
      return null;
    }
  },

  clearQueryResult: () => set({ queryResult: null }),

  // OAuth
  getOAuthUrl: async (connectorType, redirectUri, state = null) => {
    try {
      const result = await connectorsApi.getOAuthUrl(connectorType, redirectUri, state);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  handleOAuthCallback: async (connectorType, code, redirectUri, state = null) => {
    set({ loading: true, error: null });
    try {
      const result = await connectorsApi.handleOAuthCallback(connectorType, code, redirectUri, state);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Cloud Storage Files
  listFiles: async (connectionId, path = '/') => {
    set({ loading: true, error: null });
    try {
      const result = await connectorsApi.listFiles(connectionId, path);
      set({ files: result.files || [], loading: false });
      return result.files;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  downloadFile: async (connectionId, filePath) => {
    try {
      const blob = await connectorsApi.downloadFile(connectionId, filePath);
      return blob;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  uploadFile: async (connectionId, file, destinationPath) => {
    set({ loading: true, error: null });
    try {
      const result = await connectorsApi.uploadFile(connectionId, file, destinationPath);
      await get().listFiles(connectionId, destinationPath.substring(0, destinationPath.lastIndexOf('/')));
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Sync
  syncConnection: async (connectionId, options = {}) => {
    set({ loading: true, error: null });
    try {
      const result = await connectorsApi.syncConnection(connectionId, options);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  getSyncStatus: async (connectionId) => {
    try {
      const status = await connectorsApi.getSyncStatus(connectionId);
      return status;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Connector Type Details
  getConnectorType: async (connectorType) => {
    try {
      const type = await connectorsApi.getConnectorType(connectorType);
      return type;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Scheduled Sync
  scheduleSyncJob: async (connectionId, schedule) => {
    set({ loading: true, error: null });
    try {
      const result = await connectorsApi.scheduleSyncJob(connectionId, schedule);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Reset
  reset: () => set({
    currentConnection: null,
    schema: null,
    queryResult: null,
    files: [],
    error: null,
  }),

  clearConnections: () => set({
    connections: [],
    currentConnection: null,
  }),
}));

export default useConnectorStore;
