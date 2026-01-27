document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.verification-form');
    const fileInput = document.getElementById('identity_file');
    const phoneInput = document.getElementById('phone');
    
    // Phone number validation
    phoneInput.addEventListener('input', function() {
        let value = this.value.replace(/\D/g, '');
        if (value.length > 10) {
            value = value.substring(0, 10);
        }
        this.value = value;
    });
    
    // File validation
    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const maxSize = 5 * 1024 * 1024; // 5MB
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
            
            if (file.size > maxSize) {
                alert('File size must be less than 5MB');
                this.value = '';
                return;
            }
            
            if (!allowedTypes.includes(file.type)) {
                alert('Only JPG, PNG, and PDF files are allowed');
                this.value = '';
                return;
            }
        }
    });
    
    // Form submission
    form.addEventListener('submit', function(e) {
        const submitBtn = form.querySelector('.submit-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';
        
        // Re-enable button after 5 seconds in case of error
        setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Verification';
        }, 5000);
    });
    
    // Input animations
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
    });
});