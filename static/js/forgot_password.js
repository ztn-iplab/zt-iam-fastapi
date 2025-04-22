document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('forgot-password-form');
    const errorDiv = document.getElementById('forgot-error');
    const successDiv = document.getElementById('forgot-success');
  
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      errorDiv.textContent = '';
      successDiv.textContent = '';
  
      const identifier = form.identifier.value;
  
      try {
        const res = await fetch('/api/auth/forgot-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ identifier })
        });
  
        const data = await res.json();
        if (res.ok) {
          successDiv.textContent = data.message;
          form.reset();
        } else {
          errorDiv.textContent = data.error || 'Something went wrong.';
        }
      } catch (err) {
        errorDiv.textContent = 'Network error.';
      }
    });
  });
  