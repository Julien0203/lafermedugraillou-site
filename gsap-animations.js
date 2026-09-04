/**
 * La Ferme du Graillou – GSAP Animations
 * ScrollTrigger + hero entrance + parallax + micro-interactions
 */

gsap.registerPlugin(ScrollTrigger);
gsap.defaults({ ease: 'power3.out' });

const mm = gsap.matchMedia();

mm.add(
  {
    reduceMotion: '(prefers-reduced-motion: reduce)',
    motionOK:     '(prefers-reduced-motion: no-preference)',
  },
  (ctx) => {
    const { reduceMotion } = ctx.conditions;

    /* ── Reduced motion : tout visible immédiatement ── */
    if (reduceMotion) {
      gsap.set(
        '[data-animate], .hero-anim, .page-hero-eyebrow, .page-hero-title, .page-hero-sub, .hero-scroll-cue',
        { clearProps: 'all' }
      );
      return;
    }

    /* ─────────────────────────────────────────────────────
       HERO ENTRANCE (index.html)
       Stagger timeline : eyebrow → titre → script → sub → boutons
    ───────────────────────────────────────────────────── */
    const heroAnims = gsap.utils.toArray('.hero-anim');
    if (heroAnims.length) {
      const heroTl = gsap.timeline({ delay: 0.2 });
      heroTl.fromTo(
        heroAnims,
        { opacity: 0, y: 32 },
        { opacity: 1, y: 0, duration: 0.95, stagger: 0.16 }
      );
    }

    /* Scroll cue – fade in puis bobbing continu */
    const scrollCue = document.querySelector('.hero-scroll-cue');
    if (scrollCue) {
      gsap.fromTo(scrollCue,
        { autoAlpha: 0, y: 0 },
        {
          autoAlpha: 1,
          duration: 0.8,
          delay: 1.4,
          onComplete() {
            gsap.to(scrollCue, {
              y: 10,
              duration: 1.3,
              ease: 'sine.inOut',
              repeat: -1,
              yoyo: true,
            });
          },
        }
      );
    }

    /* Parallax subtil sur l'image hero */
    const heroImg = document.querySelector('.hero-img');
    if (heroImg) {
      gsap.to(heroImg, {
        yPercent: 20,
        ease: 'none',
        scrollTrigger: {
          trigger: '.hero',
          start: 'top top',
          end: 'bottom top',
          scrub: 1.5,
        },
      });
    }

    /* ─────────────────────────────────────────────────────
       PAGE HERO (sous-pages : histoire, exploitation, etc.)
    ───────────────────────────────────────────────────── */
    const pageHeroEyebrow = document.querySelector('.page-hero-eyebrow');
    const pageHeroTitle   = document.querySelector('.page-hero-title');
    const pageHeroSub     = document.querySelector('.page-hero-sub');

    if (pageHeroTitle) {
      const els = [pageHeroEyebrow, pageHeroTitle, pageHeroSub].filter(Boolean);
      gsap.fromTo(
        els,
        { opacity: 0, y: 28 },
        { opacity: 1, y: 0, duration: 0.85, stagger: 0.14, delay: 0.3 }
      );
    }

    /* ─────────────────────────────────────────────────────
       SCROLL REVEAL – [data-animate]
       Remplace l'IntersectionObserver CSS
    ───────────────────────────────────────────────────── */
    gsap.utils.toArray('[data-animate]').forEach(el => {
      const dir      = el.dataset.animate;
      const delayStr = getComputedStyle(el).getPropertyValue('--anim-delay').trim();
      const delay    = delayStr ? parseFloat(delayStr) / 1000 : 0;

      const from = { opacity: 0 };
      const to   = { opacity: 1, duration: 0.85, delay, ease: 'power3.out' };

      /* Sous 768px : pas de translation horizontale (évite le débordement
         latéral). Les révélations latérales deviennent verticales. */
      const isNarrow = window.matchMedia('(max-width: 767px)').matches;

      if (dir === 'fade-up')    { from.y = 44;   to.y = 0; }
      if (dir === 'fade-down')  { from.y = -44;  to.y = 0; }
      if (dir === 'fade-left')  { if (isNarrow) { from.y = 44; to.y = 0; } else { from.x = 56;  to.x = 0; } }
      if (dir === 'fade-right') { if (isNarrow) { from.y = 44; to.y = 0; } else { from.x = -56; to.x = 0; } }
      if (dir === 'scale')      { from.scale = 0.92; to.scale = 1; }

      gsap.fromTo(el, from, {
        ...to,
        scrollTrigger: {
          trigger: el,
          start: 'top 90%',
          once: true,
        },
      });
    });

    /* ─────────────────────────────────────────────────────
       COUNTER ANIMATION – .stat-num[data-count]
       Remplace le countObs RAF
    ───────────────────────────────────────────────────── */
    gsap.utils.toArray('.stat-num[data-count]').forEach(el => {
      const target = parseInt(el.dataset.count, 10);
      const proxy  = { val: 0 };

      gsap.to(proxy, {
        val: target,
        duration: 1.8,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: el,
          start: 'top 85%',
          once: true,
        },
        onUpdate() {
          el.textContent = Math.round(proxy.val);
        },
      });
    });

    /* ─────────────────────────────────────────────────────
       PAGE HERO – parallax image sous-pages
    ───────────────────────────────────────────────────── */
    const pageHeroImg = document.querySelector('.page-hero-img');
    if (pageHeroImg) {
      gsap.to(pageHeroImg, {
        yPercent: 15,
        ease: 'none',
        scrollTrigger: {
          trigger: '.page-hero',
          start: 'top top',
          end: 'bottom top',
          scrub: 1.5,
        },
      });
    }

    /* ─────────────────────────────────────────────────────
       BOUTONS – micro-interactions hover
    ───────────────────────────────────────────────────── */
    gsap.utils.toArray('.btn-primary, .btn-ghost, .btn-secondary, .btn-outline').forEach(btn => {
      btn.addEventListener('mouseenter', () =>
        gsap.to(btn, { scale: 1.045, duration: 0.18, ease: 'power2.out', overwrite: 'auto' })
      );
      btn.addEventListener('mouseleave', () =>
        gsap.to(btn, { scale: 1, duration: 0.22, ease: 'power2.inOut', overwrite: 'auto' })
      );
    });

    /* ─────────────────────────────────────────────────────
       SECTION TRANSHUMANCE – reveal progressif du texte
    ───────────────────────────────────────────────────── */
    const transhuText = document.querySelector('.section-transhumance .split-text');
    const transhuImgs = document.querySelector('.section-transhumance .split-image, .section-transhumance .transhu-duo');
    if (transhuText && transhuImgs) {
      const narrowTr = window.matchMedia('(max-width: 767px)').matches;
      gsap.fromTo(transhuImgs,
        narrowTr ? { opacity: 0, y: 44 } : { opacity: 0, x: -60 },
        {
          opacity: 1, x: 0, y: 0, duration: 1,
          scrollTrigger: { trigger: transhuText, start: 'top 82%', once: true },
        }
      );
    }

    /* ─────────────────────────────────────────────────────
       STATS BAND – stagger sur les chiffres
    ───────────────────────────────────────────────────── */
    const statItems = gsap.utils.toArray('.stats-band .stat-item');
    if (statItems.length) {
      gsap.fromTo(statItems,
        { opacity: 0, y: 30 },
        {
          opacity: 1, y: 0, duration: 0.75,
          stagger: { each: 0.1, from: 'start' },
          scrollTrigger: {
            trigger: '.stats-band',
            start: 'top 85%',
            once: true,
          },
        }
      );
    }

  }
);
