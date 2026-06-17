<?php
// --- Configuration ---
define('DB_PATH', __DIR__ . '/../deces.sqlite');
define('PER_PAGE', 100);

// --- HTTP headers ---
$cspNonce = base64_encode(random_bytes(16));
header('Content-Type: text/html; charset=UTF-8');
header("Content-Security-Policy: default-src 'self'; style-src 'self' 'nonce-{$cspNonce}' https://fonts.googleapis.com; font-src https://fonts.gstatic.com");
header("X-Content-Type-Options: nosniff");
header("X-Frame-Options: DENY");
header("Referrer-Policy: strict-origin-when-cross-origin");
header("Permissions-Policy: "
     . "camera=(), "          // pas d'accès caméra
     . "microphone=(), "      // pas d'accès micro
     . "geolocation=(), "     // pas de géolocalisation
     . "payment=(), "         // pas d'API paiement
     . "usb=(), "             // pas d'accès USB
     . "interest-cohort=()"   // opt-out FLoC (tracking Google)
);
if (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') {
    header("Strict-Transport-Security: max-age=31536000; includeSubDomains");
}

// --- Database Connection ---
function getDB(): PDO {
    static $pdo = null;
    if ($pdo === null) {
        if (!file_exists(DB_PATH)) {
            error_log('Base de données introuvable : ' . DB_PATH);
            throw new RuntimeException('Base de données inaccessible.');
        }
        $pdo = new PDO('sqlite:' . DB_PATH);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }
    return $pdo;
}

// --- Fetch distinct types for dropdown ---
function getTypes(): array {
    try {
        $pdo  = getDB();
        $rows = $pdo->query("SELECT DISTINCT type FROM cog WHERE type IS NOT NULL ORDER BY type ASC")->fetchAll(PDO::FETCH_COLUMN);
        return $rows;
    } catch (Exception $e) {
        return [];
    }
}

// --- Character conversion function ---
function strToUnaccentuatedUpper($sourceString) {
    $withAccents    = ['à','á','â','ã','ä','ç','è','é','ê','ë','ì','í','î','ï','ñ',
                       'ò','ó','ô','õ','ö','ù','ú','û','ü','ý','ÿ',
                       'À','Á','Â','Ã','Ä','Ç','È','É','Ê','Ë','Ì','Í','Î','Ï','Ñ',
                       'Ò','Ó','Ô','Õ','Ö','Ù','Ú','Û','Ü','Ý','Ÿ'];
    $withoutAccents = ['a','a','a','a','a','c','e','e','e','e','i','i','i','i','n',
                       'o','o','o','o','o','u','u','u','u','y','y',
                       'A','A','A','A','A','C','E','E','E','E','I','I','I','I','N',
                       'O','O','O','O','O','U','U','U','U','Y','Y'];
    $unaccentuatedString = str_replace($withAccents, $withoutAccents, $sourceString);
    return mb_strtoupper($unaccentuatedString, 'UTF-8');
}

// --- Query Builder ---
function buildQuery(array $p, bool $count = false): array {
    $where = [];
    $bind  = [];

    if (!empty($p['code'])) {
        $where[] = "c.code LIKE :code";
        $bind[':code'] = trim($p['code']) . '%';
    }
    if (!empty($p['type'])) {
        $where[] = "c.type = :type";
        $bind[':type'] = $p['type'];
    }
    if (!empty($p['nom'])) {
        $nom = strToUnaccentuatedUpper(trim($p['nom']));
        $where[] = "c.nom_maj LIKE :nom";
        $bind[':nom'] = '%' . str_replace([' ','-'],['_','_'],$nom) . '%';
    }
    if (!empty($p['date_min'])) {
        $where[] = "c.date_debut >= :date_min";
        $bind[':date_min'] = (int)$p['date_min'];
    }
    if (!empty($p['date_max'])) {
        $where[] = "(c.date_fin IS NULL OR c.date_fin <= :date_max)";
        $bind[':date_max'] = (int)$p['date_max'];
    }

    $from     = "FROM cog c";
    $whereStr = $where ? "WHERE " . implode(" AND ", $where) : "";

    if ($count) {
        $sql = "SELECT COUNT(*) $from $whereStr";
    } else {
        $sql = "SELECT c.code, c.type, c.nom_maj, c.nom_riche, c.libelle, c.date_debut, c.date_fin
                $from $whereStr ORDER BY c.nom_maj ASC, c.date_debut ASC";
    }
    return [$sql, $bind];
}

