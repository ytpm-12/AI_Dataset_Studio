const icons = {
  grid: '<rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect>',
  folder: '<path d="M3 6.5h6l2 2h10v9.5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"></path>',
  upload: '<path d="M12 16V4"></path><path d="m7 9 5-5 5 5"></path><path d="M4 20h16"></path>',
  scan: '<path d="M4 7V5a1 1 0 0 1 1-1h2"></path><path d="M17 4h2a1 1 0 0 1 1 1v2"></path><path d="M20 17v2a1 1 0 0 1-1 1h-2"></path><path d="M7 20H5a1 1 0 0 1-1-1v-2"></path><path d="M7 12h10"></path>',
  broom: '<path d="m14 4 6 6"></path><path d="m5 19 5-5"></path><path d="m9 15 6-6 2 2-6 6Z"></path><path d="M3 21c3 .3 5-.4 6-2"></path>',
  doc: '<path d="M6 3h8l4 4v14H6Z"></path><path d="M14 3v5h5"></path><path d="M8 13h8"></path><path d="M8 17h6"></path>',
  image: '<rect x="3" y="5" width="18" height="14" rx="2"></rect><circle cx="8" cy="10" r="1.5"></circle><path d="m21 16-5-5L5 19"></path>',
  tag: '<path d="M20 13 13 20a2 2 0 0 1-2.8 0L4 13.8V4h9.8L20 10.2a2 2 0 0 1 0 2.8Z"></path><circle cx="8" cy="8" r="1.4"></circle>',
  spark: '<path d="M12 3l1.8 5 5.2 1.8-5.2 1.8L12 17l-1.8-5.4L5 9.8 10.2 8Z"></path><path d="M19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8Z"></path>',
  scale: '<path d="M12 3v18"></path><path d="M6 6h12"></path><path d="m6 6-3 7h6Z"></path><path d="m18 6-3 7h6Z"></path>',
  report: '<path d="M5 3h14v18H5Z"></path><path d="M8 8h8"></path><path d="M8 12h8"></path><path d="M8 16h5"></path>',
  download: '<path d="M12 4v12"></path><path d="m7 11 5 5 5-5"></path><path d="M4 20h16"></path>',
  clock: '<circle cx="12" cy="12" r="9"></circle><path d="M12 7v5l3 2"></path>',
  settings: '<circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2 3.4-.2-.1a1.8 1.8 0 0 0-2 .1 1.7 1.7 0 0 0-.8 1.6v.2H10v-.2a1.8 1.8 0 0 0-.8-1.6 1.7 1.7 0 0 0-2-.1l-.2.1-2-3.4.1-.1A1.7 1.7 0 0 0 5.4 15a1.8 1.8 0 0 0-1.4-1H3.8v-4H4a1.8 1.8 0 0 0 1.4-1 1.7 1.7 0 0 0-.3-1.9L5 7l2-3.4.2.1a1.7 1.7 0 0 0 2-.1A1.8 1.8 0 0 0 10 2h4a1.8 1.8 0 0 0 .8 1.6 1.7 1.7 0 0 0 2 .1l.2-.1 2 3.4-.1.1a1.7 1.7 0 0 0-.3 1.9 1.8 1.8 0 0 0 1.4 1h.2v4H20a1.8 1.8 0 0 0-1.4 1Z"></path>',
  search: '<circle cx="11" cy="11" r="7"></circle><path d="m20 20-3.5-3.5"></path>',
  bell: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 7h18s-3 0-3-7"></path><path d="M10 19a2 2 0 0 0 4 0"></path>',
  chevron: '<path d="m9 18 6-6-6-6"></path>',
  check: '<path d="m5 12 4 4L19 6"></path>',
  alert: '<path d="M10.3 3.9 2.8 17a2 2 0 0 0 1.7 3h15a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path>',
  plus: '<path d="M12 5v14"></path><path d="M5 12h14"></path>',
  play: '<path d="M8 5v14l11-7Z"></path>',
  x: '<path d="M18 6 6 18"></path><path d="m6 6 12 12"></path>',
  menu: '<path d="M4 7h16"></path><path d="M4 12h16"></path><path d="M4 17h16"></path>',
  sliders: '<path d="M4 6h10"></path><path d="M18 6h2"></path><path d="M4 12h3"></path><path d="M11 12h9"></path><path d="M4 18h12"></path><path d="M20 18h0"></path><circle cx="16" cy="6" r="2"></circle><circle cx="9" cy="12" r="2"></circle><circle cx="18" cy="18" r="2"></circle>',
  copy: '<rect x="8" y="8" width="12" height="12" rx="2"></rect><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"></path>'
};

const navSections = [
  {
    label: "Workspace",
    items: [
      { key: "dashboard", label: "Tableau de bord", icon: "grid" },
      { key: "projects", label: "Projets", icon: "folder" },
      { key: "project", label: "Version active", icon: "scan" }
    ]
  },
  {
    label: "Pipeline",
    items: [
      { key: "import", label: "Import", icon: "upload" },
      { key: "profiling", label: "Analyse", icon: "scan" },
      { key: "cleaning", label: "Nettoyage", icon: "broom" },
      { key: "documents", label: "Documents PDF", icon: "doc" },
      { key: "images", label: "Images", icon: "image" },
      { key: "annotation", label: "Annotation", icon: "tag" },
      { key: "ai", label: "Recommandations IA", icon: "spark" },
      { key: "balancing", label: "Équilibrage", icon: "scale" }
    ]
  },
  {
    label: "Résultats",
    items: [
      { key: "report", label: "Rapport qualité", icon: "report" },
      { key: "export", label: "Export", icon: "download" },
      { key: "jobs", label: "Traitements", icon: "clock", badge: "2" }
    ]
  }
];

const routeLabels = {
  dashboard: "Tableau de bord",
  projects: "Projets",
  project: "Version active",
  import: "Import",
  profiling: "Analyse",
  cleaning: "Nettoyage",
  documents: "Documents PDF",
  images: "Images",
  annotation: "Annotation",
  ai: "Recommandations IA",
  balancing: "Équilibrage",
  report: "Rapport qualité",
  export: "Export",
  jobs: "Traitements"
};

function icon(name, cls = "icon") {
  return `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.grid}</svg>`;
}

function route() {
  const key = (location.hash || "#dashboard").replace("#", "");
  return routeLabels[key] ? key : "dashboard";
}

