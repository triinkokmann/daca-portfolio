-- KPI: Kogu müügitulu
SELECT ROUND(SUM(total_price), 0) AS myygiulu
FROM public.sales
WHERE sale_date BETWEEN '2023-01-01' AND '2024-12-31';

-- KPI: Unikaalseid kliente
SELECT COUNT(DISTINCT customer_id) AS kliendid
FROM public.sales
WHERE sale_date BETWEEN '2023-01-01' AND '2024-12-31';

-- KPI: Kasv vs 2023
SELECT 
    ROUND((SUM(CASE WHEN EXTRACT(YEAR FROM sale_date) = 2024 THEN total_price END) -
           SUM(CASE WHEN EXTRACT(YEAR FROM sale_date) = 2023 THEN total_price END)) /
           SUM(CASE WHEN EXTRACT(YEAR FROM sale_date) = 2023 THEN total_price END) * 100, 1) AS kasv_pct
FROM public.sales
WHERE EXTRACT(YEAR FROM sale_date) IN (2023, 2024);

-- Müügitrend kuude lõikes
SELECT 
    EXTRACT(YEAR FROM sale_date) AS aasta,
    EXTRACT(MONTH FROM sale_date) AS kuu,
    ROUND(SUM(total_price), 0) AS kaive
FROM public.sales
WHERE sale_date BETWEEN '2023-01-01' AND '2024-12-31'
GROUP BY aasta, kuu
ORDER BY aasta, kuu;