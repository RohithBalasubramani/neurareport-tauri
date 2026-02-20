/**
 * Auto-Chart Generation API Client
 */
import apiClient from './client';

function normalizeAnalyzeArgs(input, maybeOptions = {}) {
  if (input && typeof input === 'object' && Object.prototype.hasOwnProperty.call(input, 'data')) {
    return {
      data: input.data,
      columnDescriptions: input.columnDescriptions,
      maxSuggestions: input.maxSuggestions ?? 3,
    };
  }
  return {
    data: input,
    columnDescriptions: maybeOptions.columnDescriptions,
    maxSuggestions: maybeOptions.maxSuggestions ?? 3,
  };
}

function normalizeGenerateArgs(input, maybeChartType, maybeOptions = {}) {
  if (input && typeof input === 'object' && Object.prototype.hasOwnProperty.call(input, 'data')) {
    return {
      data: input.data,
      chartType: input.chartType,
      xField: input.xField,
      yFields: input.yFields,
      title: input.title,
    };
  }
  return {
    data: input,
    chartType: maybeChartType,
    xField: maybeOptions.xField,
    yFields: maybeOptions.yFields,
    title: maybeOptions.title,
  };
}

/**
 * Analyze data for chart recommendations
 * @param {Object} params
 * @param {Array} params.data - Data rows to analyze
 * @param {Object} [params.columnDescriptions] - Optional column descriptions
 * @param {number} [params.maxSuggestions=3] - Max number of suggestions
 */
export async function analyzeData(input, maybeOptions = {}) {
  const { data, columnDescriptions, maxSuggestions = 3 } = normalizeAnalyzeArgs(input, maybeOptions);
  const response = await apiClient.post('/charts/analyze', {
    data,
    column_descriptions: columnDescriptions || undefined,
    max_suggestions: maxSuggestions,
  });
  return response.data;
}

/**
 * Queue chart analysis in the background.
 */
export async function queueAnalyzeData(input, maybeOptions = {}) {
  const { data, columnDescriptions, maxSuggestions = 3 } = normalizeAnalyzeArgs(input, maybeOptions);
  const response = await apiClient.post('/charts/analyze?background=true', {
    data,
    column_descriptions: columnDescriptions || undefined,
    max_suggestions: maxSuggestions,
  });
  return response.data;
}

/**
 * Generate chart configuration
 * @param {Object} params
 * @param {Array} params.data - Data rows
 * @param {string} params.chartType - Chart type (bar, line, pie, etc.)
 * @param {string} params.xField - X-axis field name
 * @param {string[]} params.yFields - Y-axis field names (array)
 * @param {string} [params.title] - Chart title
 */
export async function generateChart(input, maybeChartType, maybeOptions = {}) {
  const { data, chartType, xField, yFields, title } = normalizeGenerateArgs(
    input,
    maybeChartType,
    maybeOptions
  );
  const response = await apiClient.post('/charts/generate', {
    data,
    chart_type: chartType,
    x_field: xField,
    y_fields: Array.isArray(yFields) ? yFields : [yFields],
    title,
  });
  return response.data;
}

/**
 * Queue chart generation in the background.
 */
export async function queueGenerateChart(input, maybeChartType, maybeOptions = {}) {
  const { data, chartType, xField, yFields, title } = normalizeGenerateArgs(
    input,
    maybeChartType,
    maybeOptions
  );
  const response = await apiClient.post('/charts/generate?background=true', {
    data,
    chart_type: chartType,
    x_field: xField,
    y_fields: Array.isArray(yFields) ? yFields : [yFields],
    title,
  });
  return response.data;
}

export default {
  analyzeData,
  queueAnalyzeData,
  generateChart,
  queueGenerateChart,
};