function shell(active) {
  return `
    <div class="app-shell">
      <aside class="rail" id="rail">
        <a class="brand" href="#dashboard">
          <span class="brand-mark" aria-hidden="true"></span>
          <span class="brand-word">
            <strong>AI Dataset Studio</strong>
            <span>Canva des datasets</span>
          </span>
        </a>
        ${navSections
          .map(
            (section) => `
              <section class="rail-section">
                <div class="rail-label">${section.label}</div>
                ${section.items
                  .map(
                    (item) => `
                      <a class="rail-link ${item.key === active ? "is-active" : ""}" href="#${item.key}" data-route="${item.key}">
                        ${icon(item.icon)}
                        <span>${item.label}</span>
                        ${item.badge ? `<span class="rail-badge">${item.badge}</span>` : ""}
                      </a>`
                  )
                  .join("")}
              </section>`
          )
          .join("")}
        <div class="rail-foot">
          <a class="active-project" href="#project">
            <small>Projet actif</small>
            <strong>customer-support-tickets</strong>
            <span>v4 - CSV - 84 320 lignes</span>
          </a>
          <a class="user-chip" href="#projects">
            <span class="avatar">PM</span>
            <span>
              <strong>Prince Migwel</strong>
              <span>Owner</span>
            </span>
            ${icon("settings")}
          </a>
        </div>
      </aside>
      <main class="main">
        <header class="topbar">
          <button class="icon-btn mobile-menu" type="button" data-action="toggle-rail" aria-label="Menu">${icon("menu")}</button>
          <nav class="crumbs" aria-label="Fil d'Ariane">
            <a href="#dashboard">Studio</a>
            ${icon("chevron")}
            <span class="current">${routeLabels[active]}</span>
          </nav>
          <div class="top-spacer"></div>
          <label class="search">
            ${icon("search")}
            <input type="search" placeholder="Rechercher projet, version, colonne" />
            <span class="kbd">Ctrl K</span>
          </label>
          <button class="icon-btn" type="button" data-toast="Deux traitements demandent une validation." aria-label="Notifications">${icon("bell")}<span class="dot"></span></button>
          <button class="icon-btn" type="button" data-toast="Préférences de studio ouvertes." aria-label="Paramètres">${icon("settings")}</button>
        </header>
        <section class="content" id="content"></section>
      </main>
    </div>
    <div class="toast-stack" id="toastStack"></div>
    <div class="overlay" id="projectModal">
      <section class="modal" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
        <div class="panel-head">
          <div>
            <h2 id="modalTitle">Nouveau projet dataset</h2>
            <p>Configuration initiale du workspace.</p>
          </div>
          <button class="icon-btn" type="button" data-action="close-modal" aria-label="Fermer">${icon("x")}</button>
        </div>
        <div class="field">
          <label for="projectName">Nom du projet</label>
          <input id="projectName" value="retail-image-quality" />
        </div>
        <div class="field">
          <label for="projectType">Type principal</label>
          <select id="projectType">
            <option>Tabulaire</option>
            <option>Documents PDF</option>
            <option>Images</option>
            <option>Mixte</option>
          </select>
        </div>
        <div class="field">
          <label for="projectGoal">Objectif</label>
          <textarea id="projectGoal" rows="3">Préparer un dataset propre, annoté et exportable pour entraînement IA.</textarea>
        </div>
        <div class="footer-actions">
          <button class="btn" type="button" data-action="close-modal">Annuler</button>
          <button class="btn btn-primary" type="button" data-action="create-project">${icon("plus")} Créer</button>
        </div>
      </section>
    </div>`;
}

function pageHead(eyebrow, title, sub, actions = "") {
  return `
    <div class="page-head">
      <div>
        <div class="eyebrow">${eyebrow}</div>
        <h1>${title}</h1>
        <p>${sub}</p>
      </div>
      <div class="actions">${actions}</div>
    </div>`;
}

function bars(values) {
  return `<div class="chart-bars">${values.map((v, i) => `<span style="height:${v}%; animation-delay:${i * 28}ms"></span>`).join("")}</div>`;
}

function miniBars(values) {
  return `<div class="mini-bars">${values.map((v, i) => `<span style="height:${v}%; animation-delay:${i * 18}ms"></span>`).join("")}</div>`;
}

function progress(value, tone = "") {
  return `<div class="progress ${tone}"><span style="width:${value}%"></span></div>`;
}

function status(label, tone = "ok") {
  return `<span class="status status-${tone}">${label}</span>`;
}

