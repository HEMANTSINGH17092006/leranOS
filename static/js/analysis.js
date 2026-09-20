/**
 * AI Analysis Page Interactions & Live Refresh Pipeline
 */
document.addEventListener('DOMContentLoaded', () => {
  const refreshBtn = document.getElementById('refreshAnalysisBtn');
  if (!refreshBtn) return;

  refreshBtn.addEventListener('click', async () => {
    const originalContent = refreshBtn.innerHTML;
    refreshBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Analysing...';
    refreshBtn.disabled = true;

    try {
      const res = await fetch('/api/analysis/refresh', { method: 'POST' });
      const data = await res.json();

      if (data.status === 'success') {
        const clusterRes = data.cluster_result;
        const analysis = data.analysis;

        // Update Overview Cards
        const levelEl = document.getElementById('learningLevelHeading');
        if (levelEl) levelEl.innerText = clusterRes.overall_learning_level;

        const confEl = document.getElementById('confidenceScoreHeading');
        if (confEl) confEl.innerText = `${clusterRes.confidence_score}%`;

        const clusH = document.getElementById('clusterHeading');
        if (clusH) clusH.innerText = `Cluster ${clusterRes.cluster_id}`;

        const clusL = document.getElementById('clusterLabelSub');
        if (clusL) clusL.innerText = clusterRes.cluster_label;

        // Update Metrics
        const accEl = document.getElementById('metricAccuracy');
        if (accEl) accEl.innerText = `${clusterRes.quiz_accuracy}%`;

        const timeEl = document.getElementById('metricAvgTime');
        if (timeEl) timeEl.innerText = `${clusterRes.avg_time_per_question} sec`;

        const attEl = document.getElementById('metricAttempts');
        if (attEl) attEl.innerText = `${clusterRes.total_attempts}`;

        const studyEl = document.getElementById('metricStudyTime');
        if (studyEl) studyEl.innerText = `${clusterRes.total_study_time} hrs`;

        // Update Timestamp
        const stampEl = document.getElementById('lastUpdatedTimestamp');
        if (stampEl) stampEl.innerText = clusterRes.updated_at || 'Just now';

        // Update Strengths
        const strengthsList = document.getElementById('strengthsList');
        if (strengthsList && clusterRes.strengths) {
          strengthsList.innerHTML = clusterRes.strengths.map(s => `
            <li class="d-flex align-items-start gap-2 text-muted">
              <i class="bi bi-check2 text-success mt-1"></i>
              <span>${s}</span>
            </li>
          `).join('');
        }

        // Update Weak Areas
        const weakList = document.getElementById('weakAreasList');
        if (weakList && clusterRes.weak_areas) {
          weakList.innerHTML = clusterRes.weak_areas.map(w => `
            <li class="d-flex align-items-start gap-2 text-muted">
              <i class="bi bi-dot text-danger mt-1 fs-5"></i>
              <span>${w}</span>
            </li>
          `).join('');
        }

        // Update Insights
        const insightsContainer = document.getElementById('aiInsightsContainer');
        if (insightsContainer && clusterRes.insights) {
          insightsContainer.innerHTML = clusterRes.insights.map(ins => {
            const iconClass = ins.type === 'positive' ? 'insight-icon-positive' : (ins.type === 'warning' ? 'insight-icon-warning' : 'insight-icon-info');
            return `
              <div class="insight-item mb-0">
                <div class="insight-icon-box ${iconClass}">
                  <i class="bi ${ins.icon}"></i>
                </div>
                <div class="insight-text">${ins.text}</div>
              </div>
            `;
          }).join('');
        }

        // Update AI Suggestion
        const suggEl = document.getElementById('aiSuggestionText');
        if (suggEl && analysis.ai_suggestion) {
          suggEl.innerText = analysis.ai_suggestion;
        }

        showToast('AI Analysis & K-Means profile refreshed! ✨', 'success');
      } else {
        showToast('Failed to refresh analysis', 'danger');
      }
    } catch (err) {
      console.error(err);
      showToast('Error syncing with ML backend', 'danger');
    } finally {
      refreshBtn.innerHTML = originalContent;
      refreshBtn.disabled = false;
    }
  });
});
