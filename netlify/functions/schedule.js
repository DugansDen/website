/**
 * Netlify Function: /.netlify/functions/schedule
 *
 * Returns the show schedule sourced from the CardInventory events table
 * in Turso. Only events with show_on_website=1 and end_date >= today
 * are included. Output shape is identical to the static schedule.json
 * consumed by roster.html / counter.html.
 *
 * To activate: add a netlify.toml redirect from /schedule.json to this
 * function with force=true, then redeploy. Test at /.netlify/functions/schedule
 * first. Confirm Delphox export-shape sign-off before enabling redirect.
 *
 * Required environment variables (already set for inventory.js):
 *   TURSO_URL    e.g. https://your-db-name-yourorg.turso.io
 *   TURSO_TOKEN  your Turso auth token
 *
 * Prerequisites before enabling:
 *   - Nick must open CardInventory v2.4.7.0 at least once so the
 *     events schema migration runs and syncs the expanded columns to Turso.
 *   - Nick must create/edit at least one event with show_on_website=true.
 */

const MONTHS = [
  '', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

// ── Turso HTTP query helper (mirrors inventory.js) ────────────────────────────
async function queryTurso(sql) {
  let url = (process.env.TURSO_URL || '').trim();
  const token = process.env.TURSO_TOKEN;

  if (!url || !token) {
    throw new Error('TURSO_URL and TURSO_TOKEN environment variables are required');
  }

  if (url.startsWith('libsql://')) url = 'https://' + url.slice('libsql://'.length);
  else if (!url.startsWith('https://') && !url.startsWith('http://')) url = 'https://' + url;

  const endpoint = url.replace(/\/$/, '') + '/v2/pipeline';

  const res = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      requests: [
        { type: 'execute', stmt: { sql } },
        { type: 'close' },
      ],
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Turso HTTP ${res.status}: ${text}`);
  }

  const body = await res.json();
  const result = body.results?.[0];
  if (result?.type !== 'ok') {
    throw new Error(`Turso error: ${JSON.stringify(result)}`);
  }

  const cols = result.response.result.cols.map(c => c.name);
  return result.response.result.rows.map(row =>
    Object.fromEntries(cols.map((col, i) => [col, row[i]?.value ?? null]))
  );
}

// ── Date helpers ──────────────────────────────────────────────────────────────
function parseDate(s) {
  if (!s) return null;
  // MM/DD/YYYY (CardInventory app convention)
  const mdy = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(s);
  if (mdy) return new Date(parseInt(mdy[3]), parseInt(mdy[1]) - 1, parseInt(mdy[2]));
  // YYYY-MM-DD (ISO fallback)
  const iso = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s);
  if (iso) return new Date(parseInt(iso[1]), parseInt(iso[2]) - 1, parseInt(iso[3]));
  return null;
}

function buildDateRange(start, end) {
  if (!start || !end) return '';
  if (start.getMonth() === end.getMonth() && start.getFullYear() === end.getFullYear()) {
    return `${start.getDate()}–${end.getDate()}`;
  }
  const sm = MONTHS[start.getMonth() + 1].slice(0, 3).toUpperCase();
  const em = MONTHS[end.getMonth() + 1].slice(0, 3).toUpperCase();
  return `${sm} ${start.getDate()} – ${em} ${end.getDate()}`;
}

// ── Handler ───────────────────────────────────────────────────────────────────
export async function handler(event) {
  if (event.httpMethod !== 'GET') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    // Pull all show_on_website events. Filter end_date >= today in JS
    // because the date is stored as MM/DD/YYYY in the blob, not ISO.
    const rows = await queryTurso(`
      SELECT data
      FROM events
      WHERE show_on_website = 1
        AND data IS NOT NULL
    `);

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const shows = [];
    for (const row of rows) {
      let d = {};
      try { d = JSON.parse(row.data || '{}'); } catch { continue; }

      const startDate = parseDate(d.start_date || d.date);
      const endDate   = parseDate(d.end_date || d.start_date || d.date);

      if (!startDate || !endDate) continue;
      if (endDate < today) continue;

      const monthNum = startDate.getMonth() + 1;
      const month    = MONTHS[monthNum];
      const venue    = (d.address || '').trim();
      const city     = [d.city, d.state].filter(Boolean).join(', ');

      shows.push({
        month,
        monthShort: month.slice(0, 3).toUpperCase(),
        dateRange:  buildDateRange(startDate, endDate),
        startDay:   startDate.getDate(),
        endDay:     endDate.getDate(),
        year:       startDate.getFullYear(),
        monthNum,
        name:       (d.name || '').trim(),
        venue,
        city,
      });
    }

    shows.sort((a, b) => {
      const da = new Date(a.year, a.monthNum - 1, a.startDay);
      const db = new Date(b.year, b.monthNum - 1, b.startDay);
      return da - db;
    });

    const generated = new Date().toLocaleString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: 'numeric', minute: '2-digit', hour12: true,
      timeZone: 'America/Chicago',
    });

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'public, s-maxage=300, max-age=60, stale-while-revalidate=600',
      },
      body: JSON.stringify({ generated, shows }),
    };

  } catch (err) {
    console.error('schedule function error:', err);
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: 'Failed to load schedule' }),
    };
  }
}
