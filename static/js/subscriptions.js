// Global function for editing and adding subscriptions
console.log('Subscriptions.js: Script initialization started');

// Centralized subscription modal handling
function handleSubscriptionModal(id = null) {
  console.log('Subscriptions.js: Handling subscription modal with ID:', id);
  
  // Ensure modal exists in the DOM
  function ensureModalExists() {
    let modal = document.getElementById('subscriptionModal');
    if (!modal) {
      console.log('Subscriptions.js: Creating dynamic modal');
      const modalHTML = `
        <div class="modal fade" id="subscriptionModal" tabindex="-1" aria-labelledby="subscriptionModalLabel" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="subscriptionModalLabel">
                  ${id ? 'Edit Subscription' : 'Add New Subscription'}
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body">
                <form id="subscriptionForm">
                  <input type="hidden" id="subscriptionId" name="id" value="${id || ''}">
                  <div class="mb-3">
                    <label for="subscriptionName" class="form-label">Subscription Name</label>
                    <input type="text" class="form-control" id="subscriptionName" name="name" required>
                  </div>
                  <div class="mb-3">
                    <label for="category" class="form-label">Category</label>
                    <select class="form-select" id="category" name="category" required>
                      <option value="">Select a category</option>
                      <option value="Streaming">Streaming</option>
                      <option value="Software">Software</option>
                      <option value="Gaming">Gaming</option>
                      <option value="Music">Music</option>
                      <option value="Utilities">Utilities</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  <div class="mb-3">
                    <label for="currency" class="form-label">Currency</label>
                    <select class="form-select" id="currency" name="currency" required>
                      <option value="USD">USD - US Dollar</option>
                      <option value="EUR">EUR - Euro</option>
                      <option value="GBP">GBP - British Pound</option>
                      <option value="JPY">JPY - Japanese Yen</option>
                      <option value="CNY">CNY - Chinese Yuan</option>
                      <option value="AUD">AUD - Australian Dollar</option>
                      <option value="CAD">CAD - Canadian Dollar</option>
                      <option value="CHF">CHF - Swiss Franc</option>
                      <option value="HKD">HKD - Hong Kong Dollar</option>
                      <option value="SGD">SGD - Singapore Dollar</option>
                      <option value="SEK">SEK - Swedish Krona</option>
                      <option value="KRW">KRW - South Korean Won</option>
                      <option value="INR">INR - Indian Rupee</option>
                      <option value="BRL">BRL - Brazilian Real</option>
                      <option value="RUB">RUB - Russian Ruble</option>
                      <option value="ZAR">ZAR - South African Rand</option>
                      <option value="MXN">MXN - Mexican Peso</option>
                      <option value="AED">AED - UAE Dirham</option>
                      <option value="THB">THB - Thai Baht</option>
                      <option value="TRY">TRY - Turkish Lira</option>
                      <option value="NZD">NZD - New Zealand Dollar</option>
                      <option value="PLN">PLN - Polish Złoty</option>
                      <option value="NOK">NOK - Norwegian Krone</option>
                      <option value="DKK">DKK - Danish Krone</option>
                      <option value="ILS">ILS - Israeli Shekel</option>
                      <option value="MYR">MYR - Malaysian Ringgit</option>
                      <option value="IDR">IDR - Indonesian Rupiah</option>
                      <option value="PHP">PHP - Philippine Peso</option>
                      <option value="CZK">CZK - Czech Koruna</option>
                      <option value="HUF">HUF - Hungarian Forint</option>
                      <option value="CLP">CLP - Chilean Peso</option>
                    </select>
                  </div>
                  <div class="mb-3">
                    <label for="cost" class="form-label">Cost</label>
                    <div class="input-group">
                      <span class="input-group-text" id="currencySymbol">$</span>
                      <input type="number" class="form-control" id="cost" name="cost" step="0.01" min="0" required>
                    </div>
                  </div>
                  <div class="mb-3">
                    <label for="billingCycle" class="form-label">Billing Cycle</label>
                    <select class="form-select" id="billingCycle" name="billingCycle" required>
                      <option value="weekly">Every week</option>
                      <option value="monthly" selected>Every month</option>
                      <option value="quarterly">Every Quarter</option>
                      <option value="sixMonths">Every Six Months</option>
                      <option value="yearly">Every Year</option>
                    </select>
                  </div>
                  <div class="mb-3">
                    <label for="billingDate" class="form-label">Next Billing Date</label>
                    <input type="date" class="form-control" id="billingDate" name="billingDate" required>
                  </div>
                  <div class="mb-3">
                    <label for="autoRenew" class="form-label">Auto Renew</label>
                    <select class="form-select" id="autoRenew" name="autoRenew" required>
                      <option value="yes">Yes</option>
                      <option value="no">No</option>
                    </select>
                  </div>
                  <div class="mb-3">
                    <label for="setReminder" class="form-label">Set Reminder</label>
                    <select class="form-select" id="setReminder" name="setReminder" required>
                      <option value="yes">Yes</option>
                      <option value="no">No</option>
                    </select>
                  </div>
                  <div class="mb-3">
                    <label for="notes" class="form-label">Notes (Optional)</label>
                    <textarea class="form-control" id="notes" name="notes" rows="3"></textarea>
                  </div>
                </form>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" form="subscriptionForm" class="btn btn-primary">
                  ${id ? 'Save Changes' : 'Add Subscription'}
                </button>
              </div>
            </div>
          </div>
        </div>
      `;
      document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
    return document.getElementById('subscriptionModal');
  }
  
  // If editing an existing subscription
  if (id) {
    fetch(`/subscription/${id}`)
      .then(response => response.json())
      .then(subscription => {
        console.log('Subscriptions.js: Subscription details retrieved:', subscription);
        
        // Ensure modal exists
        const modal = ensureModalExists();
        const bootstrapModal = new bootstrap.Modal(modal);
        
        // Populate form dynamically
        document.getElementById('subscriptionId').value = subscription.id;
        document.getElementById('subscriptionName').value = subscription.name;
        document.getElementById('category').value = subscription.category;
        document.getElementById('currency').value = subscription.currency || 'USD';
        const currencySymbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'CNY': '¥',
            'AUD': 'A$',
            'CAD': 'C$',
            'CHF': 'CHF',
            'HKD': 'HK$',
            'SGD': 'S$',
            'INR': '₹',
            'BRL': 'R$',
            'RUB': '₽',
            'ZAR': 'R',
            'MXN': '$',
            'AED': 'د.إ',
            'THB': '฿',
            'TRY': '₺',
            'NZD': 'NZ$',
            'PLN': 'zł',
            'NOK': 'kr',
            'DKK': 'kr',
            'ILS': '₪',
            'MYR': 'RM',
            'IDR': 'Rp',
            'PHP': '₱',
            'CZK': 'Kč',
            'HUF': 'Ft',
            'CLP': '$'
        };
        document.getElementById('currencySymbol').textContent = currencySymbols[subscription.currency] || '$';
        document.getElementById('cost').value = subscription.cost;
        document.getElementById('billingDate').value = subscription.billing_date;
        document.getElementById('notes').value = subscription.notes || '';
        document.getElementById('billingCycle').value = subscription.billing_cycle || 'monthly';
        document.getElementById('autoRenew').value = subscription.auto_renew || 'yes';
        document.getElementById('setReminder').value = subscription.set_reminder || 'yes';
        
        // Show modal
        bootstrapModal.show();
      })
      .catch(error => {
        console.error('Subscriptions.js: Error fetching subscription:', error);
        alert('Unable to load subscription details. Please try again.');
      });
  } else {
    // For adding a new subscription
    const modal = ensureModalExists();
    const bootstrapModal = new bootstrap.Modal(modal);
    
    // Reset form for new subscription
    document.getElementById('subscriptionForm').reset();
    document.getElementById('subscriptionId').value = '';
    
    // Show modal
    bootstrapModal.show();
  }
}

