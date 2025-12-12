(function(){
  const clearBtn = document.getElementById('clearLocal');
  const loginBtn = document.getElementById('login');
  const form = document.createElement('form');
  // Prevent default Enter key submission causing navigation quirks
  form.addEventListener('submit', (e)=> e.preventDefault());

  if (clearBtn){
    clearBtn.addEventListener('click', ()=>{ localStorage.removeItem('access_token'); alert('Token cleared'); });
  }
  if (loginBtn){
    loginBtn.addEventListener('click', async ()=>{
      const username_or_email = document.getElementById('username_or_email').value.trim();
      const password = document.getElementById('password').value;
      const messages = document.getElementById('msg');
      const showMessage = (type, text)=>{
        messages.textContent = text;
        messages.className = type === 'ok' ? 'msg success' : 'msg error';
      };
      messages.innerHTML = '';
      try{
        const r = await fetch('/users/login', {
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body: JSON.stringify({username_or_email, password})
        });
        const txt = await r.text();
        if (!r.ok){ showMessage('err', txt || ('Error '+r.status)); return; }
        const j = JSON.parse(txt);
        if (j.access_token) localStorage.setItem('access_token', j.access_token);
        showMessage('ok','Logged in — redirecting...');
        setTimeout(()=>{ window.location.href = '/static/calculations.html'; }, 600);
      }catch(err){ showMessage('err','Network error'); }
    });
  }
})();
