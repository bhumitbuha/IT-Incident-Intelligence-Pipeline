TOP_DEVICES = """
SELECT
    a.asset_type,
    a.model,
    COUNT(t.ticket_id) AS ticket_count,
    ROUND(AVG(t.resolution_hours), 2) AS avg_resolution_hr,
    SUM(t.sla_breached) AS sla_breaches
FROM tickets t
JOIN assets  a ON a.asset_tag = t.asset_tag
GROUP BY a.asset_type, a.model
ORDER BY ticket_count DESC
LIMIT 15;
"""

TOP_DEPARTMENTS = """
SELECT
    d.dept_id,
    d.dept_name,
    d.location,
    COUNT(t.ticket_id) AS ticket_count,
    ROUND(AVG(t.resolution_hours), 2) AS avg_resolution_hr,
    SUM(t.sla_breached) AS sla_breaches
FROM tickets t
JOIN users u        ON u.user_id = t.reporter_user_id
JOIN departments d  ON d.dept_id = u.dept_id
GROUP BY d.dept_id, d.dept_name, d.location
ORDER BY ticket_count DESC;
"""

REPEAT_KEYWORDS_WEEKLY = """
WITH weeks AS (
    SELECT
        STRFTIME('%Y-%W', t.opened_at) AS year_week,
        k.keyword,
        COUNT(*) AS hits
    FROM tickets t
    JOIN ticket_keywords k ON k.ticket_id = t.ticket_id
    GROUP BY year_week, k.keyword
)
SELECT
    keyword,
    COUNT(DISTINCT year_week) AS weeks_seen,
    SUM(hits)                 AS total_hits,
    ROUND(AVG(hits), 2)       AS avg_per_week
FROM weeks
GROUP BY keyword
HAVING weeks_seen >= 4
ORDER BY total_hits DESC
LIMIT 20;
"""

CATEGORY_VOLUME = """
SELECT
    c.category_name,
    COUNT(t.ticket_id) AS ticket_count,
    ROUND(AVG(t.resolution_hours), 2) AS avg_resolution_hr,
    SUM(t.sla_breached) AS sla_breaches
FROM tickets t
JOIN ticket_categories c ON c.category_id = t.category_id
GROUP BY c.category_name
ORDER BY ticket_count DESC;
"""

KB_GAPS = """
WITH ticket_kw AS (
    SELECT keyword, COUNT(*) AS hits
    FROM ticket_keywords
    GROUP BY keyword
)
SELECT
    tk.keyword,
    tk.hits,
    CASE WHEN MAX(kb.kb_id) IS NULL THEN 'No KB' ELSE 'Covered' END AS kb_coverage,
    GROUP_CONCAT(kb.kb_id, ', ') AS matching_kb_ids
FROM ticket_kw tk
LEFT JOIN kb_keywords kb ON kb.keyword = tk.keyword
GROUP BY tk.keyword, tk.hits
ORDER BY tk.hits DESC;
"""

ASSETS_NEAR_EOL = """
SELECT
    a.asset_id,
    a.asset_tag,
    a.model,
    a.asset_type,
    a.age_years,
    a.warranty_end,
    a.compliance_status,
    COUNT(t.ticket_id) AS ticket_count
FROM assets a
LEFT JOIN tickets t ON t.asset_tag = a.asset_tag
GROUP BY a.asset_id
HAVING a.age_years >= 3 OR a.compliance_status = 'Non-compliant'
ORDER BY ticket_count DESC, a.age_years DESC
LIMIT 25;
"""

DAILY_VOLUME = """
SELECT
    DATE(opened_at) AS day,
    COUNT(*) AS ticket_count,
    SUM(sla_breached) AS sla_breaches
FROM tickets
GROUP BY DATE(opened_at)
ORDER BY day;
"""

PRIORITY_BREAKDOWN = """
SELECT
    priority,
    COUNT(*) AS ticket_count,
    ROUND(AVG(resolution_hours), 2) AS avg_resolution_hr,
    SUM(sla_breached) AS sla_breaches
FROM tickets
GROUP BY priority
ORDER BY
    CASE priority
        WHEN 'Critical' THEN 1
        WHEN 'High'     THEN 2
        WHEN 'Medium'   THEN 3
        WHEN 'Low'      THEN 4
    END;
"""

REPEAT_OFFENDERS = """
SELECT
    u.user_id,
    u.full_name,
    d.dept_name,
    COUNT(t.ticket_id) AS ticket_count
FROM tickets t
JOIN users u       ON u.user_id = t.reporter_user_id
JOIN departments d ON d.dept_id = u.dept_id
GROUP BY u.user_id, u.full_name, d.dept_name
HAVING ticket_count >= 8
ORDER BY ticket_count DESC
LIMIT 20;
"""
