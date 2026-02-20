/**
 * Cross-Database Federation Store
 */
import { create } from 'zustand';
import * as federationApi from '../api/federation';

const useFederationStore = create((set, get) => ({
  // State
  schemas: [],
  currentSchema: null,
  joinSuggestions: [],
  queryResult: null,
  loading: false,
  error: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Fetch all schemas
  fetchSchemas: async () => {
    set({ loading: true, error: null });
    try {
      const response = await federationApi.listVirtualSchemas();
      set({ schemas: response.schemas || [], loading: false });
    } catch (err) {
      set({ error: err.message, loading: false });
    }
  },

  // Create virtual schema
  createSchema: async (data) => {
    set({ loading: true, error: null });
    try {
      const response = await federationApi.createVirtualSchema(data);
      const schema = response.schema;
      set((state) => ({
        schemas: [...state.schemas, schema].slice(0, 200),
        currentSchema: schema,
        loading: false,
      }));
      return schema;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Delete schema
  deleteSchema: async (schemaId) => {
    set({ loading: true, error: null });
    try {
      await federationApi.deleteVirtualSchema(schemaId);
      set((state) => ({
        schemas: state.schemas.filter((s) => s.id !== schemaId),
        currentSchema: state.currentSchema?.id === schemaId ? null : state.currentSchema,
        loading: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  // Get join suggestions for current schema's connections
  suggestJoins: async () => {
    const { currentSchema } = get();
    if (!currentSchema?.connections || currentSchema.connections.length < 2) {
      set({ error: 'Need at least 2 connections to suggest joins', loading: false });
      return [];
    }
    set({ loading: true, error: null });
    try {
      const response = await federationApi.suggestJoins(currentSchema.connections);
      set({ joinSuggestions: response.suggestions || [], loading: false });
      return response.suggestions;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  // Execute federated query
  executeQuery: async (schemaId, query) => {
    set({ loading: true, error: null, queryResult: null });
    try {
      const response = await federationApi.executeFederatedQuery({ schemaId, query });
      set({ queryResult: response.result, loading: false });
      return response.result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Get schema details
  getSchema: async (schemaId) => {
    set({ loading: true, error: null });
    try {
      const response = await federationApi.getVirtualSchema(schemaId);
      set({ currentSchema: response.schema || response, loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Set current schema
  setCurrentSchema: (schema) => set({ currentSchema: schema, joinSuggestions: [], queryResult: null }),

  // Reset state
  reset: () => set({
    currentSchema: null,
    joinSuggestions: [],
    queryResult: null,
    error: null,
  }),
}));

export default useFederationStore;
