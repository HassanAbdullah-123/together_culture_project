function joinWaitlist(eventId) {
    fetch(`/api/events/${eventId}/waitlist/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('You have been added to the waitlist. We will notify you when a spot becomes available.');
            // Optionally update the button
            const button = document.querySelector(`[data-event-id="${eventId}"] .btn-waitlist`);
            button.innerHTML = '<i class="fas fa-check"></i> On Waitlist';
            button.disabled = true;
        } else {
            alert('Could not join waitlist. Please try again later.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again later.');
    });
} 