(() => {
  "use strict";
  const t = window.SIMPANCLIP_I18N || {};
  const API = String(window.SIMPANCLIP_API || "").replace(/\/+$/, "");
  const form = document.getElementById("dl-form");
  if (!form) return;
  const input = document.getElementById("url");
  const goBtn = document.getElementById("go");
  const pasteBtn = document.getElementById("paste");
  const statusEl = document.getElementById("status");
  const resultEl = document.getElementById("result");

  const el = (tag, attrs = {}, ...kids) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") n.className = v;
      else if (k === "text") n.textContent = v;
      else n.setAttribute(k, v);
    }
    kids.forEach((c) => c && n.append(c));
    return n;
  };

  function setStatus(kind, text, spinner) {
    statusEl.hidden = !text;
    statusEl.className = "status" + (kind ? " " + kind : "");
    statusEl.replaceChildren();
    if (spinner) statusEl.append(el("span", { class: "spin", "aria-hidden": "true" }));
    statusEl.append(document.createTextNode(text || ""));
  }

  const fmtDuration = (s) => {
    if (!s) return "";
    const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
    const p = (n) => String(n).padStart(2, "0");
    return h ? `${h}:${p(m)}:${p(sec)}` : `${m}:${p(sec)}`;
  };

  function validUrl(v) {
    try {
      const u = new URL(v);
      return u.protocol === "http:" || u.protocol === "https:";
    } catch (_) { return false; }
  }

  function errorMessage(code) {
    return t["err_" + code] || t.err_failed || "Error";
  }

  function render(data, url) {
    resultEl.replaceChildren();
    const thumb = el("div", { class: "thumb" });
    if (data.thumbnail) {
      const img = el("img", { alt: "", referrerpolicy: "no-referrer", loading: "lazy" });
      img.src = data.thumbnail;
      img.addEventListener("error", () => thumb.replaceChildren());
      thumb.append(img);
    }
    const meta = [data.platform, fmtDuration(data.duration)].filter(Boolean).join(" · ");
    const opts = el("div", { class: "opts" });
    const mk = (q, label, cls) => {
      const href = `${API}/api/download?url=${encodeURIComponent(url)}&q=${encodeURIComponent(q)}`;
      const a = el("a", { class: "btn primary " + (cls || ""), href, rel: "noopener", text: label });
      a.addEventListener("click", () => setStatus("", t.processing, true));
      return a;
    };
    (data.qualities || []).forEach((q) =>
      opts.append(mk(q.id, q.id === "best" ? t.best : `MP4 ${q.id}p`))
    );
    if (data.audio) opts.append(mk("audio", "MP3", "audio"));
    const info = el(
      "div", { class: "info" },
      el("h2", { text: data.title || (data.images && data.images.length ? t.photos : "Video") }),
      el("p", { class: "meta", text: meta })
    );
    if (opts.childElementCount) info.append(el("p", { class: "opts-h", text: t.choose }), opts);
    const imgs = data.images || [];
    if (imgs.length) {
      const grid = el("div", { class: "photos" });
      imgs.forEach((im, i) => {
        const href = `${API}/api/image?url=${encodeURIComponent(url)}&i=${encodeURIComponent(im.index)}`;
        const pic = el("img", { alt: "", referrerpolicy: "no-referrer", loading: "lazy" });
        pic.src = im.thumbnail;
        pic.addEventListener("error", () => pic.remove());
        const a = el("a", { class: "btn primary", href, rel: "noopener", text: `${t.photo} ${i + 1}` });
        grid.append(el("figure", { class: "photo" }, pic, a));
      });
      info.append(el("p", { class: "opts-h photos-h", text: t.photos_h }), grid);
    }
    resultEl.append(thumb, info);
    resultEl.hidden = false;
    resultEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  async function submit(ev) {
    if (ev) ev.preventDefault();
    const url = input.value.trim();
    resultEl.hidden = true;
    if (!validUrl(url)) return setStatus("error", t.err_invalid);
    goBtn.disabled = true;
    setStatus("", t.loading, true);
    try {
      const res = await fetch(`${API}/api/info`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) return setStatus("error", errorMessage(data.error));
      setStatus("", "");
      render(data, url);
    } catch (_) {
      setStatus("error", t.err_network);
    } finally {
      goBtn.disabled = false;
    }
  }

  async function paste() {
    try {
      const text = (await navigator.clipboard.readText()).trim();
      if (text) { input.value = text; submit(); }
    } catch (_) {
      input.focus();
      setStatus("", t.paste_manual);
    }
  }

  form.addEventListener("submit", submit);
  pasteBtn.addEventListener("click", paste);
  if (!navigator.clipboard || !navigator.clipboard.readText) pasteBtn.hidden = true;

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => navigator.serviceWorker.register("/sw.js").catch(() => {}));
  }
})();
