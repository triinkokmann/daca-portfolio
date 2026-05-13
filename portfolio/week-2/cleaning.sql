-- Loon sales_test tabeili
CREATE TABLE sales_test AS SELECT * FROM sales;

-- Kontrolli ridade arvu
SELECT COUNT(*) AS ridade_arv FROM sales_test;

-- Leian duplikaatsed tellimused
SELECT sale_id, COUNT(*) AS koopiate_arv
FROM sales_test
GROUP BY sale_id
HAVING COUNT(*) > 1
ORDER BY koopiate_arv DESC;

SELECT COUNT(*) AS duplikaatsete_sale_id_arv
FROM (
    SELECT sale_id
    FROM sales_test
    GROUP BY sale_id
    HAVING COUNT(*) > 1
) duplikaadid;

-- Leian duplikaatsete ridade arvu
SELECT COUNT(*) AS duplikaat_read
FROM sales_test
WHERE id NOT IN (
    SELECT MIN(id)
    FROM sales_test
    GROUP BY sale_id
);

-- Leian NULL väärtused kriitilistes väljades
SELECT
    COUNT(*) FILTER (WHERE customer_id IS NULL) AS null_customer_id,
    COUNT(*) FILTER (WHERE sale_date IS NULL) AS null_sale_date,
    COUNT(*) FILTER (WHERE total_price IS NULL) AS null_total_price
FROM sales_test;

-- Leian tulevikukuupäevad
SELECT COUNT(*) AS tuleviku_kuupaevad
FROM sales_test
WHERE sale_date > CURRENT_DATE;

-- Kustuta duplikaadid (jäta alles ainult esimene rida iga sale_id kohta)
DELETE FROM sales_test
WHERE id NOT IN (
    SELECT MIN(id)
    FROM sales_test
    GROUP BY sale_id
);

-- Paranda tuleviku kuupäevad
UPDATE sales_test
SET sale_date = CURRENT_DATE
WHERE sale_date > CURRENT_DATE;

-- Kontrolli külalisostude arvu, kus customer_id on NULL
SELECT COUNT(*) AS külalisostud FROM sales_test WHERE customer_id IS NULL;

-- Määra customer_id NULLidele ajutine väärtus 0
UPDATE sales_test
SET customer_id = COALESCE(customer_id, 0);

-- Loenda read, kus customer_id väärtus on 0
SELECT COUNT(*) AS nullide_arv
FROM sales_test
WHERE customer_id = 0;