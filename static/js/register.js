(function(){
  const clearBtn = document.getElementById('clearLocal');
  const regBtn = document.getElementById('register');
  if (clearBtn){
    clearBtn.addEventListener('click', ()=>{ localStorage.removeItem('access_token'); alert('Token cleared'); });
  }
  if (regBtn){
    regBtn.addEventListener('click', async ()=>{
      const username = document.getElementById('username').value.trim();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const messages = document.getElementById('msg');
      const showMessage = (type, text)=>{
        messages.textContent = text;
        messages.className = type === 'ok' ? 'msg success' : 'msg error';
      };
      messages.innerHTML = '';
      try{
        const r = await fetch('/users/register', {
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body: JSON.stringify({ username, email, password })
        });
        if (!r.ok){ 
          const txt = await r.text();
          showMessage('err', txt || ('Error '+r.status)); 
          return; 
        }
        const data = await r.json();
        if (data.access_token) {
          localStorage.setItem('access_token', data.access_token);
        }
        showMessage('ok','Registered — redirecting to calculator...');
        setTimeout(()=>{ window.location.href = '/static/calculations.html'; }, 600);
      }catch(err){ showMessage('err','Network error'); }
    });
  }
})();
