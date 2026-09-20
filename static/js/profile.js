/**
 * Profile Page Interactions & Goals CRUD
 */
document.addEventListener('DOMContentLoaded', () => {
  
  // Toggle Goal Completed
  document.querySelectorAll('.goal-checkbox').forEach(chk => {
    chk.addEventListener('change', async function() {
      const goalId = this.getAttribute('data-id');
      const isCompleted = this.checked;
      const titleSpan = this.closest('.goal-item').querySelector('.goal-title-text');
      
      try {
        const res = await fetch(`/api/goals/${goalId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ is_completed: isCompleted })
        });
        const data = await res.json();
        if (data.status === 'success') {
          if (isCompleted) {
            titleSpan.classList.add('text-decoration-line-through', 'text-muted');
            showToast('Goal marked as completed! 🎯', 'success');
          } else {
            titleSpan.classList.remove('text-decoration-line-through', 'text-muted');
            showToast('Goal status updated.', 'info');
          }
        }
      } catch (err) {
        console.error(err);
        showToast('Failed to update goal', 'danger');
      }
    });
  });

  // Delete Goal
  document.querySelectorAll('.delete-goal-btn').forEach(btn => {
    btn.addEventListener('click', async function() {
      const goalId = this.getAttribute('data-id');
      const itemEl = this.closest('.goal-item');
      
      if (!confirm('Are you sure you want to delete this goal?')) return;

      try {
        const res = await fetch(`/api/goals/${goalId}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.status === 'success') {
          itemEl.remove();
          showToast('Goal deleted.', 'info');
        }
      } catch (err) {
        console.error(err);
        showToast('Failed to delete goal', 'danger');
      }
    });
  });

  // Create Goal
  const newGoalForm = document.getElementById('newGoalForm');
  if (newGoalForm) {
    newGoalForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const title = document.getElementById('goalTitleInput').value.trim();
      const desc = document.getElementById('goalDescInput').value.trim();
      const targetDate = document.getElementById('goalTargetDateInput').value.trim();

      if (!title) return;

      try {
        const res = await fetch('/api/goals', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: title,
            description: desc,
            target_date: targetDate
          })
        });
        const data = await res.json();
        if (data.status === 'success') {
          // Close modal
          const modalEl = document.getElementById('newGoalModal');
          const modalInstance = bootstrap.Modal.getInstance(modalEl);
          if (modalInstance) modalInstance.hide();
          
          showToast('New goal added successfully! 🚀', 'success');
          setTimeout(() => window.location.reload(), 600);
        }
      } catch (err) {
        console.error(err);
        showToast('Failed to create goal', 'danger');
      }
    });
  }
});
