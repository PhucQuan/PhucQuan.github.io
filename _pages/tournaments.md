---
layout: single
title: "Tournaments"
permalink: /tournaments/
author_profile: true
---

<style>
.tournament-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.tournament-card {
  border: 1px solid #333;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  background: #1a1a1a;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
}

.tournament-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  text-decoration: none;
}

.tournament-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  background-color: #333;
}

.tournament-content {
  padding: 1.5rem;
}

.tournament-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: bold;
  color: #fff;
}

.tournament-meta {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #888;
}
</style>

<div class="tournament-grid">

  <!-- LA CTF 2026 -->
  <a href="/categories/#lactf-2026" class="tournament-card">
    <img src="/assets/images/lactf/logo.png" alt="LA CTF 2026" class="tournament-image" onerror="this.onerror=null; this.src='https://placehold.co/600x400/333/fff?text=LA+CTF+2026';">
    <div class="tournament-content">
      <h3 class="tournament-title">LA CTF 2026</h3>
      <div class="tournament-meta">3 Writeups</div>
    </div>
  </a>

  <!-- NullCon 2025 -->
  <a href="/categories/#nullcon-2025" class="tournament-card">
    <img src="/assets/images/nullcon/logo.png" alt="NullCon 2025" class="tournament-image" onerror="this.onerror=null; this.src='https://placehold.co/600x400/333/fff?text=NullCon+2025';">
    <div class="tournament-content">
      <h3 class="tournament-title">NullCon 2025</h3>
      <div class="tournament-meta">1 Writeup</div>
    </div>
  </a>

  <!-- HCMUTE CTF 2026 -->
  <a href="/categories/#hcmute-ctf-2026" class="tournament-card">
    <img src="/assets/images/hcmute/logo.png" alt="HCMUTE CTF 2026" class="tournament-image" onerror="this.onerror=null; this.src='https://placehold.co/600x400/333/fff?text=HCMUTE+CTF+2026';">
    <div class="tournament-content">
      <h3 class="tournament-title">HCMUTE CTF 2026</h3>
      <div class="tournament-meta">10 Writeups</div>
    </div>
  </a>

  <!-- UofTCTF 2026 -->
  <a href="/categories/#uoftctf-2026" class="tournament-card">
    <img src="/assets/images/uoftctf/logo.png" alt="UofTCTF 2026" class="tournament-image" onerror="this.onerror=null; this.src='https://placehold.co/600x400/333/fff?text=UofTCTF+2026';">
    <div class="tournament-content">
      <h3 class="tournament-title">UofTCTF 2026</h3>
      <div class="tournament-meta">2 Writeups</div>
    </div>
  </a>

  <!-- Hack The Box -->
  <a href="/categories/#hack-the-box" class="tournament-card">
    <img src="/assets/images/htb/logo.png" alt="Hack The Box" class="tournament-image" onerror="this.onerror=null; this.src='https://placehold.co/600x400/333/fff?text=Hack+The+Box';">
    <div class="tournament-content">
      <h3 class="tournament-title">Hack The Box</h3>
      <div class="tournament-meta">2 Writeups</div>
    </div>
  </a>

</div>