// Global functions for editing and adding subscriptions
window.editSubscription = function(id) {
  handleSubscriptionModal(id);
};
window.addSubscription = function() {
  handleSubscriptionModal();
};

// Form submission handler
document.addEventListener('DOMContentLoaded', function() {
  console.log('Subscriptions.js: DOM Content Loaded');
  
  const subscriptionForm = document.getElementById('subscriptionForm');
  
  if (subscriptionForm) {
    subscriptionForm.addEventListener('submit', function(event) {
      event.preventDefault();
      
      const formData = new FormData(subscriptionForm);
      const subscriptionId = document.getElementById('subscriptionId').value;
      const url = subscriptionId ? `/subscription/${subscriptionId}` : '/home_logged_in';
      const method = subscriptionId ? 'PUT' : 'POST';
      
      fetch(url, {
        method: method,
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        if (data.message) {
          alert(data.message);
          if (data.subscription) {
            console.log('Updated subscription details:', data.subscription);
          }
          location.reload();
        } else if (data.error) {
          alert(data.error);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while saving the subscription');
      });
    });
  } else {
    console.log('Subscriptions.js: No subscription form found on this page');
  }
});

// Currency symbol update
document.addEventListener('DOMContentLoaded', function() {
  const currencySelect = document.getElementById('currency');
  const currencySymbol = document.getElementById('currencySymbol');
  
  const currencySymbols = {
    'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥', 
    'AUD': 'A$', 'CAD': 'C$', 'CHF': 'CHF', 'HKD': 'HK$', 'SGD': 'S$', 
    'INR': '₹', 'BRL': 'R$', 'RUB': '₽', 'ZAR': 'R', 'MXN': '$', 
    'AED': 'د.إ', 'THB': '฿', 'TRY': '₺', 'NZD': 'NZ$', 'PLN': 'zł', 
    'NOK': 'kr', 'DKK': 'kr', 'ILS': '₪', 'MYR': 'RM', 'IDR': 'Rp', 
    'PHP': '₱', 'CZK': 'Kč', 'HUF': 'Ft', 'CLP': '$'
  };
  
  if (currencySelect) {
    currencySelect.addEventListener('change', function() {
      currencySymbol.textContent = currencySymbols[this.value] || '$';
    });
  }
});

// Delete subscription functionality
window.deleteSubscription = function(subscriptionId) {
  const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
  const confirmDeleteButton = document.getElementById('confirmDelete');
  
  confirmDeleteButton.onclick = function() {
    fetch(`/subscription/${subscriptionId}`, {
      method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
      if (data.message) {
        alert(data.message);
        location.reload();
      } else if (data.error) {
        alert(data.error);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('An error occurred while deleting the subscription');
    });
    
    deleteModal.hide();
  };
  
  deleteModal.show();
};

console.log('Subscriptions.js: Script initialization completed');