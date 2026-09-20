document.addEventListener('DOMContentLoaded', () => {
  // Mobile Sidebar Toggle & Backdrop
  const sidebar = document.getElementById('appSidebar');
  const toggleBtn = document.getElementById('sidebarToggleBtn');
  
  // Create backdrop element if it doesn't exist
  let backdrop = document.querySelector('.sidebar-backdrop');
  if (!backdrop) {
    backdrop = document.createElement('div');
    backdrop.className = 'sidebar-backdrop';
    document.body.appendChild(backdrop);
  }
  
  if (toggleBtn && sidebar) {
    const toggleSidebar = (show) => {
      if (show) {
        sidebar.classList.add('show');
        backdrop.classList.add('show');
      } else {
        sidebar.classList.remove('show');
        backdrop.classList.remove('show');
      }
    };

    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const willShow = !sidebar.classList.contains('show');
      toggleSidebar(willShow);
    });

    backdrop.addEventListener('click', () => {
      toggleSidebar(false);
    });
  }

  // Global Search
  const searchInput = document.getElementById('globalSearchInput');
  if (searchInput) {
    searchInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && searchInput.value.trim()) {
        window.location.href = `/resources?subject=${encodeURIComponent(searchInput.value.trim())}`;
      }
    });
  }
});

// Toast notification helper
function showToast(message, type = 'info') {
  const toastContainer = document.createElement('div');
  toastContainer.style.position = 'fixed';
  toastContainer.style.top = '20px';
  toastContainer.style.right = '20px';
  toastContainer.style.zIndex = '9999';
  
  const bgClass = type === 'success' ? 'bg-success text-white' : (type === 'danger' ? 'bg-danger text-white' : 'bg-primary text-white');
  
  toastContainer.innerHTML = `
    <div class="toast show align-items-center ${bgClass} border-0 shadow" role="alert" aria-live="assertive" aria-atomic="true" style="border-radius: 12px;">
      <div class="d-flex">
        <div class="toast-body small fw-semibold">
          ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;
  document.body.appendChild(toastContainer);
  setTimeout(() => {
    toastContainer.remove();
  }, 4000);
}
