function scrollToSection(sectionId) {
  const section = document.getElementById(sectionId);
  if (section) {
    section.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    });
  }
}

function confirmPayment(subscriptionId) {
  console.log('Confirming payment for subscription ID:', subscriptionId);
  if (!subscriptionId) {
    alert('Invalid subscription ID');
    return;
  }
  fetch(`/subscription/${subscriptionId}`, {
    method: 'POST'
  })
  .then(response => {
    console.log('Response status:', response.status);
    return response.json();
  })
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
    alert('An error occurred while confirming payment');
  });
}