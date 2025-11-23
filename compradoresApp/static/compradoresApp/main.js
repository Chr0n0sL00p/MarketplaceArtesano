document.addEventListener('DOMContentLoaded', ()=> {
  // Fade-in messages
  document.querySelectorAll('.messages .msg').forEach(m => {
    m.style.opacity = 0;
    setTimeout(()=> m.style.opacity = 1, 80);
  });

  // Simple client validation for review rating
  const reviewForm = document.querySelector('.review-form');
  if (reviewForm) {
    reviewForm.addEventListener('submit', (e)=>{
      const rating = reviewForm.querySelector('[name=rating]');
      if (rating) {
        const val = parseInt(rating.value||0, 10);
        if (!(val >=1 && val <=5)) {
          e.preventDefault();
          alert('La calificación debe ser entre 1 y 5.');
        }
      }
    });
  }

  // Confirmation on remove favorite
  document.querySelectorAll('form[action*="toggle_favorite"]').forEach(f => {
    f.addEventListener('submit', (ev)=>{
      const ok = confirm('¿Seguro quieres cambiar tu favorito?');
      if (!ok) ev.preventDefault();
    });
  });

});
