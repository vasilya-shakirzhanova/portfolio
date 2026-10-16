const menuButton=document.querySelector('.menu-toggle');
const mobileMenu=document.querySelector('.mobile-menu');
function closeMenu(){menuButton?.setAttribute('aria-expanded','false');mobileMenu?.classList.remove('is-open');}
menuButton?.addEventListener('click',()=>{const open=menuButton.getAttribute('aria-expanded')!=='true';menuButton.setAttribute('aria-expanded',String(open));mobileMenu.classList.toggle('is-open',open);});
mobileMenu?.querySelectorAll('a').forEach(link=>link.addEventListener('click',closeMenu));
document.addEventListener('keydown',event=>{if(event.key==='Escape')closeMenu();});
const dialog=document.querySelector('.lightbox');
const image=dialog?.querySelector('img');
const caption=dialog?.querySelector('.lightbox__caption');
const imageArea=dialog?.querySelector('.lightbox__image');
const zoomButton=dialog?.querySelector('[data-zoom]');
let previousFocus=null;
document.querySelectorAll('[data-lightbox]').forEach(button=>button.addEventListener('click',()=>{previousFocus=button;image.src=button.dataset.lightbox;image.style.setProperty('--screen-width',Math.min(Number(button.dataset.width)||1600,1920)+'px');image.alt=button.dataset.caption;image.dataset.phone=button.dataset.phone||'false';caption.textContent=button.dataset.caption;imageArea.classList.remove('is-large');zoomButton.textContent='Увеличить';zoomButton.setAttribute('aria-pressed','false');dialog.showModal();document.body.style.overflow='hidden';}));
dialog?.querySelector('[data-close]')?.addEventListener('click',()=>dialog.close());
dialog?.addEventListener('click',event=>{if(event.target===dialog){const bounds=dialog.getBoundingClientRect();if(event.clientX<bounds.left||event.clientX>bounds.right||event.clientY<bounds.top||event.clientY>bounds.bottom)dialog.close();}});
dialog?.addEventListener('close',()=>{document.body.style.overflow='';previousFocus?.focus();image.removeAttribute('src');});
zoomButton?.addEventListener('click',()=>{const large=imageArea.classList.toggle('is-large');zoomButton.textContent=large?'Вписать':'Увеличить';zoomButton.setAttribute('aria-pressed',String(large));});