function dashboardPage() {
  return `
    <div class="grid" style="gap: var(--sp-8)">
      <section class="hero-lab">
        <div>
          <div class="eyebrow">Workspace actif</div>
          <h1>Préparateur de datasets IA</h1>
          <p>Un studio de contrôle pour importer, profiler, nettoyer, annoter, équilibrer et exporter chaque version sans modification silencieuse.</p>
          <div class="hero-meta">
            <span class="chip">Source immuable</span>
            <span class="chip">Mode assisté</span>
            <span class="chip">2 jobs actifs</span>
            <span class="chip">Score qualité 87</span>
          </div>
        </div>
        <div class="lab-instrument">
          <div class="sample-column" aria-hidden="true">
            ${Array.from({ length: 8 }, (_, i) => `<span class="sample-tile ${i === 2 ? "is-warn" : i === 5 ? "is-ok" : ""}"></span>`).join("")}
          </div>
          <div class="instrument-main">
            <div class="instrument-line">
              <span class="signal">JOB-2041 RUNNING</span>
              <span class="chip">v4</span>
            </div>
            ${miniBars([44, 61, 70, 38, 78, 83, 48, 56, 72, 66, 29, 81, 86, 54, 63, 76, 58, 40, 91, 73, 52, 67, 77, 34, 62, 86, 71, 49])}
            <div class="pipeline-strip">
              ${["Import", "Analyse", "Nettoyage", "PDF", "Images", "Annotation", "Balance", "Export"]
                .map((s, i) => `<div class="strip-step ${i === 2 ? "is-active" : ""}"><small>0${i + 1}</small><strong>${s}</strong></div>`)
                .join("")}
            </div>
          </div>
        </div>
      </section>

      <section class="grid grid-4">
        <article class="metric">
          <div class="label">Score qualité</div>
          <div class="value">87</div>
          <div class="delta">+12 apres nettoyage</div>
        </article>
        <article class="metric warn">
          <div class="label">Valeurs manquantes</div>
          <div class="value">2.4%</div>
          <div class="delta">1 982 cellules</div>
        </article>
        <article class="metric danger">
          <div class="label">Anomalies ouvertes</div>
          <div class="value">31</div>
          <div class="delta">8 critiques</div>
        </article>
        <article class="metric">
          <div class="label">Annotations validees</div>
          <div class="value">74%</div>
          <div class="delta">12 408 labels</div>
        </article>
      </section>

      <section class="grid grid-3">
        <article class="panel span-2">
          <div class="panel-head">
            <div>
              <h2>Thread de version</h2>
              <p>Historique reversible du projet actif.</p>
            </div>
            <a class="btn" href="#project">${icon("scan")} Ouvrir</a>
          </div>
          <div class="version-thread">
            <div class="thread-item"><strong>v4 - Nettoyage applique</strong><span>Suppression de 421 doublons, imputation mediane sur age.</span></div>
            <div class="thread-item is-warn"><strong>v3 - Analyse avec avertissements</strong><span>Distribution classe "billing" desequilibree.</span></div>
            <div class="thread-item"><strong>v2 - Import valide</strong><span>CSV source conserve en lecture seule.</span></div>
            <div class="thread-item is-muted"><strong>v1 - Projet créé</strong><span>Schéma initial et objectifs.</span></div>
          </div>
        </article>
        <article class="panel">
          <div class="panel-head">
            <div>
              <h2>Jobs actifs</h2>
              <p>Workers data, document et IA.</p>
            </div>
          </div>
          <div class="grid">
            <div>
              <div class="panel-head" style="margin-bottom: 8px"><strong>Profilage v4</strong>${status("RUNNING", "run")}</div>
              ${progress(68)}
            </div>
            <div>
              <div class="panel-head" style="margin-bottom: 8px"><strong>Pre-annotation</strong>${status("QUEUED", "muted")}</div>
              ${progress(18, "warn")}
            </div>
            <div>
              <div class="panel-head" style="margin-bottom: 8px"><strong>OCR PDF</strong>${status("SUCCEEDED", "ok")}</div>
              ${progress(100)}
            </div>
          </div>
        </article>
      </section>
    </div>`;
}

function projectsPage() {
  const rows = [
    ["customer-support-tickets", "Tabulaire", "84 320", "v4", "87", "Actif"],
    ["invoice-pdf-corpus", "PDF", "2 410", "v2", "78", "Analyse"],
    ["retail-shelf-images", "Images", "18 905", "v7", "91", "Annotation"],
    ["startup-leads-json", "JSON", "32 100", "v3", "72", "Nettoyage"]
  ];
  return `
    ${pageHead(
      "Workspace",
      "Projets dataset",
      "Tous les espaces de préparation avec leurs versions, formats et scores de qualité.",
      `<button class="btn btn-primary" type="button" data-action="open-modal">${icon("plus")} Nouveau projet</button>`
    )}
    <section class="grid grid-4" style="margin-bottom: var(--sp-6)">
      <article class="metric"><div class="label">Projets</div><div class="value">12</div><div class="delta">4 actifs</div></article>
      <article class="metric"><div class="label">Versions</div><div class="value">38</div><div class="delta">immutables</div></article>
      <article class="metric warn"><div class="label">À vérifier</div><div class="value">9</div><div class="delta">règles IA</div></article>
      <article class="metric"><div class="label">Exports</div><div class="value">21</div><div class="delta">CSV, JSON, YOLO</div></article>
    </section>
    <section class="table-wrap">
      <div class="table-toolbar">
        <h2>Liste des projets</h2>
        <div class="segmented" data-segmented>
          <button class="is-active">Tous</button>
          <button>Actifs</button>
          <button>À vérifier</button>
        </div>
      </div>
      <table class="data-table">
        <thead><tr><th>Nom</th><th>Type</th><th>Lignes / fichiers</th><th>Version</th><th>Qualité</th><th>État</th><th></th></tr></thead>
        <tbody>
          ${rows
            .map(
              (r, i) => `<tr>
                <td><strong>${r[0]}</strong><br><span class="muted mono">PRJ-${2040 + i}</span></td>
                <td>${r[1]}</td>
                <td>${r[2]}</td>
                <td><span class="chip">v${r[3].replace("v", "")}</span></td>
                <td>${progress(Number(r[4]))}</td>
                <td>${status(r[5], r[5] === "Actif" ? "ok" : r[5] === "Analyse" ? "run" : "warn")}</td>
                <td><a class="btn" href="#project">Ouvrir</a></td>
              </tr>`
            )
            .join("")}
        </tbody>
      </table>
    </section>`;
}

function projectPage() {
  return `
    ${pageHead(
      "Projet actif",
      "customer-support-tickets",
      "Dataset CSV destiné à classifier les tickets support avant entraînement.",
      `<a class="btn" href="#import">${icon("upload")} Importer</a><a class="btn btn-primary" href="#report">${icon("report")} Rapport</a>`
    )}
    <section class="grid grid-3">
      <article class="panel span-2">
        <div class="panel-head">
          <div><h2>Pipeline projet</h2><p>Chaque transformation produit une nouvelle version.</p></div>
          <span class="chip chip-pine">Mode assisté</span>
        </div>
        <div class="pipeline-strip" style="grid-template-columns: repeat(8, minmax(92px, 1fr)); color: var(--ink)">
          ${["Import", "Analyse", "Nettoyage", "Annotation", "Anomalies", "Balance", "Validation", "Export"]
            .map((s, i) => `<a class="strip-step ${i < 3 ? "is-active" : ""}" style="color: var(--ink); background:${i < 3 ? "var(--pine-soft)" : "var(--surface-alt)"}; border-color:${i < 3 ? "var(--pine-soft-2)" : "var(--line)"}" href="#${["import", "profiling", "cleaning", "annotation", "ai", "balancing", "report", "export"][i]}"><small>${String(i + 1).padStart(2, "0")}</small><strong>${s}</strong></a>`)
            .join("")}
        </div>
      </article>
      <article class="panel">
        <div class="panel-head"><div><h2>Mode de contrôle</h2><p>Niveau d'automatisation courant.</p></div></div>
        <div class="segmented" data-segmented style="width:100%">
          <button>Manuel</button><button class="is-active">Assisté</button><button>Auto</button>
        </div>
        <div class="recommendation" style="margin-top: var(--sp-4)">
          <strong>Validation humaine requise</strong>
          <span class="tiny soft">Les recommandations sensibles restent en attente de decision utilisateur.</span>
        </div>
      </article>
      <article class="panel">
        <div class="panel-head"><div><h2>Versions</h2><p>Fil de preparation.</p></div></div>
        <div class="version-thread">
          <div class="thread-item"><strong>v4 clean_candidate</strong><span>SUCCEEDED_WITH_WARNINGS</span></div>
          <div class="thread-item"><strong>v3 profiled</strong><span>SUCCEEDED</span></div>
          <div class="thread-item is-muted"><strong>v2 imported</strong><span>Source preservee</span></div>
        </div>
      </article>
      <article class="panel span-2">
        <div class="panel-head"><div><h2>Contrats techniques visibles</h2><p>Modeles et routes alignes avec les specifications.</p></div></div>
        <div class="file-grid">
          ${["Utilisateur", "ProjetDataset", "Dataset", "VersionDataset", "ProcessingJob", "Transformation", "Recommendation", "QualityReport"]
            .map((x) => `<div class="file-card"><div class="file-icon">${icon("doc")}</div><strong>${x}</strong><br><span class="tiny muted">metadata JSON - status - created_at</span></div>`)
            .join("")}
        </div>
      </article>
    </section>`;
}