// --- Helpers ---
function h(mixed $v): string {
    return htmlspecialchars((string)($v ?? ''), ENT_QUOTES, 'UTF-8');
}

function pageUrl(int $page, array $params): string {
    $q = array_merge($params, ['page' => $page]);
    return '?' . http_build_query($q);
}

function formatYear(mixed $v): string {
    return $v ? (string)(int)$v : '—';
}

// --- Request Handling ---
$params   = [];
$results  = [];
$total    = 0;
$page     = max(1, (int)($_GET['page'] ?? 1));
$searched = false;
$error    = null;

$fields = ['code', 'type', 'nom', 'date_min', 'date_max'];
foreach ($fields as $f) {
    $params[$f] = mb_substr(trim($_GET[$f] ?? ''), 0, 100, 'UTF-8');
}

// Search triggers if any field is filled
$searched = array_reduce($params, fn($carry, $v) => $carry || $v !== '', false);

if ($searched) {
    try {
        $pdo = getDB();

        [$sqlCount, $bind] = buildQuery($params, true);
        $stmtC = $pdo->prepare($sqlCount);
        $stmtC->execute($bind);
        $total = (int)$stmtC->fetchColumn();

        [$sql, $bind] = buildQuery($params, false);
        $offset = ($page - 1) * PER_PAGE;
        $sql   .= " LIMIT :limit OFFSET :offset";
        $stmt   = $pdo->prepare($sql);
        foreach ($bind as $k => $v) $stmt->bindValue($k, $v);
        $stmt->bindValue(':limit',  PER_PAGE, PDO::PARAM_INT);
        $stmt->bindValue(':offset', $offset,  PDO::PARAM_INT);
        $stmt->execute();
        $results = $stmt->fetchAll(PDO::FETCH_ASSOC);
    } catch (Exception $e) {
        $error = $e->getMessage();
    }
}

$totalPages = $total > 0 ? (int)ceil($total / PER_PAGE) : 1;
$types = getTypes();
?>
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Memento mortuorum - Recherche de lieux</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Mono:wght@300;400&display=swap" rel="stylesheet">
<style nonce="<?= h($cspNonce) ?>">
:root {
    --ink:    #1a1209;
    --paper:  #f5f0e8;
    --cream:  #ede6d6;
    --gold:   #b8860b;
    --rust:   #8b3a2a;
    --muted:  #7a6e5f;
    --rule:   #c8bfad;
    --shadow: rgba(26,18,9,0.12);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
    background: var(--paper);
    color: var(--ink);
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    min-height: 100vh;
}

/* ── HEADER ── */
header {
    background: var(--ink);
    color: var(--paper);
    padding: 2rem 3rem 1.6rem;
    border-bottom: 4px solid var(--gold);
    display: flex;
    align-items: baseline;
    gap: 1.5rem;
    flex-wrap: wrap;
}
header h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(1rem, 2.4vw, 1.55rem);
    letter-spacing: 0.02em;
    color: var(--paper);
    line-height: 1.25;
}
header .subtitle {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 13px;
    letter-spacing: 0.06em;
    color: var(--gold);
    white-space: nowrap;
}

