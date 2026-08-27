(() => {
  "use strict";

  /* ===========================================================
     SITE CONFIG — редактируйте здесь, когда появятся точные данные
     =========================================================== */
  const CONFIG = {
    whatsappNumber: "77771221309", // +7 777 122 1309, без "+" и пробелов
    whatsappDefaultText: "Здравствуйте! Хочу узнать подробнее о хранении в Fresh Storage Center.",
    address: "Алматинская область — точный адрес уточняется",
    email: "info@fsc.kz",
    instagram: "https://instagram.com/fsc.kz",
    telegram: "https://t.me/fsc_kz",
  };

  const waLink = (text) =>
    `https://wa.me/${CONFIG.whatsappNumber}?text=${encodeURIComponent(text)}`;

  document.querySelectorAll(".wa-link").forEach((el) => {
    el.href = waLink(CONFIG.whatsappDefaultText);
  });

  document.querySelectorAll('[data-config="address"]').forEach((el) => (el.textContent = CONFIG.address));
  document.querySelectorAll('[data-config="email"]').forEach((el) => {
    el.textContent = CONFIG.email;
    el.href = `mailto:${CONFIG.email}`;
  });
  document.querySelectorAll('[data-config="instagram"]').forEach((el) => (el.href = CONFIG.instagram));
  document.querySelectorAll('[data-config="telegram"]').forEach((el) => (el.href = CONFIG.telegram));

  /* ===========================================================
     Header scroll state
     =========================================================== */
  const header = document.getElementById("header");
  const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 12);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ===========================================================
     Mobile nav
     =========================================================== */
  const navToggle = document.getElementById("navToggle");
  const nav = document.getElementById("nav");
  navToggle.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    navToggle.classList.toggle("is-open", open);
    navToggle.setAttribute("aria-expanded", String(open));
  });
  nav.querySelectorAll("a").forEach((a) =>
    a.addEventListener("click", () => {
      nav.classList.remove("is-open");
      navToggle.classList.remove("is-open");
      navToggle.setAttribute("aria-expanded", "false");
    })
  );

  /* ===========================================================
     Scroll reveal animation (only hide content once we can reveal it)
     =========================================================== */
  const revealEls = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window && revealEls.length) {
    document.documentElement.classList.add("js-ready");
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -60px 0px" }
    );
    revealEls.forEach((el) => io.observe(el));
  }

  /* ===========================================================
     Cursor spotlight reveal effect on featured visuals
     =========================================================== */
  document.querySelectorAll(".reveal-card").forEach((card) => {
    card.addEventListener("pointermove", (e) => {
      const rect = card.getBoundingClientRect();
      card.style.setProperty("--mx", `${e.clientX - rect.left}px`);
      card.style.setProperty("--my", `${e.clientY - rect.top}px`);
    });
  });

  /* ===========================================================
     Contact form → WhatsApp handoff
     =========================================================== */
  const form = document.getElementById("contactForm");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const data = new FormData(form);
    const name = (data.get("name") || "").toString().trim();
    const phone = (data.get("phone") || "").toString().trim();
    const service = (data.get("service") || "").toString();
    const message = (data.get("message") || "").toString().trim();

    const lines = [
      "Здравствуйте! Хочу оставить заявку на сайте FSC.KZ.",
      `Имя: ${name}`,
      `Телефон: ${phone}`,
      `Услуга: ${service}`,
    ];
    if (message) lines.push(`Сообщение: ${message}`);

    window.open(waLink(lines.join("\n")), "_blank", "noopener");
  });

  /* ===========================================================
     Footer year
     =========================================================== */
  document.getElementById("year").textContent = new Date().getFullYear();
})();