function importPage() {
  return `
    ${pageHead(
      "Pipeline 01",
      "Import et validation",
      "Chargement CSV, JSON, XML, PDF ou images avec contrôle format, structure et source en lecture seule.",
      `<button class="btn" type="button" data-toast="Validation de structure lancée.">${icon("play")} Valider</button>`
    )}
    <section class="grid grid-3">
      <div class="span-2">
        <div class="dropzone">
          <div>
            <div class="dropzone-icon">${icon("upload")}</div>
            <h2>Déposer un fichier ou un dossier image</h2>
            <p>Formats acceptés: CSV, JSON, XML, PDF, PNG, JPG. Taille maximale configurée par MAX_UPLOAD_SIZE_MB.</p>
            <div class="hero-meta" style="justify-content:center; margin-top: var(--sp-4)">
              <span class="chip chip-pine">CSV</span><span class="chip">JSON</span><span class="chip">XML</span><span class="chip">PDF</span><span class="chip">Images</span>
            </div>
          </div>
        </div>
      </div>
      <aside class="panel">
        <div class="panel-head"><div><h2>Validation import</h2><p>Contrôle avant création de version.</p></div></div>
        <div class="grid">
          <div><div class="panel-head" style="margin-bottom:8px"><strong>Format</strong>${status("OK", "ok")}</div>${progress(100)}</div>
          <div><div class="panel-head" style="margin-bottom:8px"><strong>Structure</strong>${status("WARN", "warn")}</div>${progress(82, "warn")}</div>
          <div><div class="panel-head" style="margin-bottom:8px"><strong>Encodage</strong>${status("OK", "ok")}</div>${progress(100)}</div>
        </div>
      </aside>
      <article class="panel span-2">
        <div class="panel-head"><div><h2>Aperçu schéma</h2><p>Détection de colonnes et types probables.</p></div><span class="chip chip-amber">2 colonnes à confirmer</span></div>
        <div class="table-wrap" style="box-shadow:none; border:0">
          <table class="data-table">
            <thead><tr><th>Colonne</th><th>Type detecte</th><th>Null</th><th>Exemple</th><th>Action</th></tr></thead>
            <tbody>
              <tr><td><strong>ticket_id</strong></td><td>string</td><td>0%</td><td class="mono">TCK-90321</td><td>${status("Conserver", "ok")}</td></tr>
              <tr><td><strong>customer_age</strong></td><td>integer</td><td>6.8%</td><td class="mono">34</td><td>${status("Vérifier", "warn")}</td></tr>
              <tr><td><strong>created_at</strong></td><td>datetime</td><td>0%</td><td class="mono">2026-08-12</td><td>${status("Conserver", "ok")}</td></tr>
              <tr><td><strong>message</strong></td><td>text</td><td>1.1%</td><td>Retard de livraison...</td><td>${status("Nettoyer", "run")}</td></tr>
            </tbody>
          </table>
        </div>
      </article>
      <article class="panel">
        <div class="panel-head"><div><h2>Erreurs possibles</h2><p>Gestion conforme SFD.</p></div></div>
        <div class="rule-list">
          ${["Format non supporte", "Fichier illisible", "Fichier vide", "Structure invalide", "Import partiel"]
            .map((x) => `<div class="rule-row"><span class="handle">${icon("alert")}</span><div><strong>${x}</strong><br><span class="tiny muted">Message clair et action de reprise.</span></div></div>`)
            .join("")}
        </div>
      </article>
    </section>`;
}

function profilingPage() {
  return `
    ${pageHead(
      "Pipeline 02",
      "Analyse et profilage",
      "Vue qualité initiale: valeurs manquantes, doublons, distributions, anomalies et recommandations.",
      `<button class="btn btn-primary" type="button" data-toast="Reprofilage planifie dans la file workers.">${icon("play")} Reprofiler</button>`
    )}
    <section class="grid grid-4" style="margin-bottom: var(--sp-6)">
      <article class="metric"><div class="label">Colonnes</div><div class="value">42</div><div class="delta">6 sensibles</div></article>
      <article class="metric warn"><div class="label">Doublons</div><div class="value">421</div><div class="delta">0.5%</div></article>
      <article class="metric danger"><div class="label">Outliers</div><div class="value">118</div><div class="delta">age, total</div></article>
      <article class="metric"><div class="label">Completude</div><div class="value">97.6%</div><div class="delta">bon</div></article>
    </section>
    <section class="grid grid-3">
      <article class="panel span-2">
        <div class="panel-head"><div><h2>Distribution des classes</h2><p>Tickets par categorie cible.</p></div>${status("Desequilibre", "warn")}</div>
        ${bars([62, 40, 86, 34, 29, 56, 22, 74, 44, 28, 18, 32])}
      </article>
      <article class="panel">
        <div class="panel-head"><div><h2>Valeurs manquantes</h2><p>Carte des colonnes critiques.</p></div></div>
        <div class="heatmap">${Array.from({ length: 98 }, () => "<span></span>").join("")}</div>
      </article>
      <article class="table-wrap span-2">
        <div class="table-toolbar"><h2>Profil colonnes</h2><span class="chip">42 colonnes</span></div>
        <table class="data-table">
        <thead><tr><th>Colonne</th><th>Type</th><th>Missing</th><th>Unique</th><th>Qualité</th></tr></thead>
          <tbody>
            <tr><td><strong>ticket_id</strong></td><td>string</td><td>0%</td><td>84 320</td><td>${progress(100)}</td></tr>
            <tr><td><strong>customer_age</strong></td><td>integer</td><td>6.8%</td><td>78</td><td>${progress(74, "warn")}</td></tr>
            <tr><td><strong>message</strong></td><td>text</td><td>1.1%</td><td>81 204</td><td>${progress(88)}</td></tr>
            <tr><td><strong>label</strong></td><td>category</td><td>0%</td><td>12</td><td>${progress(69, "warn")}</td></tr>
          </tbody>
        </table>
      </article>
      <article class="panel">
        <div class="panel-head"><div><h2>Recommandations</h2><p>Règles proposées avant nettoyage.</p></div></div>
        <div class="rule-list">
          <div class="recommendation"><strong>customer_age</strong><span>Imputation mediane - confiance 0.82</span></div>
          <div class="recommendation"><strong>label</strong><span>Rééquilibrage recommandé - confiance 0.76</span></div>
        </div>
      </article>
    </section>`;
}

