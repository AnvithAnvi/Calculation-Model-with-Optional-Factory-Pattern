// Password Toggle Visibility
function initPasswordToggles() {
  document.querySelectorAll('.password-toggle-wrapper').forEach(wrapper => {
    const input = wrapper.querySelector('input[type="password"], input[type="text"]');
    const toggle = wrapper.querySelector('.password-toggle');
    
    if (toggle && input) {
      toggle.addEventListener('click', function() {
        const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
        input.setAttribute('type', type);
        
        // Update icon
        this.innerHTML = type === 'password'
          ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>'
          : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>';
      });
    }
  });
}

// Password Strength Checker
function checkPasswordStrength(password) {
  let strength = 0;
  const feedback = [];
  
  if (password.length >= 8) {
    strength += 25;
    feedback.push('good length');
  } else {
    feedback.push('too short');
  }
  
  if (password.match(/[a-z]+/)) {
    strength += 25;
  }
  
  if (password.match(/[A-Z]+/)) {
    strength += 25;
    feedback.push('uppercase');
  }
  
  if (password.match(/[0-9]+/)) {
    strength += 15;
    feedback.push('numbers');
  }
  
  if (password.match(/[$@#&!]+/)) {
    strength += 10;
    feedback.push('special chars');
  }
  
  return { strength: Math.min(strength, 100), feedback };
}

function updatePasswordStrength(input, strengthBar, strengthText) {
  const password = input.value;
  const { strength, feedback } = checkPasswordStrength(password);
  
  strengthBar.style.width = strength + '%';
  
  let color, label;
  if (strength < 30) {
    color = '#ef4444';
    label = 'Weak';
  } else if (strength < 60) {
    color = '#f59e0b';
    label = 'Fair';
  } else if (strength < 80) {
    color = '#3b82f6';
    label = 'Good';
  } else {
    color = '#22c55e';
    label = 'Strong';
  }
  
  strengthBar.style.background = color;
  strengthText.textContent = password.length > 0 ? `${label} (${feedback.join(', ')})` : '';
}

function initPasswordStrength() {
  const strengthWrapper = document.getElementById('passwordStrength');
  if (!strengthWrapper) return;
  
  const passwordInput = document.getElementById('password');
  const strengthBar = strengthWrapper.querySelector('.strength-bar');
  const strengthText = strengthWrapper.querySelector('.strength-text');
  
  if (passwordInput && strengthBar && strengthText) {
    passwordInput.addEventListener('input', function() {
      updatePasswordStrength(this, strengthBar, strengthText);
    });
  }
}

// Initialize all features
document.addEventListener('DOMContentLoaded', function() {
  initPasswordToggles();
  initPasswordStrength();
});
