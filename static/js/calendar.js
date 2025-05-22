(function() {
  console.log('Calendar.js: Script initialization started');
  
  let subscriptions = [];
  let currentMonth, currentYear;
  
  // Fetch subscriptions for the current month with projections
  async function fetchSubscriptions(year, month) {
    try {
      const response = await fetch(`/calendar/subscriptions/${year}/${month}`);
      const originalSubscriptions = await response.json();
      
      // Generate projected dates for each subscription
      subscriptions = originalSubscriptions.flatMap(sub => {
        const originalDate = new Date(sub.billing_date);
        const projectedDates = generateFutureBillingDates(originalDate, sub.billing_cycle || 'monthly', 12);
        
        return projectedDates.map((date, index) => ({
          id: sub.id,
          name: sub.name,
          billing_date: date.toISOString().split('T')[0],
          is_projected: index > 0,
          original_id: sub.id
        }));
      });
      
      console.log('Calendar.js: Fetched and projected subscriptions:', subscriptions);
    } catch (error) {
      console.error('Calendar.js: Error fetching subscriptions:', error);
      subscriptions = [];
    }
  }
  
  // Function to generate future billing dates based on billing cycle
  function generateFutureBillingDates(originalDate, billingCycle, numMonths) {
    const futureDates = [new Date(originalDate)];
    const baseDate = new Date(originalDate);
    
    for (let i = 1; i < numMonths; i++) {
      let projectedDate = new Date(baseDate);
      
      switch(billingCycle) {
        case 'weekly':
          projectedDate.setDate(baseDate.getDate() + (i * 7));
          break;
        case 'monthly':
          projectedDate.setMonth(baseDate.getMonth() + i);
          break;
        case 'quarterly':
          projectedDate.setMonth(baseDate.getMonth() + (i * 3));
          break;
        case 'sixMonths':
          projectedDate.setMonth(baseDate.getMonth() + (i * 6));
          break;
        case 'yearly':
          projectedDate.setFullYear(baseDate.getFullYear() + i);
          break;
        default:
          projectedDate.setMonth(baseDate.getMonth() + i);
      }
      
      futureDates.push(projectedDate);
    }
    
    return futureDates;
  }
  
  // Global function for opening edit modal from calendar
  window.calendarOpenEditModal = function(subscriptionId) {
    console.log('Calendar.js: Opening edit modal for subscription:', subscriptionId);
    if (typeof window.editSubscription === 'function') {
      window.editSubscription(subscriptionId);
    } else {
      console.error('Calendar.js: Edit subscription function not found');
      alert('Subscription editing is currently unavailable');
    }
  };
  
  document.addEventListener('DOMContentLoaded', async function() {
    console.log('Calendar.js: DOM Content Loaded');
    
    const currentDate = new Date();
    currentMonth = currentDate.getMonth();
    currentYear = currentDate.getFullYear();
    
    await fetchSubscriptions(currentYear, currentMonth + 1);
    renderCalendar(currentMonth, currentYear);
    
    document.getElementById('prevMonth').addEventListener('click', async function() {
      currentMonth--;
      if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
      }
      await fetchSubscriptions(currentYear, currentMonth + 1);
      renderCalendar(currentMonth, currentYear);
    });
    
    document.getElementById('nextMonth').addEventListener('click', async function() {
      currentMonth++;
      if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
      }
      await fetchSubscriptions(currentYear, currentMonth + 1);
      renderCalendar(currentMonth, currentYear);
    });
  });
  
  function renderCalendar(month, year) {
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startingDay = firstDay.getDay();
    const monthLength = lastDay.getDate();
    
    const monthNames = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"];
    
    document.getElementById('monthYear').textContent = `${monthNames[month]} ${year}`;
    
    let calendarBody = document.getElementById('calendarBody');
    calendarBody.innerHTML = '';
    
    let date = 1;
    for (let i = 0; i < 6; i++) {
      let row = document.createElement('tr');
      
      for (let j = 0; j < 7; j++) {
        let cell = document.createElement('td');
        cell.className = 'calendar-cell';
        
        if (i === 0 && j < startingDay) {
          cell.textContent = '';
        } else if (date > monthLength) {
          cell.textContent = '';
        } else {
          let dateDiv = document.createElement('div');
          dateDiv.className = 'date-number';
          dateDiv.textContent = date;
          cell.appendChild(dateDiv);
          
          let subscriptionList = document.createElement('div');
          subscriptionList.className = 'subscription-list';
          
          // Filter subscriptions for this date
          let dateSubscriptions = subscriptions.filter(sub => {
            let subDate = new Date(sub.billing_date);
            return subDate.getDate() === date && 
                   subDate.getMonth() === month &&
                   subDate.getFullYear() === year;
          });
          
          if (dateSubscriptions.length > 0) {
            cell.classList.add('has-subscriptions');
            cell.addEventListener('click', () => showSubscriptionsList(dateSubscriptions));
          }
          
          dateSubscriptions.slice(0, 2).forEach(sub => {
            let link = document.createElement('a');
            link.href = '#';
            link.className = 'subscription-link';
            link.textContent = sub.name + (sub.is_projected ? ' (Projected)' : '');
            link.onclick = function(e) {
              e.preventDefault();
              e.stopPropagation();
              if (!sub.is_projected) {
                calendarOpenEditModal(sub.id);
              }
            };
            subscriptionList.appendChild(link);
          });
          
          if (dateSubscriptions.length > 2) {
            let moreLink = document.createElement('a');
            moreLink.href = '#';
            moreLink.className = 'more-link';
            moreLink.textContent = `+${dateSubscriptions.length - 2} more`;
            moreLink.onclick = function(e) {
              e.preventDefault();
              e.stopPropagation();
              showSubscriptionsList(dateSubscriptions);
            };
            subscriptionList.appendChild(moreLink);
          }
          
          cell.appendChild(subscriptionList);
          date++;
        }
        
        row.appendChild(cell);
      }
      
      calendarBody.appendChild(row);
      if (date > monthLength) break;
    }
  }
  
  function showSubscriptionsList(subscriptions) {
    const modal = new bootstrap.Modal(document.getElementById('subscriptionsListModal'));
    const modalBody = document.querySelector('#subscriptionsListModal .modal-body');
    modalBody.innerHTML = '';
    
    subscriptions.forEach(sub => {
      let div = document.createElement('div');
      div.className = 'subscription-item d-flex justify-content-between align-items-center mb-2';
      div.innerHTML = `
        <div>
          <strong>${sub.name}</strong>
          <small class="text-muted d-block">Billing Date: ${sub.billing_date}</small>
          ${sub.is_projected ? '<span class="badge bg-info">Projected</span>' : ''}
        </div>
        ${!sub.is_projected ? `
          <button class="btn btn-sm btn-primary" onclick="calendarOpenEditModal(${sub.id})">
            <i class="fas fa-edit"></i> Edit
          </button>
        ` : ''}
      `;
      modalBody.appendChild(div);
    });
    
    modal.show();
  }
})();