function cleaningPage() {
  return `
    ${pageHead(
      "Pipeline 03",
      "Nettoyage et transformation",
      "Règles explicites, preview avant application et nouvelle version après transformation.",
      `<button class="btn" type="button" data-toast="Règle ajoutée au pipeline.">${icon("plus")} Règle</button><button class="btn btn-primary" type="button" data-toast="Transformation appliquée: v5 candidate créée.">${icon("play")} Appliquer</button>`
    )}
    <section class="grid grid-3">
      <article class="panel">
        <div class="panel-head"><div><h2>Règles ordonnées</h2><p>Exécution contrôlée par pipeline.</p></div></div>
        <div class="rule-list">
          <div class="rule-row"><span class="handle">${icon("sliders")}</span><div><strong>Trim espaces texte</strong><br><span class="tiny muted">message, subject</span></div>${status("pret", "ok")}</div>
          <div class="rule-row"><span class="handle">${icon("sliders")}</span><div><strong>Imputation mediane</strong><br><span class="tiny muted">customer_age</span></div>${status("IA", "warn")}</div>
          <div class="rule-row"><span class="handle">${icon("sliders")}</span><div><strong>Supprimer doublons</strong><br><span class="tiny muted">ticket_id + message</span></div>${status("pret", "ok")}</div>
        </div>
      </article>
      <article class="panel span-2">
        <div class="panel-head"><div><h2>Preview avant / apres</h2><p>Aucune modification silencieuse.</p></div><span class="chip chip-pine">421 lignes touchees</span></div>
        <div class="split-preview">
          <div class="preview-side">
            <div class="preview-head"><span>Avant</span><span class="muted">v4</span></div>
            <div class="record-lines">
              <span class="record-line warn"></span><span class="record-line"></span><span class="record-line short warn"></span><span class="record-line"></span><span class="record-line short"></span>
            </div>
          </div>
          <div class="preview-side">
            <div class="preview-head"><span>Apres</span><span class="muted">v5 candidate</span></div>
            <div class="record-lines">
              <span class="record-line ok"></span><span class="record-line"></span><span class="record-line short ok"></span><span class="record-line"></span><span class="record-line short"></span>
            </div>
          </div>
        </div>
      </article>
      <article class="panel span-2">
        <div class="panel-head"><div><h2>Impact estimé</h2><p>Score qualité après application.</p></div></div>
        <div class="grid grid-3">
          <div><strong>Completeness</strong>${progress(96)}</div>
          <div><strong>Duplicates</strong>${progress(99)}</div>
          <div><strong>Consistency</strong>${progress(89)}</div>
        </div>
      </article>
      <article class="panel">
        <div class="recommendation">
          <strong>Explication IA</strong>
          <span class="tiny">L'imputation mediane limite l'impact des valeurs extremes dans customer_age.</span>
          <button class="btn" type="button" data-toast="Recommandation acceptée.">${icon("check")} Accepter</button>
        </div>
      </article>
    </section>`;
}

function documentsPage() {
  return `
    ${pageHead(
      "Documents",
      "Analyse PDF et OCR",
      "Extraction de texte, tableaux et erreurs documentaires avec suivi de confiance.",
      `<button class="btn btn-primary" type="button" data-toast="Analyse documentaire ajoutée à la file.">${icon("play")} Analyser</button>`
    )}
    <section class="pdf-layout">
      <aside class="panel">
        <div class="panel-head"><div><h2>Pages</h2><p>12 analysees.</p></div></div>
        <div class="grid">
          <div class="page-thumb is-active"><strong>Page 1</strong><br><span class="tiny muted">OCR 96%</span></div>
          <div class="page-thumb"><strong>Page 2</strong><br><span class="tiny muted">Table detectee</span></div>
          <div class="page-thumb"><strong>Page 3</strong><br><span class="tiny muted">OCR 88%</span></div>
        </div>
      </aside>
      <article class="page-paper">
        <div class="line title"></div>
        <div class="line" style="width: 92%"></div>
        <div class="line" style="width: 84%"></div>
        <div class="line" style="width: 76%"></div>
        <div class="table-sim">
          ${Array.from({ length: 20 }, () => '<span class="cell"></span>').join("")}
        </div>
        <div class="line" style="width: 66%; margin-top: 24px"></div>
        <div class="line" style="width: 90%"></div>
      </article>
      <aside class="panel">
        <div class="panel-head"><div><h2>Qualité extraction</h2><p>Signaux documentaires.</p></div></div>
        <div class="grid">
          <div><div class="panel-head" style="margin-bottom:8px"><strong>OCR</strong><span>93%</span></div>${progress(93)}</div>
          <div><div class="panel-head" style="margin-bottom:8px"><strong>Tableaux</strong><span>81%</span></div>${progress(81, "warn")}</div>
          <div><div class="panel-head" style="margin-bottom:8px"><strong>Mise en page</strong><span>88%</span></div>${progress(88)}</div>
          <div class="rule-row"><span class="handle">${icon("alert")}</span><div><strong>DOC-ERR-03</strong><br><span class="tiny muted">Tableau partiellement reconstruit.</span></div></div>
        </div>
      </aside>
    </section>`;
}

