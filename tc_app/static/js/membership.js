document.addEventListener('DOMContentLoaded', function() {
    const profileInput = document.getElementById('profile_image');
    const previewImage = document.getElementById('previewImage');
    const form = document.querySelector('form');

    // Image preview functionality
    profileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            if (file.size > 5 * 1024 * 1024) { // 5MB limit
                alert('File size should not exceed 5MB');
                this.value = '';
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
            }
            reader.readAsDataURL(file);
        }
    });

    // Membership card selection
    const membershipCards = document.querySelectorAll('.membership-card');
    membershipCards.forEach(card => {
        card.addEventListener('click', function() {
            const radio = this.querySelector('input[type="radio"]');
            radio.checked = true;
            
            // Remove active class from all cards
            membershipCards.forEach(c => c.classList.remove('active'));
            // Add active class to selected card
            this.classList.add('active');
        });
    });

    // Handle form submission
    const membershipForm = document.getElementById('membershipForm');
    if (membershipForm) {
        membershipForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate required fields
            const requiredFields = {
                'full_name': 'Full Name',
                'email': 'Email Address',
                'membership_type': 'Membership Type',
                'terms': 'Terms and Conditions'
            };
            
            let isValid = true;
            const errors = [];
            
            Object.entries(requiredFields).forEach(([fieldId, fieldName]) => {
                const element = document.getElementById(fieldId);
                if (!element.value || (element.type === 'checkbox' && !element.checked)) {
                    isValid = false;
                    errors.push(fieldName);
                    element.classList.add('error');
                }
            });
            
            if (!isValid) {
                showMessage('Please fill in all required fields: ' + errors.join(', '), 'error');
                return;
            }
            
            // Submit the form if validation passes
            membershipForm.submit();
        });
    }
    
    // Show messages function
    function showMessage(message, type) {
        const messagesContainer = document.querySelector('.messages');
        if (!messagesContainer) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        messageElement.textContent = message;
        
        messagesContainer.appendChild(messageElement);
        
        // Auto-remove message after 5 seconds
        setTimeout(() => {
            messageElement.remove();
        }, 5000);
    }
});