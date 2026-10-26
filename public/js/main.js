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
    const go = (k) => {
      imgs[i].classList.remove("on");
      i = (k + n) % n;
      load(i); load(i + 1); load(i + 2); load(i - 1);
      imgs[i].classList.add("on");
      count.textContent = `${i + 1} / ${n}`;
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
  });
})();