function imagesPage() {
  return `
    ${pageHead(
      "Images",
      "Qualité visuelle et labels",
      "Detection d'images corrompues, floues, doublons visuels et coherence des labels.",
      `<button class="btn" type="button" data-toast="Prétraitement image configuré.">${icon("sliders")} Prétraiter</button>`
    )}
    <section class="grid grid-3">
      <article class="panel span-2">
        <div class="panel-head"><div><h2>Grille d'échantillons</h2><p>Contrôle rapide du corpus image.</p></div><span class="chip chip-amber">38 à revoir</span></div>
        <div class="image-grid">
          ${["facture", "produit", "shelf", "ticket", "label", "blur", "doublon", "produit", "shelf", "ocr"]
            .map((x, i) => `<div class="image-tile ${i === 5 ? "is-blur is-warn" : i === 6 ? "is-warn" : ""}" data-label="${x}"></div>`)
            .join("")}
        </div>
      </article>
      <aside class="panel">
        <div class="panel-head"><div><h2>Contrôle image</h2><p>Dimensions, flou, duplication.</p></div></div>
        <div class="grid">
          <div><strong>Resolution OK</strong>${progress(94)}</div>
          <div><strong>Flou detecte</strong>${progress(12, "warn")}</div>
          <div><strong>Similarite visuelle</strong>${progress(18, "warn")}</div>
          <div><strong>Labels coherents</strong>${progress(83)}</div>
        </div>
      </aside>
      <article class="table-wrap span-2">
        <div class="table-toolbar"><h2>Issues image</h2><span class="chip">priorise</span></div>
        <table class="data-table">
          <thead><tr><th>Fichier</th><th>Probleme</th><th>Confiance</th><th>Action</th></tr></thead>
          <tbody>
            <tr><td><strong>IMG_02918.jpg</strong></td><td>Flou</td><td>0.91</td><td>${status("exclure", "warn")}</td></tr>
            <tr><td><strong>IMG_04402.jpg</strong></td><td>Doublon visuel</td><td>0.88</td><td>${status("fusionner", "run")}</td></tr>
            <tr><td><strong>IMG_05018.jpg</strong></td><td>Label incohérent</td><td>0.77</td><td>${status("annoter", "warn")}</td></tr>
          </tbody>
        </table>
      </article>
      <article class="panel">
        <div class="recommendation"><strong>Analyse labels</strong><span class="tiny">La classe "damaged_package" contient 12% d'images visuellement proches de "normal_package".</span></div>
      </article>
    </section>`;
}

function annotationPage() {
  return `
    ${pageHead(
      "Annotation",
      "Validation humaine et pre-annotation",
      "Workspace pour etiqueter les enregistrements, accepter les suggestions IA et suivre l'avancement.",
      `<button class="btn btn-primary" type="button" data-toast="Annotation enregistrée.">${icon("check")} Valider</button>`
    )}
    <section class="annotation-layout">
      <aside class="panel">
        <div class="panel-head"><div><h2>File</h2><p>Enregistrements à annoter.</p></div></div>
        <div class="record-list">
          <div class="record-card is-active"><strong>#8421</strong><br><span class="tiny muted">pre-label: billing</span></div>
          <div class="record-card"><strong>#8422</strong><br><span class="tiny muted">pre-label: shipping</span></div>
          <div class="record-card"><strong>#8423</strong><br><span class="tiny muted">pre-label: refund</span></div>
          <div class="record-card"><strong>#8424</strong><br><span class="tiny muted">conflit label</span></div>
        </div>
      </aside>
      <article class="annotation-canvas">
        <div class="panel-head"><div><h2>Ticket #8421</h2><p>Message client source.</p></div>${status("PENDING_REVIEW", "warn")}</div>
        <div class="text-sample">
          <p>Bonjour, le montant facture ne correspond pas au devis valide. Le support m'a demande de joindre <span class="highlight">la facture corrigee</span> mais je ne vois aucun lien dans mon espace client.</p>
          <p class="tiny muted mono">source_hash: 4f9b8c - version_id: v4</p>
        </div>
        <div style="margin-top: var(--sp-5)">
          <strong>Labels</strong>
          <div class="label-palette" style="margin-top: var(--sp-3)">
            <button class="label-btn is-active">billing</button>
            <button class="label-btn">shipping</button>
            <button class="label-btn">refund</button>
            <button class="label-btn">technical</button>
            <button class="label-btn">other</button>
          </div>
        </div>
      </article>
      <aside class="panel">
        <div class="panel-head"><div><h2>Suggestion IA</h2><p>Decision utilisateur requise.</p></div></div>
        <div class="recommendation">
          <strong>billing - confiance 0.86</strong>
          <span class="tiny">Le message mentionne un montant facture et un devis valide.</span>
          <div class="actions" style="justify-content:flex-start">
            <button class="btn btn-primary" type="button" data-toast="Pré-annotation acceptée.">${icon("check")} Accepter</button>
            <button class="btn" type="button">Corriger</button>
          </div>
        </div>
      </aside>
    </section>`;
}

function aiPage() {
  return `
    ${pageHead(
      "IA controlable",
      "Recommandations et explications",
      "Chaque proposition est tracée, expliquée, puis acceptée ou rejetée avant action sensible.",
      `<button class="btn btn-amber" type="button" data-toast="Nouvelles recommandations demandées.">${icon("spark")} Générer</button>`
    )}
    <section class="grid grid-3">
      ${[
        ["missing_values", "column:customer_age", "median_imputation", "0.82", "PENDING_USER_DECISION"],
        ["class_balance", "label", "undersample_majority", "0.76", "PENDING_USER_DECISION"],
        ["anomaly", "row:18291", "manual_review", "0.91", "OPEN"]
      ]
        .map(
          (r) => `<article class="recommendation">
            <div class="panel-head" style="margin-bottom:0"><strong>${r[0]}</strong><span class="chip chip-violet">${r[3]}</span></div>
            <span class="tiny mono">${r[1]}</span>
            <span>Action proposee: <strong>${r[2]}</strong></span>
            ${status(r[4], r[4] === "OPEN" ? "warn" : "run")}
            <div class="actions" style="justify-content:flex-start"><button class="btn btn-primary" type="button" data-toast="Décision enregistrée.">Accepter</button><button class="btn" type="button">Rejeter</button></div>
          </article>`
        )
        .join("")}
      <article class="panel span-2">
        <div class="panel-head"><div><h2>Contrat recommandation</h2><p>Structure cible exposee au frontend.</p></div></div>
        <pre class="mono" style="white-space:pre-wrap; margin:0; padding:var(--sp-4); background:var(--surface-alt); border:1px solid var(--line); border-radius:var(--radius-sm); font-size:var(--text-xs)">{
  "id": "uuid",
  "version_id": "uuid",
  "type": "missing_values",
  "target": "column:age",
  "proposed_action": "median_imputation",
  "confidence": 0.82,
  "status": "PENDING_USER_DECISION"
}</pre>
      </article>
      <article class="panel">
        <div class="panel-head"><div><h2>Garde-fous</h2><p>Transparence de l'automatisation.</p></div></div>
        <div class="rule-list">
          <div class="rule-row"><span class="handle">${icon("check")}</span><div><strong>Validation humaine</strong><br><span class="tiny muted">Actions sensibles bloquees.</span></div></div>
          <div class="rule-row"><span class="handle">${icon("copy")}</span><div><strong>Trace complete</strong><br><span class="tiny muted">Decision + explication.</span></div></div>
        </div>
      </article>
    </section>`;
}

