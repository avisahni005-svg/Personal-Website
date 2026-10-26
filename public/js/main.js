// Play videos only while they are on screen, and make "Top ↑" scroll smoothly.
(() => {
  const vids = document.querySelectorAll("video[data-autoplay]");
  // Start fetching videos only after the page's images have arrived, so they never compete with them.
  const whenLoaded = (fn) => (document.readyState === "complete" ? fn() : window.addEventListener("load", fn, { once: true }));
  whenLoaded(() => {
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        const v = e.target;
        if (e.isIntersecting) {
          if (v.preload === "none") v.preload = "auto";
          v.play().catch(() => {});
        } else {
          v.pause();
        }
      }
    }, { rootMargin: "1500px 0px" });
    vids.forEach((v) => io.observe(v));
  } else {
    vids.forEach((v) => v.play().catch(() => {}));
  }
  });

  document.querySelectorAll("[data-top]").forEach((a) =>
    a.addEventListener("click", (ev) => {
      ev.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    })
  );

  // Slideshows: fade between spreads, preload neighbours, arrows / click / swipe / keys.
  document.querySelectorAll("[data-slides]").forEach((root) => {
    const imgs = [...root.querySelectorAll(".stage img")];
    const count = root.querySelector(".count");
    const n = imgs.length;
    let i = 0;
    const load = (k) => {
      const im = imgs[(k + n) % n];
      if (im.dataset.src) { im.src = im.dataset.src; delete im.dataset.src; }
    };
    // Crossfade: the new slide fades in on top while the old one stays fully visible underneath, then is released.
    let releaseTimer = null;
    const go = (k) => {
      const next = (k + n) % n;
      if (next === i) return;
      imgs.forEach((im) => { if (im !== imgs[i]) im.classList.remove("prev"); });
      imgs[i].classList.remove("on");
      imgs[i].classList.add("prev");
      i = next;
      load(i); load(i + 1); load(i + 2); load(i - 1);
      imgs[i].classList.remove("prev");
      imgs[i].classList.add("on");
      count.textContent = `${i + 1} / ${n}`;
      clearTimeout(releaseTimer);
      releaseTimer = setTimeout(() => imgs.forEach((im) => im.classList.remove("prev")), 520);
    };
    root.querySelector("[data-prev]").addEventListener("click", () => go(i - 1));
    root.querySelector("[data-next]").addEventListener("click", () => go(i + 1));
    const stage = root.querySelector(".stage");
    stage.addEventListener("click", (e) => {
      const r = stage.getBoundingClientRect();
      go(e.clientX - r.left < r.width / 3 ? i - 1 : i + 1);
    });
    root.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") { e.preventDefault(); go(i + 1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); go(i - 1); }
    });
    let x0 = null;
    stage.addEventListener("touchstart", (e) => { x0 = e.touches[0].clientX; }, { passive: true });
    stage.addEventListener("touchend", (e) => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 40) go(dx < 0 ? i + 1 : i - 1);
      x0 = null;
    });
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver((es) => { if (es[0].isIntersecting) { load(1); load(2); load(3); io.disconnect(); } }, { rootMargin: "2000px 0px" });
      io.observe(root);
    }

    // Auto-cycle: one slide per second while the slideshow is on screen, paused while the pointer is over it.
    const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!reduce) {
      let hover = false, visible = false, timer = null;
      const tick = () => { if (!hover && visible && !document.hidden) go(i + 1); };
      const start = () => { clearInterval(timer); timer = setInterval(tick, 1000); };
      root.addEventListener("mouseenter", () => { hover = true; });
      root.addEventListener("mouseleave", () => { hover = false; start(); });
      root.addEventListener("click", start);          // restart the 1s clock after a manual change
      if ("IntersectionObserver" in window) {
        new IntersectionObserver((es) => { visible = es[0].isIntersecting; }, { threshold: 0.25 }).observe(root);
      } else {
        visible = true;
      }
      start();
    }
  });

  // Unmute buttons (Hyperyouth). Videos always start muted; only one plays sound at a time.
  const btns = document.querySelectorAll("[data-unmute]");
  btns.forEach((btn) => {
    const v = btn.parentElement.querySelector("video");
    btn.addEventListener("click", () => {
      const on = v.muted;                       // currently muted -> turn sound on
      document.querySelectorAll("video[data-audio]").forEach((o) => { o.muted = true; });
      btns.forEach((b) => { b.setAttribute("aria-pressed", "false"); b.setAttribute("aria-label", "Unmute video"); });
      if (on) {
        v.muted = false;
        btn.setAttribute("aria-pressed", "true");
        btn.setAttribute("aria-label", "Mute video");
        v.play().catch(() => {});
      }
    });
  });

  // Playground: each press of the spacebar (or tap) drops the next image, at a random spot, on top of the others. Cards can be dragged.
  const stage = document.getElementById("pg-stage");
  if (stage) {
    let items = [];
    try { items = JSON.parse(stage.dataset.items || "[]"); } catch (e) { items = []; }
    let bag = [], z = 1;
    const cards = [];
    const refill = () => {
      bag = items.map((_, k) => k);
      for (let k = bag.length - 1; k > 0; k--) { const r = Math.floor(Math.random() * (k + 1)); [bag[k], bag[r]] = [bag[r], bag[k]]; }
    };
    const place = (card, it) => {
      const sw = stage.clientWidth, sh = stage.clientHeight;
      const ratio = it.w / it.h;
      let h = Math.min(sh * (0.55 + Math.random() * 0.3), (sw * (0.3 + Math.random() * 0.2)) / ratio);
      let w = h * ratio;
      if (w > sw * 0.7) { w = sw * 0.7; h = w / ratio; }
      card.style.width = w + "px"; card.style.height = h + "px";
      card.style.left = Math.random() * Math.max(0, sw - w) + "px";
      card.style.top = Math.random() * Math.max(0, sh - h) + "px";
    };
    const front = (card) => { card.style.zIndex = ++z; };
    const make = (it) => {
      const card = document.createElement("div");
      card.className = "pg-card pop";
      let el;
      if (it.v) { el = document.createElement("video"); el.src = it.s; el.muted = true; el.loop = true; el.autoplay = true; el.playsInline = true; }
      else { el = document.createElement("img"); el.src = it.s; el.alt = ""; el.draggable = false; }
      card.appendChild(el);
      card.addEventListener("pointerdown", (e) => {
        if (e.button !== undefined && e.button !== 0) return;
        e.preventDefault();
        front(card); card.classList.add("drag");
        card.setPointerCapture(e.pointerId);
        const dx = e.clientX - card.offsetLeft, dy = e.clientY - card.offsetTop;
        const move = (ev) => {
          const sw = stage.clientWidth, sh = stage.clientHeight, w = card.offsetWidth, h = card.offsetHeight;
          card.style.left = Math.min(sw - w * 0.25, Math.max(-w * 0.75, ev.clientX - dx)) + "px";
          card.style.top = Math.min(sh - h * 0.25, Math.max(-h * 0.75, ev.clientY - dy)) + "px";
        };
        const up = () => { card.classList.remove("drag"); card.removeEventListener("pointermove", move); card.removeEventListener("pointerup", up); card.removeEventListener("pointercancel", up); };
        card.addEventListener("pointermove", move); card.addEventListener("pointerup", up); card.addEventListener("pointercancel", up);
      });
      return card;
    };
    const next = () => {
      if (!items.length) return;
      if (!bag.length) refill();
      const it = items[bag.pop()];
      let card;
      if (cards.length >= items.length) { card = cards.shift(); stage.removeChild(card); }   // all shown once: recycle the oldest
      card = make(it);
      place(card, it); front(card); stage.appendChild(card); cards.push(card);
    };
    refill();
    document.addEventListener("keydown", (e) => {
      if (e.code !== "Space" && e.key !== " ") return;
      const t = e.target; if (t && /^(INPUT|TEXTAREA|SELECT|BUTTON)$/.test(t.tagName)) return;
      e.preventDefault(); if (!e.repeat) next();
    });
    stage.addEventListener("click", (e) => { if (e.target === stage && window.matchMedia("(pointer: coarse)").matches) next(); });
    // warm the cache so the first presses are instant
    items.slice(0, 6).forEach((it) => { if (!it.v) { const im = new Image(); im.src = it.s; } });
  }
})();
