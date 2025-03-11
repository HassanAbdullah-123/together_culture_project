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
    const membershipCards = document.querySelectorAll('.membership-option label');
    
    membershipCards.forEach(card => {
        card.addEventListener('click', function(e) {
            const radio = this.previousElementSibling;
            if (radio) {
                radio.checked = true;
            }
        });
    });

    // Form submission handling
    const membershipForm = document.getElementById('membershipForm');
    if (membershipForm) {
        membershipForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate membership selection
            const selectedMembership = document.querySelector('input[name="membership_type"]:checked');
            if (!selectedMembership) {
                showMessage('Please select a membership type', 'error');
                return;
            }
            
            // Validate required fields
            const requiredFields = {
                'full_name': 'Full Name',
                'email': 'Email Address',
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
                } else {
                    element.classList.remove('error');
                }
            });
            
            if (!isValid) {
                showMessage('Please fill in all required fields: ' + errors.join(', '), 'error');
                return;
            }

            // Show loading message
            showMessage('Updating your membership...', 'info');
            
            // Submit the form
            this.submit();
        });
    }
});

// Enhanced message display function
function showMessage(message, type = 'info') {
    // Create messages container if it doesn't exist
    let messagesContainer = document.querySelector('.messages');
    if (!messagesContainer) {
        messagesContainer = document.createElement('div');
        messagesContainer.className = 'messages';
        const formElement = document.querySelector('.membership-form');
        formElement.insertBefore(messagesContainer, formElement.firstChild);
    }
    
    // Create message element
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}`;
    
    // Add icon based on message type
    const icon = getMessageIcon(type);
    messageElement.innerHTML = `
        <div class="message-content">
            <span class="message-icon">${icon}</span>
            <span class="message-text">${message}</span>
        </div>
        <button class="message-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    // Add to container
    messagesContainer.appendChild(messageElement);
    
    // Animate in
    setTimeout(() => messageElement.classList.add('show'), 10);
    
    // Auto-remove after delay (except for errors)
    if (type !== 'error') {
        setTimeout(() => {
            messageElement.classList.remove('show');
            setTimeout(() => messageElement.remove(), 300);
        }, 5000);
    }
}

// Helper function to get message icons
function getMessageIcon(type) {
    switch(type) {
        case 'success':
            return '✓';
        case 'error':
            return '!';
        case 'info':
            return 'i';
        case 'warning':
            return '⚠';
        default:
            return '';
    }
}