function balancingPage() {
  const rows = [
    ["billing", 42, 27],
    ["shipping", 22, 24],
    ["refund", 14, 19],
    ["technical", 11, 16],
    ["other", 11, 14]
  ];
  return `
    ${pageHead(
      "Pipeline 06",
      "Équilibrage des classes",
      "Comparer la distribution avant/après et choisir une stratégie reproductible.",
      `<button class="btn btn-primary" type="button" data-toast="Stratégie d'équilibrage appliquée à une version candidate.">${icon("play")} Équilibrer</button>`
    )}
    <section class="grid grid-3">
      <article class="panel span-2">
        <div class="panel-head"><div><h2>Distribution avant / apres</h2><p>Pourcentage par classe cible.</p></div><span class="chip chip-amber">desequilibre detecte</span></div>
        <div class="balance-bars">
          ${rows
            .map(
              (r) => `<div class="balance-row"><strong>${r[0]}</strong>${progress(r[1], "warn")}<span>${r[1]}%</span></div><div class="balance-row"><span class="muted">cible</span>${progress(r[2])}<span>${r[2]}%</span></div>`
            )
            .join("")}
        </div>
      </article>
      <aside class="panel">
        <div class="panel-head"><div><h2>Stratégie</h2><p>Paramètres configurables.</p></div></div>
        <div class="field"><label>Methode</label><select><option>Undersampling majoritaire</option><option>Oversampling minoritaire</option><option>Poids de classes</option></select></div>
        <div class="field"><label>Classe cible</label><select><option>label</option><option>category</option></select></div>
        <div class="field"><label>Seuil min</label><input value="14%" /></div>
        <div class="recommendation"><strong>Impact estime</strong><span class="tiny">Perte de 3.1% des lignes, score balance +21.</span></div>
      </aside>
    </section>`;
}

function reportPage() {
  return `
    ${pageHead(
      "Validation",
      "Rapport qualité",
      "Synthèse lisible des contrôles, anomalies, transformations et décisions.",
      `<button class="btn" type="button">${icon("download")} PDF</button><button class="btn btn-primary" type="button" data-toast="Rapport régénéré.">${icon("play")} Générer</button>`
    )}
    <section class="grid grid-3">
      <article class="panel span-2">
        <div class="quality-score">
          <div class="donut" style="--value: 87%"><strong>87</strong></div>
          <div>
            <h2>Dataset pret sous reserve</h2>
            <p class="soft">La version v4 peut etre exportee apres decision sur 3 recommandations IA et validation du desequilibre residual.</p>
            <div class="hero-meta">
              <span class="chip chip-pine">Completude 97.6</span>
              <span class="chip chip-amber">Balance 69</span>
              <span class="chip">Traçabilite 100</span>
            </div>
          </div>
        </div>
      </article>
      <article class="panel">
        <div class="panel-head"><div><h2>Decision</h2><p>Statut de validation.</p></div></div>
        ${status("SUCCEEDED_WITH_WARNINGS", "warn")}
        <p class="soft" style="margin-top:var(--sp-4)">Export possible avec avertissements joints aux métadonnées.</p>
      </article>
      <article class="panel span-2">
        <div class="panel-head"><div><h2>Sections du rapport</h2><p>Elements generes et tracables.</p></div></div>
        ${[
          ["Import", "Source conservee, schema detecte, encodage valide.", "ok"],
          ["Nettoyage", "421 doublons supprimés, 1 règle IA acceptée.", "ok"],
          ["Anomalies", "31 anomalies ouvertes dont 8 critiques.", "warn"],
          ["Équilibrage", "Classe billing encore majoritaire.", "warn"]
        ]
          .map((x) => `<div class="report-section"><span>${icon(x[2] === "ok" ? "check" : "alert")}</span><div><strong>${x[0]}</strong><br><span class="soft">${x[1]}</span></div>${status(x[2] === "ok" ? "OK" : "WARN", x[2])}</div>`)
          .join("")}
      </article>
      <article class="panel">
        <div class="panel-head"><div><h2>Journal</h2><p>Opérations récentes.</p></div></div>
        <div class="version-thread">
          <div class="thread-item"><strong>Rapport v4</strong><span>Genere il y a 4 min</span></div>
          <div class="thread-item is-warn"><strong>Balance warning</strong><span>Classe billing 42%</span></div>
          <div class="thread-item"><strong>Cleaning done</strong><span>Worker data</span></div>
        </div>
      </article>
    </section>`;
}

