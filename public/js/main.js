// Play videos only while they are on screen, and make "Top ↑" scroll smoothly.
(() => {
  const vids = document.querySelectorAll("video[data-autoplay]");
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
    }, { rootMargin: "200px 0px" });
    vids.forEach((v) => io.observe(v));
  } else {
    vids.forEach((v) => v.play().catch(() => {}));
  }

  document.querySelectorAll("[data-top]").forEach((a) =>
    a.addEventListener("click", (ev) => {
      ev.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    })
  );
})();
