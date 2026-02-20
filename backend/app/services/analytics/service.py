"""Analytics Service.

Services for generating insights, trends, anomalies, and correlations.
"""
from __future__ import annotations

import time
import uuid
from typing import Dict, List, Optional

import numpy as np

from backend.app.schemas.analytics import (
    Anomaly,
    AnomaliesRequest,
    AnomaliesResponse,
    AnomalySeverity,
    AnomalyType,
    CorrelationPair,
    CorrelationsRequest,
    CorrelationsResponse,
    CorrelationStrength,
    CorrelationType,
    DataSeries,
    ForecastMethod,
    ForecastPoint,
    Insight,
    InsightsRequest,
    InsightsResponse,
    InsightSeverity,
    InsightType,
    TrendDirection,
    TrendRequest,
    TrendResponse,
    TrendResult,
    WhatIfRequest,
    WhatIfResponse,
    WhatIfResult,
)


class InsightService:
    """Service for generating automated insights from data."""

    def __init__(self) -> None:
        """Initialize the insight service."""
        pass

    async def generate_insights(self, request: InsightsRequest) -> InsightsResponse:
        """Generate insights from the provided data."""
        start_time = time.time()
        insights: List[Insight] = []
        data_quality = 1.0

        for series in request.data:
            values = np.array(series.values)

            # Check data quality
            nan_ratio = np.isnan(values).sum() / len(values) if len(values) > 0 else 0
            data_quality = min(data_quality, 1 - nan_ratio)

            # Clean data for analysis
            clean_values = values[~np.isnan(values)]
            if len(clean_values) < 2:
                continue

            # Generate summary insight
            insights.append(self._summary_insight(series.name, clean_values))

            # Generate trend insight
            if len(clean_values) >= 5:
                trend_insight = self._trend_insight(series.name, clean_values)
                if trend_insight:
                    insights.append(trend_insight)

            # Generate distribution insight
            dist_insight = self._distribution_insight(series.name, clean_values)
            if dist_insight:
                insights.append(dist_insight)

            # Generate anomaly insight
            if len(clean_values) >= 10:
                anomaly_insight = self._anomaly_insight(series.name, clean_values)
                if anomaly_insight:
                    insights.append(anomaly_insight)

        # Limit insights
        if request.max_insights and len(insights) > request.max_insights:
            # Sort by severity and confidence
            insights.sort(key=lambda x: (
                0 if x.severity == InsightSeverity.HIGH else (1 if x.severity == InsightSeverity.MEDIUM else 2),
                -x.confidence
            ))
            insights = insights[:request.max_insights]

        # Generate overall summary
        summary = self._generate_summary(insights, request.data)

        processing_time = int((time.time() - start_time) * 1000)

        return InsightsResponse(
            insights=insights,
            summary=summary,
            data_quality_score=data_quality,
            processing_time_ms=processing_time,
        )

    def _summary_insight(self, name: str, values: np.ndarray) -> Insight:
        """Generate a summary statistics insight."""
        return Insight(
            id=str(uuid.uuid4()),
            type=InsightType.SUMMARY,
            title=f"Summary of {name}",
            description=(
                f"{name} ranges from {values.min():.2f} to {values.max():.2f} "
                f"with a mean of {values.mean():.2f} and median of {np.median(values):.2f}."
            ),
            severity=InsightSeverity.LOW,
            confidence=1.0,
            related_columns=[name],
            data={
                "min": float(values.min()),
                "max": float(values.max()),
                "mean": float(values.mean()),
                "median": float(np.median(values)),
                "std": float(values.std()),
            },
        )

    def _trend_insight(self, name: str, values: np.ndarray) -> Optional[Insight]:
        """Generate a trend insight."""
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)

        # Determine trend direction and strength
        std = values.std()
        if std == 0:
            return None

        normalized_slope = slope / std
        if abs(normalized_slope) < 0.1:
            return None

        direction = "upward" if slope > 0 else "downward"
        strength = "strong" if abs(normalized_slope) > 0.5 else "moderate"

        pct_change = ((values[-1] - values[0]) / abs(values[0])) * 100 if values[0] != 0 else 0

        return Insight(
            id=str(uuid.uuid4()),
            type=InsightType.TREND,
            title=f"{strength.title()} {direction} trend in {name}",
            description=(
                f"{name} shows a {strength} {direction} trend with a "
                f"{abs(pct_change):.1f}% {'increase' if slope > 0 else 'decrease'} "
                f"from start to end."
            ),
            severity=InsightSeverity.MEDIUM if abs(normalized_slope) > 0.5 else InsightSeverity.LOW,
            confidence=min(abs(normalized_slope), 1.0),
            related_columns=[name],
            data={
                "slope": float(slope),
                "direction": direction,
                "percentage_change": float(pct_change),
            },
            visualization_hint="line_chart",
        )

    def _distribution_insight(self, name: str, values: np.ndarray) -> Optional[Insight]:
        """Generate a distribution insight."""
        from scipy import stats

        # Calculate skewness
        skewness = stats.skew(values)
        kurtosis = stats.kurtosis(values)

        if abs(skewness) < 0.5 and abs(kurtosis) < 2:
            return None  # Normal distribution, not interesting

        if abs(skewness) > 1:
            skew_desc = "heavily right-skewed" if skewness > 0 else "heavily left-skewed"
            severity = InsightSeverity.MEDIUM
        else:
            skew_desc = "slightly right-skewed" if skewness > 0 else "slightly left-skewed"
            severity = InsightSeverity.LOW

        return Insight(
            id=str(uuid.uuid4()),
            type=InsightType.DISTRIBUTION,
            title=f"Non-normal distribution in {name}",
            description=(
                f"{name} has a {skew_desc} distribution (skewness: {skewness:.2f}). "
                f"This may affect statistical analysis assumptions."
            ),
            severity=severity,
            confidence=0.9,
            related_columns=[name],
            data={
                "skewness": float(skewness),
                "kurtosis": float(kurtosis),
            },
            visualization_hint="histogram",
        )

    def _anomaly_insight(self, name: str, values: np.ndarray) -> Optional[Insight]:
        """Generate an anomaly insight."""
        mean = values.mean()
        std = values.std()

        if std == 0:
            return None

        z_scores = np.abs((values - mean) / std)
        anomaly_count = (z_scores > 3).sum()

        if anomaly_count == 0:
            return None

        anomaly_indices = np.where(z_scores > 3)[0]
        anomaly_values = values[anomaly_indices]

        return Insight(
            id=str(uuid.uuid4()),
            type=InsightType.ANOMALY,
            title=f"Outliers detected in {name}",
            description=(
                f"Found {anomaly_count} potential outlier(s) in {name} "
                f"that deviate more than 3 standard deviations from the mean."
            ),
            severity=InsightSeverity.HIGH if anomaly_count > 3 else InsightSeverity.MEDIUM,
            confidence=0.85,
            related_columns=[name],
            data={
                "anomaly_count": int(anomaly_count),
                "anomaly_indices": anomaly_indices.tolist(),
                "anomaly_values": anomaly_values.tolist(),
            },
        )

    def _generate_summary(self, insights: List[Insight], data: List[DataSeries]) -> str:
        """Generate an overall summary of insights."""
        high_count = sum(1 for i in insights if i.severity == InsightSeverity.HIGH)
        medium_count = sum(1 for i in insights if i.severity == InsightSeverity.MEDIUM)

        parts = [f"Generated {len(insights)} insights from {len(data)} data series."]

        if high_count > 0:
            parts.append(f"{high_count} require immediate attention.")
        if medium_count > 0:
            parts.append(f"{medium_count} are noteworthy findings.")

        return " ".join(parts)