function exportPage() {
  return `
    ${pageHead(
      "Livraison",
      "Export dataset",
      "Formats standards avec métadonnées, annotations et rapport qualité.",
      `<button class="btn btn-primary" type="button" data-toast="Export HF Dataset planifie.">${icon("download")} Exporter</button>`
    )}
    <section class="grid grid-3">
      <article class="panel span-2">
        <div class="panel-head"><div><h2>Formats</h2><p>Selection de la cible d'export.</p></div></div>
        <div class="export-grid">
          ${["CSV", "JSON", "COCO", "YOLO", "Hugging Face"]
            .map((x, i) => `<button class="export-card ${i === 4 ? "is-selected" : ""}" type="button"><div class="file-icon">${icon("download")}</div><strong>${x}</strong><br><span class="tiny muted">${i === 4 ? "selectionne" : "disponible"}</span></button>`)
            .join("")}
        </div>
      </article>
      <aside class="panel">
        <div class="panel-head"><div><h2>Contenu</h2><p>Paquet exporte.</p></div></div>
        <div class="rule-list">
          <div class="rule-row"><span class="handle">${icon("check")}</span><div><strong>Dataset prepare</strong><br><span class="tiny muted">v4</span></div></div>
          <div class="rule-row"><span class="handle">${icon("check")}</span><div><strong>Annotations</strong><br><span class="tiny muted">12 408 labels</span></div></div>
          <div class="rule-row"><span class="handle">${icon("check")}</span><div><strong>Pipeline JSON</strong><br><span class="tiny muted">reutilisable</span></div></div>
          <div class="rule-row"><span class="handle">${icon("check")}</span><div><strong>Rapport qualité</strong><br><span class="tiny muted">warnings inclus</span></div></div>
        </div>
      </aside>
      <article class="panel span-2">
        <div class="panel-head"><div><h2>Manifest export</h2><p>Sortie independante et tracable.</p></div></div>
        <pre class="mono" style="white-space:pre-wrap; margin:0; padding:var(--sp-4); background:var(--surface-alt); border:1px solid var(--line); border-radius:var(--radius-sm); font-size:var(--text-xs)">dataset: customer-support-tickets
version: v4
format: huggingface_dataset
includes:
  - prepared_data
  - annotations
  - transformations
  - quality_report
status: READY_WITH_WARNINGS</pre>
      </article>
      <article class="panel">
        <div class="panel-head"><div><h2>Compatibilité</h2><p>Contrôle avant livraison.</p></div></div>
        <div class="grid">
          <div><strong>Schema</strong>${progress(100)}</div>
          <div><strong>Labels</strong>${progress(92)}</div>
          <div><strong>Métadonnées</strong>${progress(100)}</div>
        </div>
      </article>
    </section>`;
}

function jobsPage() {
  const jobs = [
    ["JOB-2041", "Profilage v4", 68, "RUNNING"],
    ["JOB-2042", "Pre-annotation batch", 18, "QUEUED"],
    ["JOB-2038", "OCR invoice corpus", 100, "SUCCEEDED"],
    ["JOB-2036", "Export COCO", 100, "SUCCEEDED_WITH_WARNINGS"],
    ["JOB-2033", "Detection anomalies", 100, "FAILED"]
  ];
  return `
    ${pageHead(
      "Workers",
      "Suivi des traitements",
      "Cycle de vie technique des jobs: pending, queued, running, succeeded, warnings, failed, cancelled.",
      `<button class="btn" type="button" data-toast="La file de traitements est actualisée.">${icon("clock")} Actualiser</button>`
    )}
    <section class="panel flush">
      <div class="table-toolbar"><h2>File workers</h2><span class="chip">Redis + Celery cible</span></div>
      ${jobs
        .map((j) => {
          const tone = j[3] === "RUNNING" ? "run" : j[3] === "QUEUED" ? "muted" : j[3] === "FAILED" ? "danger" : j[3].includes("WARN") ? "warn" : "ok";
          return `<div class="job-row">
            <div><strong>${j[0]}</strong><span class="tiny muted mono">version_id: v4</span></div>
            <div><strong>${j[1]}</strong>${progress(j[2], tone === "danger" ? "danger" : tone === "warn" ? "warn" : "")}</div>
            <div>${status(j[3], tone)}</div>
            <div class="actions"><button class="btn" type="button">${j[3] === "RUNNING" ? "Annuler" : "Details"}</button></div>
          </div>`;
        })
        .join("")}
    </section>`;
}

const pages = {
  dashboard: dashboardPage,
  projects: projectsPage,
  project: projectPage,
  import: importPage,
  profiling: profilingPage,
  cleaning: cleaningPage,
  documents: documentsPage,
  images: imagesPage,
  annotation: annotationPage,
  ai: aiPage,
  balancing: balancingPage,
  report: reportPage,
  export: exportPage,
  jobs: jobsPage
};

function toast(message, tone = "") {
  const stack = document.getElementById("toastStack");
  if (!stack) return;
  const node = document.createElement("div");
  node.className = `toast ${tone}`;
  node.innerHTML = `${icon(tone === "danger" ? "alert" : tone === "warn" ? "alert" : "check")}<div><strong>${message}</strong><br><span class="tiny muted">Prototype interactif</span></div>`;
  stack.appendChild(node);
  setTimeout(() => {
    node.style.opacity = "0";
    node.style.transform = "translateY(8px)";
    setTimeout(() => node.remove(), 220);
  }, 3200);
}

function render() {
  const active = route();
  document.getElementById("app").innerHTML = shell(active);
  document.getElementById("content").innerHTML = pages[active]();
  document.title = `${routeLabels[active]} - AI Dataset Studio`;
}

document.addEventListener("click", (event) => {
  const railToggle = event.target.closest("[data-action='toggle-rail']");
  if (railToggle) {
    document.getElementById("rail")?.classList.toggle("is-open");
    return;
  }

  const modalOpen = event.target.closest("[data-action='open-modal']");
  if (modalOpen) {
    document.getElementById("projectModal")?.classList.add("is-open");
    return;
  }

  const modalClose = event.target.closest("[data-action='close-modal']");
  if (modalClose || event.target.classList.contains("overlay")) {
    document.getElementById("projectModal")?.classList.remove("is-open");
    return;
  }

  const createProject = event.target.closest("[data-action='create-project']");
  if (createProject) {
    document.getElementById("projectModal")?.classList.remove("is-open");
    toast("Projet dataset créé.");
    location.hash = "#projects";
    return;
  }

  const segment = event.target.closest("[data-segmented] button");
  if (segment) {
    [...segment.parentElement.children].forEach((button) => button.classList.remove("is-active"));
    segment.classList.add("is-active");
    return;
  }

  const toastButton = event.target.closest("[data-toast]");
  if (toastButton) {
    toast(toastButton.dataset.toast);
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    document.getElementById("projectModal")?.classList.remove("is-open");
    document.getElementById("rail")?.classList.remove("is-open");
  }

  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    document.querySelector(".search input")?.focus();
  }
});

window.addEventListener("hashchange", render);
render();
