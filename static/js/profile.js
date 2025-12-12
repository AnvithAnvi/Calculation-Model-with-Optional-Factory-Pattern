(function(){
  function getToken(){ return (localStorage.getItem('access_token') || '').trim(); }
  const clearBtn = document.getElementById('clearLocal');
  if (clearBtn){ clearBtn.addEventListener('click', ()=>{ localStorage.removeItem('access_token'); alert('Token cleared'); }); }

  async function authFetch(url, opts={}){
    const token = getToken();
    if (!token) return { ok:false, status:401, text:'Please login first.' };
    opts.headers = opts.headers || {};
    opts.headers['Authorization'] = token.startsWith('Bearer ') ? token : 'Bearer '+token;
    const r = await fetch(url, opts);
    const text = await r.text();
    try{ return { ok: r.ok, status: r.status, json: JSON.parse(text), text }; }catch(e){ return { ok: r.ok, status: r.status, text }; }
  }

  async function loadProfile(){
    const res = await authFetch('/users/me');
    const msgP = document.querySelector('.msg.profile');
    if (!res.ok){ msgP.textContent = 'Please login to manage your profile.'; msgP.className='msg profile error'; setTimeout(()=>{ window.location.href='/static/login.html'; }, 800); return; }
    const j = res.json || {};
    const emailEl = document.getElementById('email');
    const usernameEl = document.getElementById('username');
    if (emailEl) emailEl.value = j.email || '';
    if (usernameEl) usernameEl.value = j.username || '';
  }
  window.addEventListener('load', loadProfile);

  const saveBtn = document.getElementById('save');
  if (saveBtn){
    saveBtn.addEventListener('click', async ()=>{
      const email = document.getElementById('email').value.trim();
      const username = document.getElementById('username').value.trim();
      const msgP = document.querySelector('.msg.profile');
      msgP.textContent = '';
      const r = await authFetch('/users/me', { method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ email, username }) });
      if (!r.ok){ msgP.textContent = 'Error '+r.status+': '+(r.text||''); msgP.className='msg profile error'; return; }
      msgP.textContent = 'Profile updated'; msgP.className='msg profile success';
    });
  }

  const changeBtn = document.getElementById('changePassword');
  if (changeBtn){
    changeBtn.addEventListener('click', async ()=>{
      const current_password = document.getElementById('current_password').value;
      const new_password = document.getElementById('new_password').value;
      const msgPW = document.querySelector('.msg.password');
      msgPW.textContent = '';
      const r = await authFetch('/users/me/password', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ current_password: current_password, new_password }) });
      if (!r.ok){ msgPW.textContent = 'Error '+r.status+': '+(r.text||''); msgPW.className='msg password error'; return; }
      msgPW.textContent = 'Password changed'; msgPW.className='msg password success';
      // Clear token to require re-login after password change
      localStorage.removeItem('access_token');
      setTimeout(()=>{ window.location.href = '/static/login.html'; }, 1000);
    });
  }
})();