class TrendService:
    """Service for trend analysis and forecasting."""

    def __init__(self) -> None:
        """Initialize the trend service."""
        self._statsmodels_available = self._check_statsmodels()
        self._prophet_available = self._check_prophet()

    def _check_statsmodels(self) -> bool:
        try:
            import statsmodels  # noqa: F401
            return True
        except ImportError:
            return False

    def _check_prophet(self) -> bool:
        try:
            from prophet import Prophet  # noqa: F401
            return True
        except ImportError:
            return False

    async def analyze_trend(self, request: TrendRequest) -> TrendResponse:
        """Analyze trends and generate forecasts."""
        start_time = time.time()

        values = np.array(request.data.values)
        clean_values = values[~np.isnan(values)]

        # Determine trend
        trend_result = self._analyze_trend_direction(clean_values)

        # Generate forecast
        method = request.method
        if method == ForecastMethod.AUTO:
            method = self._select_best_method(clean_values)

        forecast, accuracy = await self._generate_forecast(
            clean_values,
            request.forecast_periods,
            method,
            request.confidence_level,
        )

        processing_time = int((time.time() - start_time) * 1000)

        return TrendResponse(
            trend=trend_result,
            forecast=forecast,
            model_accuracy=accuracy,
            method_used=method,
            processing_time_ms=processing_time,
        )

    def _analyze_trend_direction(self, values: np.ndarray) -> TrendResult:
        """Analyze the direction and strength of trend."""
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)

        # Calculate R-squared
        predicted = slope * x + intercept
        ss_res = np.sum((values - predicted) ** 2)
        ss_tot = np.sum((values - values.mean()) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Determine direction
        std = values.std()
        normalized_slope = slope / std if std > 0 else 0

        if abs(normalized_slope) < 0.1:
            direction = TrendDirection.STABLE
        elif normalized_slope > 0:
            direction = TrendDirection.UP
        else:
            direction = TrendDirection.DOWN

        # Detect volatility
        returns = np.diff(values) / values[:-1] if len(values) > 1 else np.array([0])
        volatility = returns.std()
        if volatility > 0.1:  # High volatility threshold
            direction = TrendDirection.VOLATILE

        # Detect change points (simple method)
        change_points = self._detect_change_points(values)

        # Detect seasonality
        seasonality = self._detect_seasonality(values)

        description = f"Data shows a {direction.value} trend with {r_squared:.0%} confidence."
        if seasonality:
            description += f" {seasonality} seasonality detected."

        return TrendResult(
            direction=direction,
            slope=float(slope),
            strength=float(abs(r_squared)),
            seasonality=seasonality,
            change_points=change_points,
            description=description,
        )

    def _detect_change_points(self, values: np.ndarray, threshold: float = 2.0) -> List[int]:
        """Detect change points using simple method."""
        if len(values) < 10:
            return []

        change_points = []
        window = len(values) // 5

        for i in range(window, len(values) - window):
            left_mean = values[i - window:i].mean()
            right_mean = values[i:i + window].mean()
            overall_std = values.std()

            if overall_std > 0 and abs(right_mean - left_mean) > threshold * overall_std:
                change_points.append(i)

        return change_points

    def _detect_seasonality(self, values: np.ndarray) -> Optional[str]:
        """Detect seasonality in the data."""
        if len(values) < 24:
            return None

        try:
            from scipy import signal

            # Calculate autocorrelation
            autocorr = np.correlate(values - values.mean(), values - values.mean(), mode="full")
            autocorr = autocorr[len(autocorr) // 2:]
            autocorr = autocorr / autocorr[0]

            # Find peaks
            peaks, _ = signal.find_peaks(autocorr[1:], height=0.3)

            if len(peaks) == 0:
                return None

            period = peaks[0] + 1
            if period <= 7:
                return "daily"
            elif period <= 31:
                return "weekly"
            elif period <= 92:
                return "monthly"
            elif period <= 366:
                return "yearly"

        except ImportError:
            pass

        return None

    def _select_best_method(self, values: np.ndarray) -> ForecastMethod:
        """Select the best forecasting method based on data characteristics."""
        if len(values) < 10:
            return ForecastMethod.LINEAR

        # Check for seasonality
        seasonality = self._detect_seasonality(values)
        if seasonality and self._prophet_available:
            return ForecastMethod.PROPHET

        # Check for exponential pattern
        if len(values) > 5:
            ratio = values[-1] / values[0] if values[0] != 0 else 1
            if ratio > 2 or ratio < 0.5:
                return ForecastMethod.EXPONENTIAL

        return ForecastMethod.LINEAR

    async def _generate_forecast(
        self,
        values: np.ndarray,
        periods: int,
        method: ForecastMethod,
        confidence: float,
    ) -> tuple[List[ForecastPoint], float]:
        """Generate forecast using specified method."""
        if method == ForecastMethod.LINEAR:
            return self._forecast_linear(values, periods, confidence)
        elif method == ForecastMethod.EXPONENTIAL:
            return self._forecast_exponential(values, periods, confidence)
        elif method == ForecastMethod.PROPHET and self._prophet_available:
            return self._forecast_prophet(values, periods, confidence)
        elif method == ForecastMethod.ARIMA and self._statsmodels_available:
            return self._forecast_arima(values, periods, confidence)
        else:
            return self._forecast_linear(values, periods, confidence)

    def _forecast_linear(
        self,
        values: np.ndarray,
        periods: int,
        confidence: float,
    ) -> tuple[List[ForecastPoint], float]:
        """Linear regression forecast."""
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)

        # Calculate R-squared for accuracy
        predicted = slope * x + intercept
        ss_res = np.sum((values - predicted) ** 2)
        ss_tot = np.sum((values - values.mean()) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Calculate prediction interval
        residuals = values - predicted
        std_err = residuals.std()
        z_score = 1.96 if confidence == 0.95 else 2.58

        forecasts = []
        for i in range(periods):
            idx = len(values) + i
            pred = slope * idx + intercept
            margin = z_score * std_err * np.sqrt(1 + 1 / len(values))

            forecasts.append(ForecastPoint(
                index=idx,
                predicted=float(pred),
                lower_bound=float(pred - margin),
                upper_bound=float(pred + margin),
            ))

        return forecasts, max(r_squared, 0)

    def _forecast_exponential(
        self,
        values: np.ndarray,
        periods: int,
        confidence: float,
    ) -> tuple[List[ForecastPoint], float]:
        """Exponential smoothing forecast."""
        # Simple exponential smoothing
        alpha = 0.3
        smoothed = [values[0]]
        for val in values[1:]:
            smoothed.append(alpha * val + (1 - alpha) * smoothed[-1])

        last_smoothed = smoothed[-1]
        std_err = np.std(values - np.array(smoothed))
        z_score = 1.96 if confidence == 0.95 else 2.58

        forecasts = []
        for i in range(periods):
            idx = len(values) + i
            pred = last_smoothed
            margin = z_score * std_err * np.sqrt(i + 1)

            forecasts.append(ForecastPoint(
                index=idx,
                predicted=float(pred),
                lower_bound=float(pred - margin),
                upper_bound=float(pred + margin),
            ))

        accuracy = 1 - (std_err / values.std()) if values.std() > 0 else 0.5
        return forecasts, max(accuracy, 0)

    def _forecast_prophet(
        self,
        values: np.ndarray,
        periods: int,
        confidence: float,
    ) -> tuple[List[ForecastPoint], float]:
        """Prophet forecast."""
        try:
            from prophet import Prophet
            import pandas as pd

            df = pd.DataFrame({
                "ds": pd.date_range(start="2020-01-01", periods=len(values), freq="D"),
                "y": values,
            })

            model = Prophet(interval_width=confidence)
            model.fit(df)

            future = model.make_future_dataframe(periods=periods)
            forecast = model.predict(future)

            forecasts = []
            for i in range(periods):
                idx = len(values) + i
                row = forecast.iloc[len(values) + i]
                forecasts.append(ForecastPoint(
                    index=idx,
                    timestamp=row["ds"],
                    predicted=float(row["yhat"]),
                    lower_bound=float(row["yhat_lower"]),
                    upper_bound=float(row["yhat_upper"]),
                ))

            # Calculate accuracy on historical data
            in_sample = forecast.iloc[:len(values)]
            mape = np.mean(np.abs((values - in_sample["yhat"].values) / values))
            accuracy = 1 - mape

            return forecasts, max(accuracy, 0)

        except Exception:
            return self._forecast_linear(values, periods, confidence)

    def _forecast_arima(
        self,
        values: np.ndarray,
        periods: int,
        confidence: float,
    ) -> tuple[List[ForecastPoint], float]:
        """ARIMA forecast."""
        try:
            from statsmodels.tsa.arima.model import ARIMA

            model = ARIMA(values, order=(1, 1, 1))
            fitted = model.fit()

            forecast_result = fitted.get_forecast(steps=periods)
            pred = forecast_result.predicted_mean
            conf_int = forecast_result.conf_int(alpha=1 - confidence)

            forecasts = []
            for i in range(periods):
                forecasts.append(ForecastPoint(
                    index=len(values) + i,
                    predicted=float(pred.iloc[i]),
                    lower_bound=float(conf_int.iloc[i, 0]),
                    upper_bound=float(conf_int.iloc[i, 1]),
                ))

            accuracy = 1 - (fitted.aic / 1000)  # Rough approximation
            return forecasts, max(min(accuracy, 1), 0)

        except Exception:
            return self._forecast_linear(values, periods, confidence)


class AnomalyService:
    """Service for anomaly detection."""

    async def detect_anomalies(self, request: AnomaliesRequest) -> AnomaliesResponse:
        """Detect anomalies in the data."""
        start_time = time.time()

        values = np.array(request.data.values)
        clean_values = values.copy()
        clean_values[np.isnan(clean_values)] = np.nanmean(values)

        # Calculate baseline statistics
        mean = float(np.mean(clean_values))
        std = float(np.std(clean_values))
        median = float(np.median(clean_values))

        anomalies: List[Anomaly] = []

        # Z-score based detection
        threshold = self._sensitivity_to_zscore(request.sensitivity)
        z_scores = np.abs((clean_values - mean) / std) if std > 0 else np.zeros_like(clean_values)

        for i, (value, z) in enumerate(zip(clean_values, z_scores)):
            if z > threshold:
                severity = self._z_to_severity(z)
                if self._severity_meets_min(severity, request.min_severity):
                    anomalies.append(Anomaly(
                        id=str(uuid.uuid4()),
                        type=AnomalyType.POINT,
                        severity=severity,
                        index=i,
                        timestamp=request.data.timestamps[i] if request.data.timestamps else None,
                        value=float(value),
                        expected_value=mean,
                        deviation=float(z),
                        description=f"Value {value:.2f} deviates {z:.1f} standard deviations from mean",
                        possible_causes=["Data entry error", "Unusual event", "Measurement issue"],
                    ))

        # Detect collective anomalies if requested
        if request.detect_collective and len(clean_values) > request.context_window * 2:
            collective = self._detect_collective_anomalies(
                clean_values, request.context_window
            )
            anomalies.extend(collective)

        anomaly_rate = len(anomalies) / len(values) if len(values) > 0 else 0

        processing_time = int((time.time() - start_time) * 1000)

        return AnomaliesResponse(
            anomalies=anomalies,
            anomaly_rate=anomaly_rate,
            baseline_stats={
                "mean": mean,
                "std": std,
                "median": median,
                "min": float(np.min(clean_values)),
                "max": float(np.max(clean_values)),
            },
            processing_time_ms=processing_time,
        )

    def _sensitivity_to_zscore(self, sensitivity: float) -> float:
        """Convert sensitivity to z-score threshold."""
        # Higher sensitivity = lower threshold = more anomalies
        return 4 - (sensitivity * 3)  # Range: 1 to 4

    def _z_to_severity(self, z_score: float) -> AnomalySeverity:
        """Convert z-score to severity level."""
        if z_score > 4:
            return AnomalySeverity.CRITICAL
        elif z_score > 3:
            return AnomalySeverity.HIGH
        elif z_score > 2:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW

    def _severity_meets_min(self, severity: AnomalySeverity, min_severity: AnomalySeverity) -> bool:
        """Check if severity meets minimum threshold."""
        severity_order = [
            AnomalySeverity.LOW,
            AnomalySeverity.MEDIUM,
            AnomalySeverity.HIGH,
            AnomalySeverity.CRITICAL,
        ]
        return severity_order.index(severity) >= severity_order.index(min_severity)

    def _detect_collective_anomalies(
        self,
        values: np.ndarray,
        window: int,
    ) -> List[Anomaly]:
        """Detect collective anomalies (unusual patterns)."""
        anomalies = []

        for i in range(window, len(values) - window):
            left_window = values[i - window:i]
            right_window = values[i:i + window]

            left_mean = left_window.mean()
            right_mean = right_window.mean()
            overall_std = values.std()

            if overall_std > 0:
                change = abs(right_mean - left_mean) / overall_std
                if change > 2:
                    anomalies.append(Anomaly(
                        id=str(uuid.uuid4()),
                        type=AnomalyType.TREND,
                        severity=AnomalySeverity.MEDIUM,
                        index=i,
                        value=float(values[i]),
                        expected_value=float(left_mean),
                        deviation=float(change),
                        description=f"Sudden trend change detected at index {i}",
                        possible_causes=["Policy change", "External event", "System change"],
                    ))

        return anomalies


class CorrelationService:
    """Service for correlation analysis."""

    async def analyze_correlations(self, request: CorrelationsRequest) -> CorrelationsResponse:
        """Analyze correlations between data series."""
        start_time = time.time()

        # Build correlation matrix
        n_series = len(request.data)
        correlation_matrix: Dict[str, Dict[str, float]] = {}
        correlations: List[CorrelationPair] = []

        for i, series_a in enumerate(request.data):
            correlation_matrix[series_a.name] = {}
            for j, series_b in enumerate(request.data):
                if i <= j:
                    corr, p_value = self._calculate_correlation(
                        series_a.values, series_b.values, request.method
                    )
                    correlation_matrix[series_a.name][series_b.name] = corr

                    if i < j and abs(corr) >= request.min_correlation:
                        strength = self._correlation_strength(corr)
                        significant = p_value < request.significance_level

                        correlations.append(CorrelationPair(
                            variable_a=series_a.name,
                            variable_b=series_b.name,
                            correlation=corr,
                            p_value=p_value,
                            strength=strength,
                            significant=significant,
                            description=self._describe_correlation(
                                series_a.name, series_b.name, corr, significant
                            ),
                        ))
                else:
                    correlation_matrix[series_a.name][series_b.name] = (
                        correlation_matrix[series_b.name][series_a.name]
                    )

        # Find strongest correlations
        strongest_positive = None
        strongest_negative = None

        for corr_pair in correlations:
            if corr_pair.correlation > 0:
                if strongest_positive is None or corr_pair.correlation > strongest_positive.correlation:
                    strongest_positive = corr_pair
            else:
                if strongest_negative is None or corr_pair.correlation < strongest_negative.correlation:
                    strongest_negative = corr_pair

        processing_time = int((time.time() - start_time) * 1000)

        return CorrelationsResponse(
            correlations=correlations,
            correlation_matrix=correlation_matrix,
            strongest_positive=strongest_positive,
            strongest_negative=strongest_negative,
            processing_time_ms=processing_time,
        )

    def _calculate_correlation(
        self,
        values_a: List[float],
        values_b: List[float],
        method: CorrelationType,
    ) -> tuple[float, float]:
        """Calculate correlation coefficient and p-value."""
        from scipy import stats

        a = np.array(values_a)
        b = np.array(values_b)

        # Align lengths
        min_len = min(len(a), len(b))
        a = a[:min_len]
        b = b[:min_len]

        # Remove NaN pairs
        mask = ~(np.isnan(a) | np.isnan(b))
        a = a[mask]
        b = b[mask]

        if len(a) < 3:
            return 0.0, 1.0

        if method == CorrelationType.PEARSON:
            corr, p_value = stats.pearsonr(a, b)
        elif method == CorrelationType.SPEARMAN:
            corr, p_value = stats.spearmanr(a, b)
        elif method == CorrelationType.KENDALL:
            corr, p_value = stats.kendalltau(a, b)
        else:
            corr, p_value = stats.pearsonr(a, b)

        return float(corr), float(p_value)

    def _correlation_strength(self, corr: float) -> CorrelationStrength:
        """Determine correlation strength from coefficient."""
        abs_corr = abs(corr)

        if abs_corr >= 0.7:
            return CorrelationStrength.STRONG_POSITIVE if corr > 0 else CorrelationStrength.STRONG_NEGATIVE
        elif abs_corr >= 0.4:
            return CorrelationStrength.MODERATE_POSITIVE if corr > 0 else CorrelationStrength.MODERATE_NEGATIVE
        elif abs_corr >= 0.2:
            return CorrelationStrength.WEAK_POSITIVE if corr > 0 else CorrelationStrength.WEAK_NEGATIVE
        else:
            return CorrelationStrength.NONE

    def _describe_correlation(
        self,
        name_a: str,
        name_b: str,
        corr: float,
        significant: bool,
    ) -> str:
        """Generate human-readable correlation description."""
        strength = self._correlation_strength(corr)
        direction = "positive" if corr > 0 else "negative"

        if strength == CorrelationStrength.NONE:
            return f"No significant correlation between {name_a} and {name_b}."

        strength_word = strength.value.split("_")[0]
        sig_word = "statistically significant" if significant else "not statistically significant"

        return (
            f"{name_a} and {name_b} have a {strength_word} {direction} correlation "
            f"(r={corr:.3f}), which is {sig_word}."
        )


class WhatIfService:
    """Service for what-if analysis and scenario modeling."""

    async def analyze_whatif(self, request: WhatIfRequest) -> WhatIfResponse:
        """Perform what-if analysis."""
        start_time = time.time()

        # Find target variable
        target_series = None
        for series in request.data:
            if series.name == request.target_variable:
                target_series = series
                break

        if not target_series:
            raise ValueError(f"Target variable {request.target_variable} not found")

        # Build simple predictive model
        baseline, model_r_squared = self._build_model(request.data, request.target_variable)

        # Evaluate scenarios
        results: List[WhatIfResult] = []

        for scenario in request.scenarios:
            result = self._evaluate_scenario(
                scenario, baseline, target_series.values, request.data
            )
            results.append(result)

        processing_time = int((time.time() - start_time) * 1000)

        return WhatIfResponse(
            results=results,
            baseline=baseline,
            model_r_squared=model_r_squared,
            processing_time_ms=processing_time,
        )

    def _build_model(
        self,
        data: List[DataSeries],
        target: str,
    ) -> tuple[float, float]:
        """Build a simple predictive model."""
        # Find target and predictors
        target_values = None
        predictors = []

        for series in data:
            if series.name == target:
                target_values = np.array(series.values)
            else:
                predictors.append(np.array(series.values))

        if target_values is None or len(predictors) == 0:
            return float(np.mean(target_values)) if target_values is not None else 0.0, 0.0

        # Simple linear regression
        X = np.column_stack(predictors)
        y = target_values

        # Remove NaN
        mask = ~np.isnan(y) & ~np.any(np.isnan(X), axis=1)
        X = X[mask]
        y = y[mask]

        if len(y) < 2:
            return float(np.mean(target_values)), 0.0

        # Fit model
        from scipy import linalg
        X_with_intercept = np.column_stack([np.ones(len(X)), X])
        try:
            coefficients, residues, rank, s = linalg.lstsq(X_with_intercept, y)
            y_pred = X_with_intercept @ coefficients

            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - y.mean()) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            baseline = float(y.mean())
            return baseline, max(r_squared, 0)
        except Exception:
            return float(np.mean(target_values)), 0.0

    def _evaluate_scenario(
        self,
        scenario,
        baseline: float,
        target_values: List[float],
        data: List[DataSeries],
    ) -> WhatIfResult:
        """Evaluate a single scenario."""
        # Find the variable to change
        change_series = None
        for series in data:
            if series.name == scenario.variable:
                change_series = series
                break

        if change_series is None:
            return WhatIfResult(
                scenario_name=scenario.name,
                original_value=baseline,
                projected_value=baseline,
                change=0,
                change_percentage=0,
                confidence=0,
            )

        original_mean = np.mean(change_series.values)

        # Calculate new value
        if scenario.change_type == "percentage":
            new_mean = original_mean * (1 + scenario.change_value / 100)
        elif scenario.change_type == "absolute":
            new_mean = original_mean + scenario.change_value
        else:  # value
            new_mean = scenario.change_value

        # Estimate impact (simplified - assumes linear relationship)
        target_mean = np.mean(target_values)
        if original_mean != 0:
            impact_ratio = (new_mean - original_mean) / original_mean
            projected = target_mean * (1 + impact_ratio * 0.5)  # Dampened effect
        else:
            projected = target_mean

        change = projected - baseline
        change_pct = (change / baseline * 100) if baseline != 0 else 0

        return WhatIfResult(
            scenario_name=scenario.name,
            original_value=baseline,
            projected_value=float(projected),
            change=float(change),
            change_percentage=float(change_pct),
            confidence=0.7,  # Simplified confidence
            affected_metrics={scenario.variable: float(new_mean)},
        )


# Service instances
insight_service = InsightService()
trend_service = TrendService()
anomaly_service = AnomalyService()
correlation_service = CorrelationService()
whatif_service = WhatIfService()
