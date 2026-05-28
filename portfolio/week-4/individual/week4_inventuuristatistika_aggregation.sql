-- Ülevaade tootekategooriatest
 SELECT      p.category,      
 COUNT(DISTINCT p.product_id) AS tooteid,      
 ROUND(AVG(p.retail_price), 2) AS keskmine_hind,      MIN(p.retail_price) AS min_hind,      MAX(p.retail_price) AS max_hind    
 FROM products p   
  GROUP BY p.category    
  ORDER BY tooteid DESC;

 -- Müüdud vs laos: kategooriad kus müüdud üle 50 ühiku
SELECT
    p.category AS kategooria,
    SUM(s.quantity) AS müüdud_kogus,
    ROUND(AVG(s.quantity), 2) AS keskmine_müük_toote_kohta
FROM products p
JOIN sales s ON p.product_id = s.product_id
GROUP BY p.category
HAVING SUM(s.quantity) > 1
ORDER BY müüdud_kogus DESC;

-- Todete järjestus kategooria sees
SELECT
    p.product_name,
    p.category,
    p.retail_price,
    ROW_NUMBER() OVER (
        PARTITION BY p.category
        ORDER BY p.retail_price DESC
    ) AS koht_kategoorias
FROM products p;

-- Edasijõudnute: TOP 3 tooted igas kategoorias (window function)
WITH kategooria_myyk AS (
    SELECT
        p.category,
        SUM(s.quantity) AS müüdud_kogus
    FROM products p
    JOIN sales s ON p.product_id = s.product_id
    GROUP BY p.category
    HAVING SUM(s.quantity) > 50
),
toote_jarjestus AS (
    SELECT
        p.product_name,
        p.category,
        SUM(s.quantity) AS toote_müük,
        ROW_NUMBER() OVER (
            PARTITION BY p.category
            ORDER BY SUM(s.quantity) DESC
        ) AS koht
    FROM products p
    JOIN sales s ON p.product_id = s.product_id
    GROUP BY p.category, p.product_name
)
SELECT
    t.category AS kategooria,
    k.müüdud_kogus AS kategooria_kokku,
    t.koht,
    t.product_name AS toode,
    t.toote_müük,
    ROUND(t.toote_müük * 100.0 / k.müüdud_kogus, 1) AS osakaal_protsent
FROM toote_jarjestus t
JOIN kategooria_myyk k ON t.category = k.category
WHERE t.koht <= 3
ORDER BY k.müüdud_kogus DESC, t.category, t.koht;