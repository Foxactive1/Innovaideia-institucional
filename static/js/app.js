// static/js/app.js
(function() {
    // Loader
    const loader = document.getElementById('inv-loader');
    window.addEventListener('load', () => {
        setTimeout(() => loader.classList.add('hidden'), 400);
    });

    // Navbar scroll
    const navbar = document.getElementById('invNavbar');
    const backTop = document.getElementById('invBackTop');
    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY > 60;
        navbar.classList.toggle('scrolled', scrolled);
        backTop.classList.toggle('visible', scrolled);
    });

    // Mobile menu
    const hamburger = document.getElementById('invHamburger');
    const navLinks = document.getElementById('invNavLinks');
    const overlay = document.getElementById('invNavOverlay');

    function closeMenu() {
        navLinks.classList.remove('open');
        overlay.classList.remove('show');
        hamburger.setAttribute('aria-expanded', 'false');
    }

    hamburger.addEventListener('click', () => {
        const isOpen = navLinks.classList.toggle('open');
        overlay.classList.toggle('show', isOpen);
        hamburger.setAttribute('aria-expanded', isOpen);
    });
    overlay.addEventListener('click', closeMenu);
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            if (navLinks.classList.contains('open')) closeMenu();
        });
    });

    // Active nav link on scroll
    const sections = document.querySelectorAll('section[id]');
    const navAnchors = navLinks.querySelectorAll('a[href^="#"]');
    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(sec => {
            const top = sec.offsetTop - 120;
            if (window.scrollY >= top) current = sec.getAttribute('id');
        });
        navAnchors.forEach(a => {
            a.classList.toggle('active', a.getAttribute('href') === '#' + current);
        });
    });

    // Animate on scroll
    const animElements = document.querySelectorAll('.inv-animate-on-scroll');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
    animElements.forEach(el => observer.observe(el));

    // Counter animation
    const counterEls = document.querySelectorAll('.inv-num[data-count]');
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.getAttribute('data-count'));
                const duration = 1800;
                const start = performance.now();

                function update(now) {
                    const elapsed = now - start;
                    const progress = Math.min(elapsed / duration, 1);
                    const eased = 1 - Math.pow(1 - progress, 3);
                    el.textContent = Math.floor(eased * target) + '+';
                    if (progress < 1) requestAnimationFrame(update);
                    else el.textContent = target + '+';
                }
                requestAnimationFrame(update);
                counterObserver.unobserve(el);
            }
        });
    }, { threshold: 0.6 });
    counterEls.forEach(el => counterObserver.observe(el));
})();