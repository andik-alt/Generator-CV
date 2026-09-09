const form = document.getElementById("cv-form");

const el = {
  nama: document.getElementById("p-nama"),
  gelar: document.getElementById("p-gelar"),
  kontak: document.getElementById("p-kontak"),
  ringkasanBlok: document.getElementById("s-ringkasan"),
  ringkasan: document.getElementById("p-ringkasan"),
  pendidikanBlok: document.getElementById("s-pendidikan"),
  pendidikan: document.getElementById("p-pendidikan"),
  pengalamanBlok: document.getElementById("s-pengalaman"),
  pengalaman: document.getElementById("p-pengalaman"),
  skillBlok: document.getElementById("s-skill"),
  skill: document.getElementById("p-skill"),
};

function linesOf(id) {
  return document
    .getElementById(id)
    .value.split("\n")
    .map((s) => s.trim())
    .filter(Boolean);
}

function fillList(ulEl, blockEl, items) {
  ulEl.innerHTML = "";
  if (items.length === 0) {
    blockEl.hidden = true;
    return;
  }
  blockEl.hidden = false;
  items.forEach((text) => {
    const li = document.createElement("li");
    li.textContent = text;
    ulEl.appendChild(li);
  });
}

function updatePreview() {
  const nama = document.getElementById("nama").value.trim();
  const gelar = document.getElementById("gelar").value.trim();
  const email = document.getElementById("email").value.trim();
  const telepon = document.getElementById("telepon").value.trim();
  const lokasi = document.getElementById("lokasi").value.trim();
  const kontakLain = linesOf("kontak_lain");
  const ringkasan = document.getElementById("ringkasan").value.trim();
  const pendidikan = linesOf("pendidikan");
  const pengalaman = linesOf("pengalaman");
  const skill = document
    .getElementById("skill")
    .value.split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  el.nama.textContent = nama || "Nama Lengkap";
  el.gelar.textContent = gelar;

  const kontakParts = [email, telepon, lokasi, ...kontakLain].filter(Boolean);
  el.kontak.textContent = kontakParts.join("  ·  ");

  if (ringkasan) {
    el.ringkasanBlok.hidden = false;
    el.ringkasan.textContent = ringkasan;
  } else {
    el.ringkasanBlok.hidden = true;
  }

  fillList(el.pendidikan, el.pendidikanBlok, pendidikan);
  fillList(el.pengalaman, el.pengalamanBlok, pengalaman);
  fillList(el.skill, el.skillBlok, skill);
}

form.addEventListener("input", updatePreview);
updatePreview();

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const button = form.querySelector(".btn-download");
  const originalLabel = button.textContent;
  button.textContent = "Membuat PDF...";
  button.disabled = true;

  try {
    const response = await fetch("/generate-pdf", {
      method: "POST",
      body: new FormData(form),
    });

    if (!response.ok) {
      throw new Error("Gagal membuat PDF");
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;

    const disposition = response.headers.get("Content-Disposition") || "";
    const match = disposition.match(/filename="?([^"]+)"?/);
    a.download = match ? match[1] : "cv.pdf";

    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert("Terjadi kesalahan saat membuat PDF. Coba lagi.");
    console.error(err);
  } finally {
    button.textContent = originalLabel;
    button.disabled = false;
  }
});
