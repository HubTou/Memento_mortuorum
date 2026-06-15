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

// --- Query Logic ---
function buildQuery(array $p, string $mode = 'results'): array {
    // NOM: exact or LIKE
    if (!empty($p['nom_approx'])) {
        $nomWhere = "p.nom LIKE :nom";
        $bind = [':nom' => '%' . strToUnaccentuatedUpper(str_replace([' ','-'],['_','_'],trim($p['nom']))) . '%'];
    } else {
        $nomWhere = "p.nom = :nom";
        $bind = [':nom' => strToUnaccentuatedUpper(trim($p['nom']))];
    }

    $where = [$nomWhere];

    // Opposition filter — direction depends on mode
    if ($mode === 'opposition') {
        $where[] = "p.opposition = 1";
    } else {
        $where[] = "(p.opposition IS NULL OR p.opposition != 1)";
    }

    if (!empty($p['prenom'])) {
        if (!empty($p['prenom_approx'])) {
            if (!empty($p['premier_prenom'])) {
                $where[] = "pr.prenom LIKE :prenom";
                $where[] = "pp.ordre = 1";
            } else {
                $where[] = "pr.prenom LIKE :prenom";
            }
            $bind[':prenom'] = '%' . strToUnaccentuatedUpper(str_replace([' ','-'],['_','_'],trim($p['prenom']))) . '%';
        } else {
            if (!empty($p['premier_prenom'])) {
                $where[] = "pr.prenom = :prenom";
                $where[] = "pp.ordre = 1";
            } else {
                $where[] = "pr.prenom = :prenom";
            }
            $bind[':prenom'] = strToUnaccentuatedUpper(trim($p['prenom']));
        }
    }
    if (!empty($p['sexe']) && in_array($p['sexe'], ['1','2'])) {
        $where[] = "p.sexe = :sexe";
        $bind[':sexe'] = (int)$p['sexe'];
    }
    if (!empty($p['jour_naissance'])) {
        $where[] = "p.jour_naissance = :jn";
        $bind[':jn'] = (int)$p['jour_naissance'];
    }
    if (!empty($p['mois_naissance'])) {
        $where[] = "p.mois_naissance = :mn";
        $bind[':mn'] = (int)$p['mois_naissance'];
    }
    if (!empty($p['annee_naissance_min']) and !empty($p['annee_naissance_max'])) {
        $where[] = "p.annee_naissance >= :an_min AND p.annee_naissance <= :an_max";
        $bind[':an_min'] = (int)$p['annee_naissance_min'];
        $bind[':an_max'] = (int)$p['annee_naissance_max'];
    }
    elseif (!empty($p['annee_naissance_min'])) {
        $where[] = "p.annee_naissance = :an";
        $bind[':an'] = (int)$p['annee_naissance_min'];
    }
    elseif (!empty($p['annee_naissance_max'])) {
        $where[] = "p.annee_naissance = :an";
        $bind[':an'] = (int)$p['annee_naissance_max'];
    }
    if (!empty($p['lieu_naissance'])) {
        $where[] = "p.lieu_naissance LIKE :ln";
        $bind[':ln'] = strToUnaccentuatedUpper(trim($p['lieu_naissance'])) . '%';
    }
    if (!empty($p['commune_naissance'])) {
        $where[] = "p.commune_naissance LIKE :cn";
        $bind[':cn'] = '%' . strToUnaccentuatedUpper(trim($p['commune_naissance'])) . '%';
    }
    if (!empty($p['pays_naissance'])) {
        $where[] = "p.pays_naissance LIKE :pn";
        $bind[':pn'] = '%' . strToUnaccentuatedUpper(trim($p['pays_naissance'])) . '%';
    }
    if (!empty($p['id_personne'])) {
        $where[] = "p.id = :ip";
        $bind[':ip'] = strToUnaccentuatedUpper(trim($p['id_personne']));
    }
    if (!empty($p['jour_deces'])) {
        $where[] = "p.jour_deces = :jd";
        $bind[':jd'] = (int)$p['jour_deces'];
    }
    if (!empty($p['mois_deces'])) {
        $where[] = "p.mois_deces = :md";
        $bind[':md'] = (int)$p['mois_deces'];
    }
    if (!empty($p['annee_deces_min']) and !empty($p['annee_deces_max'])) {
        $where[] = "p.annee_deces >= :ad_min AND p.annee_deces <= :ad_max";
        $bind[':ad_min'] = (int)$p['annee_deces_min'];
        $bind[':ad_max'] = (int)$p['annee_deces_max'];
    }
    elseif (!empty($p['annee_deces_min'])) {
        $where[] = "p.annee_deces = :ad";
        $bind[':ad'] = (int)$p['annee_deces_min'];
    }
    elseif (!empty($p['annee_deces_max'])) {
        $where[] = "p.annee_deces = :ad";
        $bind[':ad'] = (int)$p['annee_deces_max'];
    }
    if (!empty($p['lieu_deces'])) {
        $where[] = "p.lieu_deces LIKE :ld";
        $bind[':ld'] = strToUnaccentuatedUpper(trim($p['lieu_deces'])) . '%';
    }
    if (!empty($p['commune_deces'])) {
        $where[] = "p.commune_deces LIKE :cd";
        $bind[':cd'] = '%' . strToUnaccentuatedUpper(trim($p['commune_deces'])) . '%';
    }
    if (!empty($p['pays_deces'])) {
        $where[] = "p.pays_deces LIKE :pd";
        $bind[':pd'] = '%' . strToUnaccentuatedUpper(trim($p['pays_deces'])) . '%';
    }
    if (!empty($p['acte_deces'])) {
        $where[] = "p.acte_deces = :acte";
        $bind[':acte'] = trim($p['acte_deces']);
    }

    $join     = "FROM personnes p LEFT JOIN prenoms_personne pp ON pp.id_personne = p.id LEFT JOIN prenoms pr ON pr.id = pp.id_prenom";
    $whereStr = "WHERE " . implode(" AND ", $where);

    if ($mode === 'count' || $mode === 'opposition') {
        $sql = "SELECT COUNT(DISTINCT p.id) $join $whereStr";
    } else {
        $sql = "SELECT DISTINCT p.id, p.nom, p.prenoms, p.sexe,
                    p.annee_naissance, p.mois_naissance, p.jour_naissance,
                    p.lieu_naissance, p.commune_naissance, p.pays_naissance,
                    p.annee_deces, p.mois_deces, p.jour_deces,
                    p.lieu_deces, p.commune_deces, p.pays_deces, p.acte_deces
                $join $whereStr ORDER BY p.nom ASC, p.date_naissance ASC";
    }
    return [$sql, $bind];
}

