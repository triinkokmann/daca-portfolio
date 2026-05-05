-- See päring leiab tehingud, kus summa on 0 või negatiivne või puudub kliendi ID:
SELECT sale_id, customer_id, total_price
FROM sales
WHERE total_price <= 0 OR customer_id IS NULL 

-- See päring näitab 10 kõige suuremat tehingut:
SELECT sale_id, total_price AS summa
FROM sales
ORDER BY total_price DESC
LIMIT 10;

-- See päring näitab 20 kõige värskemat tehingut:
SELECT customer_id,  sale_date,  total_price
FROM sales
ORDER BY sale_date DESC
LIMIT 20;

-- See päring näitab 2024. aasta tellimusi, mis on üle 200 euro:
SELECT sale_id, customer_id, total_price
FROM sales
WHERE total_price > 200 AND sale_date BETWEEN '2024-01-01' AND '2024-03-31'

-- See päring on ülevaade products tabelist toodete koguarvu, unikaalsete kategooriate arvu ja puuduvate hindade arvuga:
SELECT
    COUNT(*) AS toodete_arv,
    COUNT(DISTINCT category) AS kategooriaid,
    COUNT(*) - COUNT(cost_price) AS puuduvaid_hindu
FROM products;
