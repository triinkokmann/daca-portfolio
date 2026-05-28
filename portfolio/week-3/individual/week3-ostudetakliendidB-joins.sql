 -- LEFT JOIN: kõik kliendid, ka need kellel pole oste    
 SELECT        c.first_name,        c.last_name,        c.email,        c.city,        c.registration_date,        s.sale_id    
 FROM customers c    LEFT JOIN sales s ON c.customer_id = s.customer_id    
 WHERE s.sale_id IS NULL; 

 -- Leian "kadunud" kliendid
 SELECT COUNT(*) AS kadunud_kliente    
 FROM customers c    LEFT JOIN sales s ON c.customer_id = s.customer_id    
 WHERE s.sale_id IS NULL; 

 -- Kadunud kliendid linnade kaupa
 SELECT        c.city,        COUNT(*) AS kadunud_kliente    
 FROM customers c    LEFT JOIN sales s ON c.customer_id = s.customer_id    
 WHERE s.sale_id IS NULL    
 GROUP BY c.city    
 ORDER BY kadunud_kliente DESC;

-- Kliente linnades kokku
SELECT 
    city AS linn,
    COUNT(*) AS kliente_kokku
FROM customers
GROUP BY city
ORDER BY kliente_kokku DESC;

-- Millal kadunud kliendid registreerusid?    
SELECT        c.first_name || ' ' || c.last_name AS klient,        c.registration_date,        c.city,        c.loyalty_tier    
FROM customers c    LEFT JOIN sales s ON c.customer_id = s.customer_id    
WHERE s.sale_id IS NULL    
ORDER BY c.registration_date DESC;  

-- Kadunud vs aktiivsete klientide arv
 SELECT        CASE            WHEN s.sale_id IS NULL THEN 'Kadunud (pole ostnud)'            ELSE 'Aktiivne (on ostnud)'        END AS staatus,        
 COUNT(DISTINCT c.customer_id) AS kliente    
 FROM customers c    LEFT JOIN sales s ON c.customer_id = s.customer_id    
 GROUP BY        CASE            WHEN s.sale_id IS NULL THEN 'Kadunud (pole ostnud)'            ELSE 'Aktiivne (on ostnud)'        END;   

-- Grupeeri kadunud kliendid registreerimiskuu kaupa ja otsi mustreid
 SELECT       DATE_TRUNC('month', c.registration_date) AS registreerimis_kuu,       
 COUNT(*) AS kadunud_kliente   
 FROM customers c   LEFT JOIN sales s ON c.customer_id = s.customer_id   
 WHERE s.sale_id IS NULL   
 GROUP BY DATE_TRUNC('month', c.registration_date)   
 ORDER BY registreerimis_kuu; 

-- Loendan järelmaksuga sooritatud ostud
SELECT COUNT(*) AS jarelmaksu_ostud
FROM sales
WHERE payment_method = 'järelmaks';
 
 -- Loendan kõik ostud makseviisi järgi
 SELECT 
    payment_method,
    COUNT(*) AS ostude_arv,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS osakaal_pct
FROM sales
GROUP BY payment_method
ORDER BY ostude_arv DESC;
