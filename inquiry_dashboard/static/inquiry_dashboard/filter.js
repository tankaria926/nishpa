// Filter Form Handling
document.addEventListener('DOMContentLoaded', function() {
  const filterForm = document.getElementById('filter-form');
  const tableContainer = document.getElementById('table-container');
  
  if (!filterForm) return;
  
  // Setup event listeners for all filter elements
  const searchInput = document.getElementById('search-input');
  const statusFilter = document.getElementById('status-filter');
  const dateFilter = document.getElementById('date-filter');
  const sortFilter = document.getElementById('sort-filter');
  const perPageFilter = document.getElementById('per-page');
  
  // Debounce search input
  let searchTimeout;
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(applyFilters, 300);
    });
  }
  
  // Immediate filter on select change
  if (statusFilter) statusFilter.addEventListener('change', applyFilters);
  if (dateFilter) dateFilter.addEventListener('change', applyFilters);
  if (sortFilter) sortFilter.addEventListener('change', applyFilters);
  if (perPageFilter) perPageFilter.addEventListener('change', applyFilters);
  
  // Reset button
  const resetBtn = document.querySelector('.btn-reset');
  if (resetBtn) {
    resetBtn.addEventListener('click', function() {
      filterForm.reset();
      // Redirect to clean URL
      window.location.href = filterForm.action || window.location.pathname;
    });
  }
  
  // Status select in table (inline status updates)
  document.addEventListener('change', function(e) {
    if (e.target.classList.contains('status-select')) {
      const select = e.target;
      const inquiryRow = select.closest('.inquiry-row');
      const inquiryId = inquiryRow.dataset.inquiryId;
      const newStatus = select.value;
      
      updateInquiryStatus(inquiryId, newStatus, select);
    }
  });
  
  function applyFilters() {
    const formData = new FormData(filterForm);
    const params = new URLSearchParams(formData);
    
    // Add AJAX header to indicate we want just the table
    fetch(window.location.pathname + '?' + params.toString(), {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => response.json())
    .then(data => {
      tableContainer.innerHTML = data.html;
      window.history.replaceState({}, '', '?' + params.toString());
      
      // Re-attach event listeners to new status selects
      reattachStatusListeners();
    })
    .catch(error => console.error('Error:', error));
  }
  
  function reattachStatusListeners() {
    const statusSelects = document.querySelectorAll('.status-select');
    statusSelects.forEach(select => {
      select.addEventListener('change', function() {
        const inquiryRow = this.closest('.inquiry-row');
        const inquiryId = inquiryRow.dataset.inquiryId;
        const newStatus = this.value;
        updateInquiryStatus(inquiryId, newStatus, this);
      });
    });
  }
  
  function updateInquiryStatus(inquiryId, newStatus, selectElement) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(`/inquiries/inquiry/${inquiryId}/status/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: 'status=' + newStatus
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Add success feedback
        selectElement.style.borderColor = '#14a44d';
        selectElement.style.boxShadow = '0 0 0 2px rgba(20, 164, 77, 0.2)';
        
        setTimeout(() => {
          selectElement.style.borderColor = '#d1d5db';
          selectElement.style.boxShadow = 'none';
        }, 2000);
        
        // Show toast notification
        showNotification('Status updated successfully', 'success');
      } else {
        console.error('Error:', data.error);
        showNotification('Error: ' + data.error, 'error');
        // Reset select to previous value
        selectElement.value = newStatus === 'pending' ? 'pending' : newStatus;
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showNotification('Error updating status', 'error');
    });
  }
  
  function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 12px 20px;
      background: ${type === 'success' ? '#14a44d' : '#ef4444'};
      color: white;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      z-index: 10000;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }
});

// Add animation styles
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  
  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);