/* ── NAV RIBBON ── */
nav.ribbon {
    background: var(--cream);
    border-bottom: 1px solid var(--rule);
    padding: 0 3rem;
    display: flex;
    align-items: stretch;
    gap: 0;
    flex-wrap: wrap;
}
nav.ribbon a {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    padding: .6rem 1.2rem;
    font-size: 11px;
    letter-spacing: .1em;
    text-transform: uppercase;
    text-decoration: none;
    color: var(--muted);
    border-right: 1px solid var(--rule);
    transition: background .15s, color .15s;
    white-space: nowrap;
}
nav.ribbon a:first-child { border-left: 1px solid var(--rule); }
nav.ribbon a:hover { background: var(--paper); color: var(--rust); }
nav.ribbon a.active { background: var(--paper); color: var(--rust); border-bottom: 2px solid var(--rust); }
nav.ribbon a svg { flex-shrink: 0; }
@media (max-width: 640px) {
    nav.ribbon { padding: 0 1rem; }
    nav.ribbon a { padding: .55rem .8rem; font-size: 10px; gap: .3rem; }
}

/* ── LAYOUT ── */
.wrapper { max-width: 1200px; margin: 0 auto; padding: 2rem; }

/* ── SEARCH PANEL ── */
.search-panel {
    background: var(--cream);
    border: 1px solid var(--rule);
    border-top: 3px solid var(--rust);
    padding: 1.8rem 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 12px var(--shadow);
}
.search-panel > legend {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    color: var(--rust);
    letter-spacing: 0.05em;
    margin-bottom: 1.2rem;
    display: block;
    border-bottom: 1px solid var(--rule);
    padding-bottom: .5rem;
}

.form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: .9rem 1.2rem;
    align-items: end;
}

.form-group { display: flex; flex-direction: column; gap: .3rem; }
.form-group label, .range-pair-label {
    font-size: 10px;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--muted);
}
.form-group input[type=text],
.form-group input[type=number],
.form-group select {
    background: var(--paper);
    border: 1px solid var(--rule);
    color: var(--ink);
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    padding: .45rem .7rem;
    outline: none;
    transition: border-color .15s;
    -webkit-appearance: none;
    border-radius: 0;
    width: 100%;
}
.form-group input:focus, .form-group select:focus { border-color: var(--gold); }

.range-pair { display: grid; grid-template-columns: 1fr 1fr; gap: .5rem; }
.range-pair-label { margin-bottom: .3rem; display: block; }

.form-hint {
    font-size: 10px;
    color: var(--muted);
    letter-spacing: .04em;
    margin-top: .25rem;
    font-style: italic;
}

.form-actions {
    display: flex; gap: .8rem; align-items: center;
    margin-top: 1.2rem; border-top: 1px solid var(--rule); padding-top: 1rem;
}
button[type=submit] {
    background: var(--rust); color: var(--paper);
    border: none; font-family: 'DM Mono', monospace;
    font-size: 12px; letter-spacing: .1em; text-transform: uppercase;
    padding: .6rem 1.8rem; cursor: pointer; transition: background .15s;
}
button[type=submit]:hover { background: var(--gold); }
a.reset-link { font-size: 11px; color: var(--muted); text-decoration: none; letter-spacing: .06em; }
a.reset-link:hover { color: var(--rust); }

/* ── RESULTS HEADER ── */
.results-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: .8rem; border-bottom: 1px solid var(--rule);
    padding-bottom: .5rem; flex-wrap: wrap; gap: .5rem;
}
.results-header .count { font-family: 'Playfair Display', serif; font-size: 1.05rem; }
.results-header .count em { color: var(--rust); font-style: normal; font-weight: 700; }
.results-header .page-info { font-size: 11px; color: var(--muted); letter-spacing: .06em; }

