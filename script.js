// Mobile menu toggle
const toggle = document.querySelector('.menu-toggle');
const menu = document.getElementById('mobile-menu');
toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  menu.hidden = !open;
});

// Trap 16: visible for half a second after load, then hidden by script
document.querySelectorAll('[data-hide-after]').forEach((el) => {
  setTimeout(() => { el.hidden = true; }, 500);
});

// Lazy-loaded control: added to the footer only once its slot scrolls into view
const slot = document.getElementById('lazy-slot');
const observer = new IntersectionObserver((entries) => {
  if (!entries[0].isIntersecting) return;
  const link = document.createElement('a');
  link.setAttribute('href', 'control/lazy-loaded-newsletter');
  link.textContent = "Wizard's newsletter";
  slot.append(link);
  observer.disconnect();
});
observer.observe(slot);

// Contact form: no backend, so just confirm receipt
document.getElementById('contact-form').addEventListener('submit', (event) => {
  event.preventDefault();
  event.target.querySelector('.form-note').textContent = 'Thank you. Corvin will reply within two working days.';
  event.target.reset();
});