// --- Request Handling ---
$params   = [];
$results  = [];
$total    = 0;
$excluded = 0;
$page     = max(1, (int)($_GET['page'] ?? 1));
$searched = false;
$error    = null;

$fields = ['nom','nom_approx','prenom','prenom_approx','premier_prenom','sexe',
           'jour_naissance','mois_naissance','annee_naissance_min','annee_naissance_max',
           'lieu_naissance','commune_naissance','pays_naissance',
           'jour_deces','mois_deces','annee_deces_min','annee_deces_max',
           'lieu_deces','commune_deces','pays_deces','acte_deces','id_personne'];
foreach ($fields as $f) {
    $params[$f] = mb_substr(trim($_GET[$f] ?? ''), 0, 100, 'UTF-8');
}

if (!empty($_GET['nom'])) {
    $searched = true;
    try {
        $pdo = getDB();

        // Visible results count (opposition excluded)
        [$sqlCount, $bind] = buildQuery($params, 'count');
        $stmtC = $pdo->prepare($sqlCount);
        $stmtC->execute($bind);
        $total = (int)$stmtC->fetchColumn();

        // Excluded (opposition=1) count
        [$sqlOpp, $bindOpp] = buildQuery($params, 'opposition');
        $stmtO = $pdo->prepare($sqlOpp);
        $stmtO->execute($bindOpp);
        $excluded = (int)$stmtO->fetchColumn();

        // Paginated results
        [$sql, $bind] = buildQuery($params, 'results');
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

function formatDate(mixed $y, mixed $m, mixed $d): string {
    if (!$y) return '—';
    $parts = [];
    if ($d) $parts[] = str_pad((string)(int)$d, 2, '0', STR_PAD_LEFT);
    if ($m) $parts[] = str_pad((string)(int)$m, 2, '0', STR_PAD_LEFT);
    $parts[] = (string)(int)$y;
    return implode('/', $parts);
}

function h(mixed $v): string {
    return htmlspecialchars((string)($v ?? ''), ENT_QUOTES, 'UTF-8');
}

function pageUrl(int $page, array $params): string {
    $q = array_merge($params, ['page' => $page]);
    return '?' . http_build_query($q);
}

function ck(string $key, array $params): string {
    return !empty($params[$key]) ? 'checked' : '';
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Memento mortuorum - Recherche de personnes</title>
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
nav.ribbon a.active { background: var(--paper); color: var(--rust); border-bottom: 2px solid var(--rust); font-weight: 400; }
nav.ribbon a svg { flex-shrink: 0; }
@media (max-width: 640px) {
    nav.ribbon { padding: 0 1rem; }
    nav.ribbon a { padding: .55rem .8rem; font-size: 10px; gap: .3rem; }
}

/* ── LAYOUT ── */
.wrapper { max-width: 1400px; margin: 0 auto; padding: 2rem; }

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

/* Top row: NOM + approximatif | PRÉNOM + approximatif + le_premier | SEXE */
.form-top-row {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr 1fr;
    gap: .9rem 1rem;
    align-items: end;
    margin-bottom: 1.2rem;
}

/* Two-column section for naissance / décès */
.form-sections {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.2rem 2.5rem;
    margin-bottom: .6rem;
}
.form-section-title {
    font-size: 10px;
    letter-spacing: .15em;
    text-transform: uppercase;
    color: var(--rust);
    border-bottom: 1px solid var(--rule);
    padding-bottom: .3rem;
    margin-bottom: .8rem;
}
.form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(175px, 1fr));
    gap: .85rem 1.1rem;
    align-items: end;
}

.form-group { display: flex; flex-direction: column; gap: .3rem; }
.form-group label, .range-pair-label {
    font-size: 10px;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0;
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
.form-group.required label::after { content: ' *'; color: var(--rust); }

/* Inline checkbox */
.cb-group {
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding-bottom: .1rem;
}
.cb-label {
    display: flex;
    align-items: center;
    gap: .45rem;
    cursor: pointer;
    white-space: nowrap;
    height: 2rem; /* match input height */
    padding: 0 .3rem;
    border: 1px solid transparent;
}
.cb-label input[type=checkbox] {
    width: 14px; height: 14px;
    accent-color: var(--rust);
    flex-shrink: 0;
    cursor: pointer;
}
.cb-label span {
    font-size: 10px;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--muted);
    user-select: none;
}

.range-pair { display: grid; grid-template-columns: 1fr 1fr; gap: .5rem; }
.range-pair-label { margin-bottom: .3rem; display: block; }

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
.results-header .right { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
.results-header .page-info { font-size: 11px; color: var(--muted); letter-spacing: .06em; }
.excluded-note {
    font-size: 11px; color: var(--muted); letter-spacing: .04em;
    background: var(--cream); border: 1px solid var(--rule);
    border-left: 3px solid var(--gold); padding: .25rem .7rem;
}
.excluded-note em { color: var(--gold); font-style: normal; font-weight: 700; }

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
td.num-cell { color: var(--rule); font-size: 11px; text-align: right; }
td.nom-cell { font-family: 'Playfair Display', serif; font-size: 13px; font-weight: 700; color: var(--rust); }
td.prenoms-cell { color: var(--ink); }
td.date-cell { color: var(--muted); font-size: 11.5px; }
td.lieu-cell { color: var(--muted); font-size: 11.5px; }
td.sexe-cell { text-align: center; }
.sexe-m { color: #1a4a7a; }
.sexe-f { color: var(--rust); }
td.acte-cell { font-size: 11px; max-width: 130px; overflow: hidden; text-overflow: ellipsis; color: var(--muted); }

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
.notice code { font-family: 'DM Mono', monospace; font-size: 11px; background: #e8e0ce; padding: .1rem .4rem; }

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
@media (max-width: 1000px) {
    .form-top-row { grid-template-columns: 1fr auto 1fr; }
    .form-sections { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
    header { padding: 1rem 1.2rem; flex-direction: column; gap: .3rem; }
    .wrapper { padding: 1rem; }
    .search-panel { padding: 1.2rem; }
    .form-top-row { grid-template-columns: 1fr auto; }
    tbody td { white-space: normal; }
}
</style>
</head>
<body>

<header>
    <h1>Recherche dans la base INSEE des personnes décédées depuis 1970</h1>
    <span class="subtitle">Memento mortuorum</span>
</header>

<nav class="ribbon">
    <a href="index.php" class="active">
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="8" cy="4.5" r="2.5"/><path d="M2 14c0-3.3 2.7-6 6-6s6 2.7 6 6"/>
        </svg>
        Recherche de personnes
    </a>
    <a href="lieux.php">
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

        <!-- Top row -->
        <div class="form-top-row">

            <div class="form-group required">
                <label for="nom">Nom</label>
                <input type="text" id="nom" name="nom" value="<?= h($params['nom']) ?>" placeholder="ex. MARTIN" autocomplete="off">
            </div>
            <div class="cb-group">
                <label class="cb-label" for="nom_approx">
                    <input type="checkbox" id="nom_approx" name="nom_approx" value="1" <?= ck('nom_approx', $params) ?>>
                    <span><span class="has-tooltip" data-tooltip="si coché: le nom de famille est partiel et ne tient pas compte des espaces ou tirets">Approx.</span></span>
                </label>
            </div>

            <div class="form-group">
                <label for="prenom"><span class="has-tooltip" data-tooltip="un seul des prénoms, quel que soit son ordre, ou un prénom composé">Un prénom</span></label>
                <input type="text" id="prenom" name="prenom" value="<?= h($params['prenom']) ?>" placeholder="ex. Marie" autocomplete="off">
            </div>
            <div class="cb-group">
                <label class="cb-label" for="prenom_approx">
                    <input type="checkbox" id="prenom_approx" name="prenom_approx" value="1" <?= ck('prenom_approx', $params) ?>>
                    <span><span class="has-tooltip" data-tooltip="si coché: le prénom est partiel et ne tient pas compte des espaces ou tirets">Approx.</span></span>
                </label>
            </div>
            <div class="cb-group">
                <label class="cb-label" for="premier_prenom">
                    <input type="checkbox" id="premier_prenom" name="premier_prenom" value="1" <?= ck('premier_prenom', $params) ?>>
                    <span><span class="has-tooltip" data-tooltip="si coché: uniquement le premier prénom">Le premier</span></span>
                </label>
            </div>

            <div class="form-group">
                <label for="sexe">Sexe</label>
                <select id="sexe" name="sexe">
                    <option value="">— Tous —</option>
                    <option value="1" <?= $params['sexe']==='1'?'selected':'' ?>>Masculin</option>
                    <option value="2" <?= $params['sexe']==='2'?'selected':'' ?>>Féminin</option>
                </select>
            </div>

        </div><!-- /form-top-row -->

        <!-- Naissance | Décès sections -->
        <div class="form-sections">

            <div>
                <div class="form-section-title">Naissance</div>
                <div class="form-grid">
                    <div class="form-group">
                        <span class="range-pair-label">Date</span>
                        <div class="range-pair">
                            <input type="number" name="jour_naissance" value="<?= h($params['jour_naissance']) ?>" placeholder="jour" min="1" max="31">
                            <input type="number" name="mois_naissance" value="<?= h($params['mois_naissance']) ?>" placeholder="mois" min="1" max="12">
                        </div>
                    </div>
                    <div class="form-group">
                        <span class="range-pair-label"><span class="has-tooltip" data-tooltip="une année pour une recherche exacte ou deux pour une recherche sur l'intervalle">Année</span></span>
                        <div class="range-pair">
                            <input type="number" name="annee_naissance_min" value="<?= h($params['annee_naissance_min']) ?>" placeholder="de" min="0" max="2100">
                            <input type="number" name="annee_naissance_max" value="<?= h($params['annee_naissance_max']) ?>" placeholder="à" min="1848" max="2100">
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="lieu_naissance"><span class="has-tooltip" data-tooltip="un Code Officiel Géographique ou son début pour une recherche par département">COG / Département</span></label>
                        <input type="text" id="lieu_naissance" name="lieu_naissance" value="<?= h($params['lieu_naissance']) ?>" placeholder="ex. 01174 ou 01" autocomplete="off">
                    </div>
                    <div class="form-group">
                        <label for="commune_naissance">Commune</label>
                        <input type="text" id="commune_naissance" name="commune_naissance" value="<?= h($params['commune_naissance']) ?>" placeholder="ex. Paris" autocomplete="off">
                    </div>
                    <div class="form-group">
                        <label for="pays_naissance">Pays</label>
                        <input type="text" id="pays_naissance" name="pays_naissance" value="<?= h($params['pays_naissance']) ?>" placeholder="ex. France" autocomplete="off">
                    </div>
                    <div class="form-group">
                        <label for="id_personne"><span class="has-tooltip" data-tooltip="L'identifiant interne d'une personne dans notre base de données">Clé</span></label>
                        <input type="text" id="id_personne" name="id_personne" value="<?= h($params['id_personne']) ?>" autocomplete="off">
                    </div>
                </div>
            </div>

            <div>
                <div class="form-section-title">Décès</div>
                <div class="form-grid">
                    <div class="form-group">
                        <span class="range-pair-label">Date</span>
                        <div class="range-pair">
                            <input type="number" name="jour_deces" value="<?= h($params['jour_deces']) ?>" placeholder="jour" min="1" max="31">
                            <input type="number" name="mois_deces" value="<?= h($params['mois_deces']) ?>" placeholder="mois" min="1" max="12">
                        </div>
                    </div>
                    <div class="form-group">
                        <span class="range-pair-label"><span class="has-tooltip" data-tooltip="une année pour une recherche exacte ou deux pour une recherche sur l'intervalle">Année</span></span>
                        <div class="range-pair">
                            <input type="number" name="annee_deces_min" value="<?= h($params['annee_deces_min']) ?>" placeholder="de" min="0" max="2100">
                            <input type="number" name="annee_deces_max" value="<?= h($params['annee_deces_max']) ?>" placeholder="à" min="1882" max="2100">
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="lieu_deces"><span class="has-tooltip" data-tooltip="un Code Officiel Géographique ou son début pour une recherche par département">COG / Département</span></label>
                        <input type="text" id="lieu_deces" name="lieu_deces" value="<?= h($params['lieu_deces']) ?>" placeholder="ex. 01174 ou 01" autocomplete="off">
                    </div>
                    <div class="form-group">
                        <label for="commune_deces">Commune</label>
                        <input type="text" id="commune_deces" name="commune_deces" value="<?= h($params['commune_deces']) ?>" placeholder="ex. Brest" autocomplete="off">
                    </div>
                    <div class="form-group">
                        <label for="pays_deces">Pays</label>
                        <input type="text" id="pays_deces" name="pays_deces" value="<?= h($params['pays_deces']) ?>" placeholder="ex. France" autocomplete="off">
                    </div>
                    <div class="form-group">
                        <label for="acte_deces">Acte</label>
                        <input type="text" id="acte_deces" name="acte_deces" value="<?= h($params['acte_deces']) ?>" placeholder="ex. 42" autocomplete="off">
                    </div>
                </div>
            </div>

        </div><!-- /form-sections -->

        <div class="form-actions">
            <button type="submit">Rechercher</button>
            <a href="?" class="reset-link">Réinitialiser</a>
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
        Saisissez un nom pour lancer la recherche.
    </div>

    <!-- ── NO RESULTS ── -->
    <?php elseif ($total === 0): ?>
    <div class="notice">
        <span class="big">∅</span>
        Aucun résultat pour ces critères.
        <?php if ($excluded > 0): ?>
        <br><br>
        <span style="color:var(--gold)">
            <?= number_format($excluded, 0, ',', '&nbsp;') ?> résultat<?= $excluded>1?'s':'' ?>
            exclu<?= $excluded>1?'s':'' ?> (opposition)
        </span>
        <?php endif; ?>
    </div>

    <!-- ── RESULTS ── -->
    <?php else: ?>

    <div class="results-header">
        <div class="count">
            <em><?= number_format($total, 0, ',', '&nbsp;') ?></em>
            résultat<?= $total > 1 ? 's' : '' ?>
        </div>
        <div class="right">
            <?php if ($excluded > 0): ?>
            <div class="excluded-note">
                <em><?= number_format($excluded, 0, ',', '&nbsp;') ?></em>
                résultat<?= $excluded>1?'s':'' ?> exclu<?= $excluded>1?'s':'' ?> (opposition)
            </div>
            <?php endif; ?>
            <div class="page-info">Page <?= $page ?> / <?= $totalPages ?></div>
        </div>
    </div>

    <div class="table-wrap">
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Nom</th>
                <th>Prénom(s)</th>
                <th>Sexe</th>
                <th>Naissance</th>
                <th>Commune naiss.</th>
                <th>Pays naiss.</th>
                <th>Décès</th>
                <th>Commune décès</th>
                <th>Pays décès</th>
                <th>Acte décès</th>
                <th>Clé</th>
            </tr>
        </thead>
        <tbody>
        <?php foreach ($results as $i => $r): ?>
            <tr>
                <td class="num-cell"><?= ($page - 1) * PER_PAGE + $i + 1 ?></td>
                <td class="nom-cell"><?= h($r['nom']) ?></td>
                <td class="prenoms-cell"><?= h($r['prenoms']) ?></td>
                <td class="sexe-cell">
                    <?php if ($r['sexe'] === null): ?>—
                    <?php elseif ((int)$r['sexe'] === 1): ?><span class="sexe-m" title="Masculin">M</span>
                    <?php else: ?><span class="sexe-f" title="Féminin">F</span>
                    <?php endif; ?>
                </td>
                <td class="date-cell"><?= formatDate($r['annee_naissance'], $r['mois_naissance'], $r['jour_naissance']) ?></td>
                <td class="lieu-cell"><?= h($r['commune_naissance'] . ' (' . substr($r['lieu_naissance'], 0, 2) . ')') ?: '—' ?></td>
                <td class="lieu-cell"><?= h($r['pays_naissance']) ?: '—' ?></td>
                <td class="date-cell"><?= formatDate($r['annee_deces'], $r['mois_deces'], $r['jour_deces']) ?></td>
                <td class="lieu-cell"><?= h($r['commune_deces'] . ' (' . substr($r['lieu_deces'], 0, 2) . ')') ?: '—' ?></td>
                <td class="lieu-cell"><?= h($r['pays_deces']) ?: '—' ?></td>
                <td class="acte-cell" title="<?= h($r['acte_deces']) ?>"><?= h($r['acte_deces']) ?: '—' ?></td>
                <td class="num-cell"><?= h($r['id']) ?></td>
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
</footer>
</body>
</html>