/* ── TABLE ── */
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
thead tr { background: var(--ink); color: var(--paper); }
thead th {
    font-family: 'DM Mono', monospace; font-weight: 400;
    font-size: 10px; letter-spacing: .12em; text-transform: uppercase;
    padding: .55rem .75rem; text-align: left; white-space: nowrap;
    border-right: 1px solid #2e2416;
}
thead th:last-child { border-right: none; }
tbody tr { border-bottom: 1px solid var(--rule); transition: background .1s; }
tbody tr:nth-child(even) { background: var(--cream); }
tbody tr:hover { background: #e3d9c6; }
tbody td { padding: .45rem .75rem; vertical-align: top; white-space: nowrap; }

td.num-cell   { color: var(--rule); font-size: 11px; text-align: right; }
td.code-cell  { font-family: 'DM Mono', monospace; font-weight: 400; color: var(--rust); letter-spacing: .06em; }
td.type-cell  { font-size: 11px; color: var(--muted); }
td.nom-cell   { font-family: 'Playfair Display', serif; font-size: 13px; font-weight: 700; color: var(--ink); }
td.rich-cell  { color: var(--ink); }
td.lib-cell   { color: var(--muted); font-size: 11.5px; max-width: 220px; overflow: hidden; text-overflow: ellipsis; }
td.date-cell  { color: var(--muted); font-size: 11.5px; white-space: nowrap; }

/* ── TYPE BADGE ── */
.type-badge {
    display: inline-block;
    background: var(--ink);
    color: var(--paper);
    font-size: 9px;
    letter-spacing: .1em;
    text-transform: uppercase;
    padding: .15rem .45rem;
}

/* ── PAGINATION ── */
.pagination { display: flex; align-items: center; gap: .4rem; margin-top: 1.5rem; flex-wrap: wrap; }
.pagination a, .pagination span {
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 2rem; height: 2rem; padding: 0 .5rem;
    text-decoration: none; font-size: 12px; border: 1px solid var(--rule);
    color: var(--ink); transition: background .12s, border-color .12s;
}
.pagination a:hover { background: var(--cream); border-color: var(--gold); }
.pagination .active { background: var(--rust); color: var(--paper); border-color: var(--rust); pointer-events: none; }
.pagination .disabled { color: var(--rule); pointer-events: none; }
.pagination .ellipsis { border: none; color: var(--muted); pointer-events: none; }

/* ── NOTICES ── */
.notice {
    padding: 2rem; text-align: center; color: var(--muted);
    font-size: 12px; letter-spacing: .06em;
    border: 1px dashed var(--rule); background: var(--cream);
}
.notice.error { color: var(--rust); border-color: var(--rust); border-style: solid; }
.notice .big { font-family: 'Playfair Display', serif; font-size: 2rem; display: block; margin-bottom: .5rem; color: var(--rule); }

/* ── FOOTER ── */
footer.ribbon {
    background: var(--ink);
    border-top: 4px solid var(--gold);
    padding: 0 3rem;
    display: flex;
    align-items: stretch;
    gap: 0;
    flex-wrap: wrap;
    margin-top: 2rem;
}
footer.ribbon a {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    padding: .6rem 1.2rem;
    font-size: 11px;
    letter-spacing: .1em;
    text-transform: uppercase;
    text-decoration: none;
    color: var(--paper);
    opacity: .65;
    border-right: 1px solid #2e2416;
    transition: opacity .15s, color .15s;
    white-space: nowrap;
}
footer.ribbon a:first-child { border-left: 1px solid #2e2416; }
footer.ribbon a:hover { opacity: 1; color: var(--gold); }
footer.ribbon a svg { flex-shrink: 0; }
@media (max-width: 640px) {
    footer.ribbon { padding: 0 1rem; }
    footer.ribbon a { padding: .55rem .8rem; font-size: 10px; gap: .3rem; }
}

/* ── TOOLTIPS ── */
.has-tooltip {
    position: relative;
    cursor: help;
    border-bottom: 1px dotted var(--muted);
}
.has-tooltip::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: calc(100% + 6px);
    left: 0;
    background: var(--ink);
    color: var(--paper);
    font-size: 10px;
    letter-spacing: .05em;
    text-transform: none;
    white-space: nowrap;
    padding: .35rem .65rem;
    pointer-events: none;
    opacity: 0;
    transition: opacity .15s;
    z-index: 10;
}
.has-tooltip::before {
    content: '';
    position: absolute;
    bottom: calc(100% + 1px);
    left: .7rem;
    border: 5px solid transparent;
    border-top-color: var(--ink);
    pointer-events: none;
    opacity: 0;
    transition: opacity .15s;
    z-index: 10;
}
.has-tooltip:hover::after,
.has-tooltip:hover::before { opacity: 1; }

/* ── RESPONSIVE ── */
@media (max-width: 640px) {
    header { padding: 1rem 1.2rem; flex-direction: column; gap: .3rem; }
    .wrapper { padding: 1rem; }
    .search-panel { padding: 1.2rem; }
    tbody td { white-space: normal; }
}
</style>
</head>
<body>

<header>
    <h1>Recherche dans les Codes Officiels Géographiques depuis 1943</h1>
    <span class="subtitle">Memento mortuorum</span>
</header>

<nav class="ribbon">
    <a href="index.php">
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="8" cy="4.5" r="2.5"/><path d="M2 14c0-3.3 2.7-6 6-6s6 2.7 6 6"/>
        </svg>
        Recherche de personnes
    </a>
    <a href="lieux.php" class="active">
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="8" cy="6" r="2.5"/><path d="M8 1C5.2 1 3 3.2 3 6c0 4 5 9 5 9s5-5 5-9c0-2.8-2.2-5-5-5z"/>
        </svg>
        Recherche de lieux
    </a>
    <a href="stats.html">
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <rect x="1" y="9" width="3" height="6"/><rect x="6.5" y="5" width="3" height="10"/><rect x="12" y="1" width="3" height="14"/>
        </svg>
        Statistiques
    </a>
</nav>

<div class="wrapper">

    <!-- ── SEARCH FORM ── -->
    <form method="get" action="">
    <div class="search-panel">
        <legend>Critères de recherche</legend>
        <div class="form-grid">

            <div class="form-group">
                <label for="code"><span class="has-tooltip" data-tooltip="un Code Officiel Géographique ou son début pour une recherche par département">Code</span></label>
                <input type="text" id="code" name="code" value="<?= h($params['code']) ?>" placeholder="ex. 75101" autocomplete="off">
            </div>

            <div class="form-group">
                <label for="type">Type</label>
                <select id="type" name="type">
                    <option value="">— Tous —</option>
                    <?php foreach ($types as $t): ?>
                    <option value="<?= h($t) ?>" <?= $params['type'] === $t ? 'selected' : '' ?>><?= h($t) ?></option>
                    <?php endforeach; ?>
                </select>
            </div>

            <div class="form-group">
                <label for="nom">Nom</label>
                <input type="text" id="nom" name="nom" value="<?= h($params['nom']) ?>" placeholder="ex. PARIS ou Paris" autocomplete="off">
            </div>

            <div class="form-group">
                <span class="range-pair-label">Dates (début / fin)</span>
                <div class="range-pair">
                    <input type="text" name="date_min" value="<?= h($params['date_min']) ?>" placeholder="AAAAMMJJ">
                    <input type="text" name="date_max" value="<?= h($params['date_max']) ?>" placeholder="AAAAMMJJ">
                </div>
            </div>

        </div>

        <div class="form-actions">
            <button type="submit">Rechercher</button>
            <a href="lieux.php" class="reset-link">Réinitialiser</a>
        </div>
    </div>
    </form>

    <!-- ── ERROR ── -->
    <?php if ($error): ?>
    <div class="notice error"><span class="big">!</span><?= h($error) ?></div>

    <!-- ── NO SEARCH YET ── -->
    <?php elseif (!$searched): ?>
    <div class="notice">
        <span class="big">⊙</span>
        Renseignez au moins un critère pour lancer la recherche.
    </div>

    <!-- ── NO RESULTS ── -->
    <?php elseif ($total === 0): ?>
    <div class="notice">
        <span class="big">∅</span>
        Aucun résultat pour ces critères.
    </div>

    <!-- ── RESULTS ── -->
    <?php else: ?>

    <div class="results-header">
        <div class="count">
            <em><?= number_format($total, 0, ',', '&nbsp;') ?></em>
            résultat<?= $total > 1 ? 's' : '' ?>
        </div>
        <div class="page-info">Page <?= $page ?> / <?= $totalPages ?></div>
    </div>

    <div class="table-wrap">
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Code</th>
                <th>Type</th>
                <th>Nom (maj)</th>
                <th>Nom (riche)</th>
                <th>Libellé</th>
                <th>Date début</th>
                <th>Date fin</th>
            </tr>
        </thead>
        <tbody>
        <?php foreach ($results as $i => $r): ?>
            <tr>
                <td class="num-cell"><?= ($page - 1) * PER_PAGE + $i + 1 ?></td>
                <td class="code-cell"><?= h($r['code']) ?></td>
                <td class="type-cell"><span class="type-badge"><?= h($r['type']) ?></span></td>
                <td class="nom-cell"><?= h($r['nom_maj']) ?: '—' ?></td>
                <td class="rich-cell"><?= h($r['nom_riche']) ?: '—' ?></td>
                <td class="lib-cell" title="<?= h($r['libelle']) ?>"><?= h($r['libelle']) ?: '—' ?></td>
                <td class="date-cell"><?= formatYear($r['date_debut']) ?></td>
                <td class="date-cell"><?= formatYear($r['date_fin']) ?></td>
            </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
    </div>

    <!-- ── PAGINATION ── -->
    <?php if ($totalPages > 1): ?>
    <nav class="pagination" aria-label="Pagination">
        <?php if ($page > 1): ?>
            <a href="<?= pageUrl($page - 1, $params) ?>">&lsaquo; Préc.</a>
        <?php else: ?>
            <span class="disabled">&lsaquo; Préc.</span>
        <?php endif; ?>

        <?php
        $window = 2;
        $start  = max(1, $page - $window);
        $end    = min($totalPages, $page + $window);
        if ($start > 1): ?>
            <a href="<?= pageUrl(1, $params) ?>">1</a>
            <?php if ($start > 2): ?><span class="ellipsis">…</span><?php endif; ?>
        <?php endif; ?>

        <?php for ($pg = $start; $pg <= $end; $pg++): ?>
            <?php if ($pg === $page): ?>
                <span class="active"><?= $pg ?></span>
            <?php else: ?>
                <a href="<?= pageUrl($pg, $params) ?>"><?= $pg ?></a>
            <?php endif; ?>
        <?php endfor; ?>

        <?php if ($end < $totalPages): ?>
            <?php if ($end < $totalPages - 1): ?><span class="ellipsis">…</span><?php endif; ?>
            <a href="<?= pageUrl($totalPages, $params) ?>"><?= $totalPages ?></a>
        <?php endif; ?>

        <?php if ($page < $totalPages): ?>
            <a href="<?= pageUrl($page + 1, $params) ?>">Suiv. &rsaquo;</a>
        <?php else: ?>
            <span class="disabled">Suiv. &rsaquo;</span>
        <?php endif; ?>
    </nav>
    <?php endif; ?>

    <?php endif; ?>

</div><!-- /wrapper -->

<footer class="ribbon">
    <a href="https://github.com/HubTou" target="_blank" rel="noopener noreferrer">
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="8" cy="5" r="2.5"/><path d="M3 14c0-2.8 2.2-5 5-5s5 2.2 5 5"/>
        </svg>
        À propos de l'auteur
    </a>
    <a href="https://github.com/HubTou/Memento_mortuorum" target="_blank" rel="noopener noreferrer">
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="5,4 1,8 5,12"/><polyline points="11,4 15,8 11,12"/>
        </svg>
        Code source
    </a>
    <a href="https://www.insee.fr/fr/information/4190491" target="_blank" rel="noopener noreferrer">
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="5,4 1,8 5,12"/><polyline points="11,4 15,8 11,12"/>
        </svg>
        Données sources
    </a>
    <a href="https://github.com/HubTou/Memento_mortuorum/discussions" target="_blank" rel="noopener noreferrer">
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 12h4M6.5 14h3"/>
            <path d="M8 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V11H6V9.5C4.8 8.8 4 7.5 4 6a4 4 0 0 1 4-4z"/>
            <line x1="8" y1="2" x2="8" y2="1"/>
            <line x1="3.5" y1="3.5" x2="2.8" y2="2.8"/>
            <line x1="12.5" y1="3.5" x2="13.2" y2="2.8"/>
        </svg>
        Suggestions
    </a>
</footer>
</body>
</html>
